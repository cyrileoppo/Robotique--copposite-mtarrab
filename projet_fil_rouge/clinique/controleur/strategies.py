"""strategies.py — Stratégies de navigation fluides (Lidar 180°, N rayons)."""
import math

class Strategy:
    def compute_command(self, observation, *args):
        raise NotImplementedError


class AvoidStrategy(Strategy):
    """Évitement fluide : Plus l'obstacle est proche, plus l'angle de braquage augmente."""

    def __init__(self, distance_securite=60.0):
        self.distance_securite = distance_securite

    def compute_command(self, observation, *args):
        if not observation:
            return 1.0, 0.0

        dist_min = min(observation)
        
        # Voie libre totale ou limite du capteur
        if dist_min >= self.distance_securite:
            return 1.0, 0.0

        # --- Calcul Fluide ---
        mid = len(observation) // 2
        
        # On calcule le niveau de "danger" (proximité) à gauche et à droite
        danger_gauche = sum([self.distance_securite - d for d in observation[:mid] if d < self.distance_securite])
        danger_droite = sum([self.distance_securite - d for d in observation[mid+1:] if d < self.distance_securite])
        danger_centre = self.distance_securite - observation[mid] if observation[mid] < self.distance_securite else 0

        # Répartition du danger central du côté le plus encombré pour faciliter le choix
        if danger_droite >= danger_gauche:
            danger_droite += danger_centre
        else:
            danger_gauche += danger_centre

        # Ralentissement fluide : on maintient la vitesse à 80% minimum pour garder de l'élan
        v = max(0.8, dist_min / self.distance_securite) 
        
        # Rotation fluide : on augmente la réactivité (0.15) pour compenser la vitesse élevée
        diff_danger = danger_gauche - danger_droite
        omega = diff_danger * 0.15
        
        # Bornage élargi pour autoriser un braquage plus sec
        omega = max(-2.5, min(2.5, omega))

        return v, omega


class GoalAndAvoidStrategy(Strategy):
    """Navigation fluide vers cible + évitement."""

    def __init__(self, distance_securite=80.0):
        self.distance_securite = distance_securite
        self.cible_x = self.cible_y = None

    def set_cible(self, x, y):
        self.cible_x, self.cible_y = x, y

    def compute_command(self, observation, robot_x, robot_y, robot_theta):
        dist_min = min(observation) if observation else self.distance_securite
        
        # 1. ESQUIVE (Prioritaire)
        if dist_min < self.distance_securite:
            mid = len(observation) // 2
            danger_gauche = sum([self.distance_securite - d for d in observation[:mid] if d < self.distance_securite])
            danger_droite = sum([self.distance_securite - d for d in observation[mid+1:] if d < self.distance_securite])
            danger_centre = self.distance_securite - observation[mid] if observation[mid] < self.distance_securite else 0

            if danger_droite >= danger_gauche:
                danger_droite += danger_centre
            else:
                danger_gauche += danger_centre

            # Vitesse maintenue haute et rotation très nerveuse
            v = max(0.8, dist_min / self.distance_securite) 
            omega = (danger_gauche - danger_droite) * 0.15
            omega = max(-2.5, min(2.5, omega))
            return v, omega

        # 2. NAVIGATION VERS CIBLE (Si pas d'obstacle)
        if self.cible_x is not None:
            erreur_angle = (math.atan2(self.cible_y - robot_y, self.cible_x - robot_x) - robot_theta + math.pi) % (2 * math.pi) - math.pi
            v = 1.0
            omega = max(-1.0, min(1.0, erreur_angle * 1.5))
            return v, omega

        return 0.0, 0.0


class Navigator:
    """Contexte Strategy."""
    def __init__(self, strategy): 
        self.strategy = strategy
        
    def set_strategy(self, s): 
        self.strategy = s
        
    def step(self, obs, *args): 
        return self.strategy.compute_command(obs, *args)