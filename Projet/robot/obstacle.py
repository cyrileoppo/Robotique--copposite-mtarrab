from abc import ABC, abstractmethod
import math


class Obstacle(ABC):
    @abstractmethod
    def collision(self, robot_x, robot_y, robot_rayon):
        pass


class ObstacleCirculaire(Obstacle):
    def __init__(self, x, y, rayon):
        self.x = x
        self.y = y
        self.rayon = rayon

    def collision(self, robot_x, robot_y, robot_rayon):
        distance = math.hypot(self.x - robot_x, self.y - robot_y)
        return distance <= (self.rayon + robot_rayon)