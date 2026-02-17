from abc import ABC, abstractmethod
from math import cos, sin


# =====================================
# Classe abstraite
# =====================================

class Moteur(ABC):

    @abstractmethod
    def commander(self, **kwargs):
        pass

    @abstractmethod
    def mettre_a_jour(self, robot, dt):
        pass


# =====================================
# Moteur Différentiel
# =====================================

class MoteurDifferentiel(Moteur):

    def __init__(self, v=0.0, omega=0.0):
        self.v = v
        self.omega = omega

    def commander(self, v, omega):
        self.v = v
        self.omega = omega

    def mettre_a_jour(self, robot, dt):
        robot.orientation += self.omega * dt
        robot.x += self.v * cos(robot.orientation) * dt
        robot.y += self.v * sin(robot.orientation) * dt


# =====================================
# Moteur Omnidirectionnel
# =====================================

class MoteurOmnidirectionnel(Moteur):

    def __init__(self, vx=0.0, vy=0.0, omega=0.0):
        self.vx = vx
        self.vy = vy
        self.omega = omega

    def commander(self, vx, vy, omega):
        self.vx = vx
        self.vy = vy
        self.omega = omega

    def mettre_a_jour(self, robot, dt):
        robot.orientation += self.omega * dt

        robot.x += (self.vx * cos(robot.orientation)
                    - self.vy * sin(robot.orientation)) * dt

        robot.y += (self.vx * sin(robot.orientation)
                    + self.vy * cos(robot.orientation)) * dt
