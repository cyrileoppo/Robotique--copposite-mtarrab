import math
from robot.moteur import Moteur


class RobotMobile:
    _nb_robots = 0

    def __init__(self, x=0.0, y=0.0, orientation=0.0, moteur: Moteur = None):
        self.__x = x
        self.__y = y
        self.__orientation = orientation
        self.__moteur = moteur

    # ==========================
    # Encapsulation : Getters / Setters
    # ==========================

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, value):
        self.__x = float(value)

    @property
    def y(self):
        return self.__y

    @property
    def y(self): return self.__y
    @y.setter
    def y(self, value):
        self.__y = float(value)

    @property
    def orientation(self):
        return self.__orientation

    @orientation.setter
    def orientation(self, value):
        self.__orientation = value % (2 * math.pi)

    @property
    def moteur(self):
        return self.__moteur

    @moteur.setter
    def moteur(self, value):
        self.__moteur = value

    # ==========================
    # Polymorphisme / Délégation
    # ==========================

    def commander(self, **kwargs):
        if self.__moteur is not None:
            self.__moteur.commander(**kwargs)

    def mettre_a_jour(self, dt):
        if self.__moteur is not None:
            self.__moteur.mettre_a_jour(self, dt)

    # ==========================

    def afficher(self):
        print(f"(x={self.__x:.2f}, y={self.__y:.2f}, orientation={self.__orientation:.2f})")