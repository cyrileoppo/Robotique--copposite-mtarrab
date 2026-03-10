import math

class Strategy:
    """Interface commune pour tous les comportements ."""
    def compute_command(self, observation):
        raise NotImplementedError

class AvoidStrategy(Strategy):
    """Stratégie d'évitement directionnel ."""
    def __init__(self, distance_securite=40.0):
        self.distance_securite = distance_securite

    def compute_command(self, observation):
        # L'observation est la liste des distances lues par les moustaches : [gauche, centre, droite]
        dist_gauche, dist_centre, dist_droite = observation
        
        v_cmd = 1.0     # Vitesse par défaut (avancer)
        omega_cmd = 0.0 # Rotation par défaut (tout droit)
        
        # S'il y a un obstacle trop proche devant ou sur les côtés [cite: 763-768]
        if dist_centre < self.distance_securite or dist_gauche < self.distance_securite or dist_droite < self.distance_securite:
            v_cmd = 0.2 # On ralentit fortement
            
            # On tourne du côté où l'espace est le plus libre [cite: 772-773]
            if dist_gauche < dist_droite:
                omega_cmd = 1.5  # Tourner à droite
            else:
                omega_cmd = -1.5 # Tourner à gauche
                
        return v_cmd, omega_cmd

class Navigator:
    """Le contexte qui utilise une stratégie sans la connaître [cite: 738-747]."""
    def __init__(self, strategy):
        self.strategy = strategy

    def set_strategy(self, strategy):
        self.strategy = strategy

    def step(self, observation):
        return self.strategy.compute_command(observation)
    
class GoalAndAvoidStrategy(Strategy):
    """Combine l'attraction vers une cible et la répulsion des obstacles [cite: 780-782]."""
    def __init__(self, distance_securite=50.0):
        self.distance_securite = distance_securite
        self.cible_x = None
        self.cible_y = None

    def set_cible(self, x, y):
        self.cible_x = x
        self.cible_y = y

    def compute_command(self, observation, robot_x, robot_y, robot_theta):
        if observation:
            dist_gauche, dist_centre, dist_droite = observation
            if dist_centre < self.distance_securite or dist_gauche < self.distance_securite or dist_droite < self.distance_securite:
                vitesse_esquive = 3.0
                rotation_esquive = 2.5
                
                if dist_gauche < dist_droite:
                    return vitesse_esquive, rotation_esquive  # Tourner droite
                else:
                    return vitesse_esquive, -rotation_esquive # Tourner gauche

        if self.cible_x is not None and self.cible_y is not None:
            angle_cible = math.atan2(self.cible_y - robot_y, self.cible_x - robot_x)
            erreur_angle = angle_cible - robot_theta
            erreur_angle = (erreur_angle + math.pi) % (2 * math.pi) - math.pi
            
            v_cmd = 1.0 
            omega_cmd = max(-1.5, min(1.5, erreur_angle * 2.5)) 
            
            return v_cmd, omega_cmd

        return 0.0, 0.0