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
        # Délègue le calcul à la stratégie active [cite: 746-747]
        return self.strategy.compute_command(observation)