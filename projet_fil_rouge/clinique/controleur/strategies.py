"""strategies.py — Stratégies de navigation (pattern Strategy)."""
import math


# ── Interface ─────────────────────────────────────────────────────────

class Strategy:
    """Interface commune pour toutes les stratégies de navigation."""

    def compute_command(self, observation, *args):
        raise NotImplementedError


# ── Évitement pur (robots standards) ──────────────────────────────────

class AvoidStrategy(Strategy):
    """Évitement fluide basé sur la répartition du danger gauche/droite."""

    def __init__(self, distance_securite=60.0):
        self.distance_securite = distance_securite

    def compute_command(self, observation, *args):
        if not observation:
            return 1.0, 0.0

        dist_min = min(observation)

        # Voie libre → tout droit
        if dist_min >= self.distance_securite:
            return 1.0, 0.0

        # Calcul du danger de chaque côté
        mid = len(observation) // 2
        ds = self.distance_securite
        danger_gauche = sum(ds - d for d in observation[:mid] if d < ds)
        danger_droite = sum(ds - d for d in observation[mid+1:] if d < ds)
        danger_centre = (ds - observation[mid]
                         if observation[mid] < ds else 0)

        # Répartition du danger central vers le côté le plus encombré
        if danger_droite >= danger_gauche:
            danger_droite += danger_centre
        else:
            danger_gauche += danger_centre

        # Vitesse réduite proportionnellement à la proximité (min 80 %)
        v = max(0.8, dist_min / ds)

        # Rotation proportionnelle au déséquilibre de danger
        omega = (danger_gauche - danger_droite) * 0.15
        omega = max(-2.5, min(2.5, omega))

        return v, omega

    def compute_escape(self, observation):
        """Manœuvre d'échappatoire quand le robot est bloqué."""
        if observation:
            max_idx = observation.index(max(observation))
            mid = len(observation) // 2
            if max_idx < mid:
                return 0.5, 2.5
            elif max_idx > mid:
                return 0.5, -2.5
            else:
                return -0.3, 2.5
        return 0.5, 2.5


# ── Navigation vers cible + évitement (ambulance) ────────────────────

class GoalAndAvoidStrategy(Strategy):
    """Combine navigation vers une cible et évitement d'obstacles."""

    def __init__(self, distance_securite=80.0):
        self.distance_securite = distance_securite
        self.cible_x = self.cible_y = None

    def set_cible(self, x, y):
        self.cible_x, self.cible_y = x, y

    def compute_command(self, observation, robot_x, robot_y, robot_theta):
        dist_min = (min(observation) if observation
                    else self.distance_securite)
        ds = self.distance_securite

        # 1. Esquive prioritaire si obstacle proche
        if dist_min < ds:
            mid = len(observation) // 2
            danger_gauche = sum(ds - d for d in observation[:mid]
                                if d < ds)
            danger_droite = sum(ds - d for d in observation[mid+1:]
                                if d < ds)
            danger_centre = (ds - observation[mid]
                             if observation[mid] < ds else 0)

            if danger_droite >= danger_gauche:
                danger_droite += danger_centre
            else:
                danger_gauche += danger_centre

            v = max(0.8, dist_min / ds)
            omega = (danger_gauche - danger_droite) * 0.15
            omega = max(-2.5, min(2.5, omega))
            return v, omega

        # 2. Navigation vers la cible
        if self.cible_x is not None:
            erreur_angle = (
                math.atan2(self.cible_y - robot_y,
                           self.cible_x - robot_x)
                - robot_theta + math.pi
            ) % (2 * math.pi) - math.pi
            v = 1.0
            omega = max(-1.0, min(1.0, erreur_angle * 1.5))
            return v, omega

        return 0.0, 0.0


# ── Contexte Strategy (pattern) ───────────────────────────────────────

class Navigator:
    """Encapsule une stratégie interchangeable."""

    def __init__(self, strategy):
        self.strategy = strategy

    def set_strategy(self, s):
        self.strategy = s

    def step(self, obs, *args):
        return self.strategy.compute_command(obs, *args)
