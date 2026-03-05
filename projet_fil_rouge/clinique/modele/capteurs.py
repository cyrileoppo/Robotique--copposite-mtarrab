import math

class CapteurDistance:
    """Interface commune pour les capteurs [cite: 374-376]."""
    def read(self, env):
        raise NotImplementedError

class LidarMoustaches(CapteurDistance):
    def __init__(self, robot, angles, portee_max=100):
        self.robot = robot
        self.angles = angles # Liste d'angles relatifs au robot (ex: [-0.5, 0, 0.5])
        self.portee_max = portee_max
        self.dernieres_mesures = [] # Pour l'affichage graphique

    def read(self, env):
        """Lit les distances pour chaque rayon [cite: 163, 177-186]."""
        self.dernieres_mesures = []
        
        for angle_relatif in self.angles:
            # Calcul de la direction du rayon [cite: 172-173]
            angle_absolu = self.robot.theta + angle_relatif
            dx = math.cos(angle_absolu)
            dy = math.sin(angle_absolu)
            
            dist_min = self.portee_max
            
            # Test d'intersection avec tous les obstacles [cite: 182-186]
            for obs in env.obstacles:
                dist = obs.intersection(self.robot.x, self.robot.y, dx, dy, self.portee_max)
                if dist is not None and dist < dist_min:
                    dist_min = dist
                    
            self.dernieres_mesures.append((angle_absolu, dist_min))
            
        return [mesure[1] for mesure in self.dernieres_mesures]