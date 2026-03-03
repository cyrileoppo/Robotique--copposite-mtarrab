from abc import ABC, abstractmethod
import math

class Moteur(ABC):
    """Classe abstraite représentant l'actionneur d'un robot."""
    
    @abstractmethod
    def commander(self, *args, **kwargs):
        """Reçoit une commande de vitesse."""
        pass

    @abstractmethod
    def mettre_a_jour(self, robot, dt):
        """Applique la mise à jour cinématique."""
        pass


class MoteurDifferentiel(Moteur):
    """Implémente un déplacement basé sur une vitesse linéaire et angulaire."""
    
    def __init__(self, v=0.0, omega=0.0):
        self.v = v 
        self.omega = omega

    def commander(self, v=0.0, omega=0.0, **kwargs):
        self.v = v
        self.omega = omega

    def mettre_a_jour(self, robot, dt):
        """
        Met à jour la position du robot avec la cinématique du robot différentiel.
        """
        robot.orientation = (robot.orientation + self.omega * dt) % (2 * math.pi)
        
        robot.x = robot.x + self.v * math.cos(robot.orientation) * dt
        robot.y = robot.y + self.v * math.sin(robot.orientation) * dt