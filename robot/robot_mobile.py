import math
from .moteur import Moteur

class RobotMobile:
    # Attribut statique
    _nb_robots = 0

    def __init__(self, x=0.0, y=0.0, orientation=0.0, moteur=None):
        # Attributs privés (Encapsulation)
        self.__x = x
        self.__y = y
        self.__orientation = orientation
        self.moteur = moteur
        
        # Incrémentation du compteur de classe
        RobotMobile._nb_robots += 1

    # --- Getters et Setters (Encapsulation) ---
    @property
    def x(self) -> float:
        return self.__x
    
    @x.setter
    def x(self, value: float):
        self.__x = value

    @property
    def y(self) -> float:
        return self.__y
    
    @y.setter
    def y(self, value: float):
        self.__y = value

    @property
    def orientation(self) -> float:
        return self.__orientation
    
    @orientation.setter
    def orientation(self, value: float):
        self.__orientation = value

    # --- Méthodes de mouvement simple ---
    def avancer(self, distance: float):
        self.__x += distance * math.cos(self.__orientation)
        self.__y += distance * math.sin(self.__orientation)

    def tourner(self, angle: float):
        self.__orientation = (self.__orientation + angle) % (2 * math.pi)

    # --- Méthodes liées au moteur (Polymorphisme) ---
    def commander(self, **kwargs):
        if self.moteur is not None:
            self.moteur.commander(**kwargs)

    def mettre_a_jour(self, dt: float):
        if self.moteur is not None:
            self.moteur.mettre_a_jour(self, dt)

    # --- Méthodes Statiques et de Classe ---
    @classmethod
    def nombre_robots(cls) -> int:
        return cls._nb_robots

    @staticmethod
    def moteur_valide(moteur):
        return isinstance(moteur, Moteur)

    # --- Méthodes Spéciales ---
    def __str__(self):
        return f"RobotMobile(x={self.x:.2f}, y={self.y:.2f}, orient={self.orientation:.2f} rad)"

    def afficher(self):
        # On utilise maintenant la méthode __str__ pour l'affichage
        print(self.__str__())