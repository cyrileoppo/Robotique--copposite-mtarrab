from abc import ABC, abstractmethod
import math

class Obstacle(ABC):
    """Classe abstraite imposant une interface commune à tous les obstacles."""
    
    @abstractmethod
    def collision(self, robot_x, robot_y, robot_rayon):
        """Méthode de collision imposée."""
        pass

class ObstacleCirculaire(Obstacle):
    """Obstacle simple défini par un centre et un rayon."""
    
    def __init__(self, x, y, rayon):
        self.x = x
        self.y = y
        self.rayon = rayon

    def collision(self, robot_x, robot_y, robot_rayon):
        """Retourne True s'il y a un contact physique avec le robot."""
        distance = math.hypot(self.x - robot_x, self.y - robot_y)
        return distance <= (self.rayon + robot_rayon)