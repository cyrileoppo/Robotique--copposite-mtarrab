from abc import ABC, abstractmethod
import math


class Moteur(ABC):
    @abstractmethod
    def commander(self, *args, **kwargs):
        pass

    @abstractmethod
    def mettre_a_jour(self, robot, dt):
        pass


class MoteurDifferentiel(Moteur):
    def __init__(self, v=0.0, omega=0.0):
        self.v = v
        self.omega = omega

    def commander(self, v=0.0, omega=0.0, **kwargs):
        self.v = v
        self.omega = omega

    def mettre_a_jour(self, robot, dt):
        robot.orientation = (robot.orientation + self.omega * dt) % (2 * math.pi)
        robot.x = robot.x + self.v * math.cos(robot.orientation) * dt
        robot.y = robot.y + self.v * math.sin(robot.orientation) * dt