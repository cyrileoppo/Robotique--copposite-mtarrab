import math
from .obstacles import ObstacleCercle

class CapteurDistance:
    def read(self, env):
        raise NotImplementedError

class LidarMoustaches(CapteurDistance):
    def __init__(self, robot, angles, portee_max=100):
        self.robot = robot
        self.angles = angles
        self.portee_max = portee_max
        self.dernieres_mesures = []

    def read(self, env):
        self.dernieres_mesures = []
        
        for angle_relatif in self.angles:
            angle_absolu = self.robot.theta + angle_relatif
            dx = math.cos(angle_absolu)
            dy = math.sin(angle_absolu)
            
            dist_min = self.portee_max
            
            # 1. Détection des obstacles fixes
            for obs in env.obstacles:
                dist = obs.intersection(self.robot.x, self.robot.y, dx, dy, self.portee_max)
                if dist is not None and dist < dist_min:
                    dist_min = dist
                    
            # 2. Détection des obstacles dynamiques (les autres robots actifs)
            for autre_robot in env.robots:
                # On ignore soi-même et les robots en panne (pour pouvoir les secourir)
                if autre_robot != self.robot and not getattr(autre_robot, 'en_panne', False):
                    # On modélise temporairement le robot comme un ObstacleCercle de rayon 25
                    obs_robot = ObstacleCercle(autre_robot.x, autre_robot.y, 25)
                    dist = obs_robot.intersection(self.robot.x, self.robot.y, dx, dy, self.portee_max)
                    if dist is not None and dist < dist_min:
                        dist_min = dist
                        
            self.dernieres_mesures.append((angle_absolu, dist_min))
            
        return [mesure[1] for mesure in self.dernieres_mesures]