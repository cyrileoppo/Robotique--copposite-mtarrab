import math
import random
from .moteur import MoteurDifferentielRealiste
from .capteurs import LidarMoustaches

class RobotMobile:
    def __init__(self, id_robot, x, y, poids=0):
        self.id = id_robot
        self.x = x
        self.y = y
        self.theta = 0.0
        self.poids = poids
        self.en_panne = False
        
        # Composition : le robot possède un moteur 
        self.moteur = MoteurDifferentielRealiste()

    def appliquer_commande(self, v_cmd, omega_cmd, dt):
        if self.en_panne:
            v_cmd, omega_cmd = 0.0, 0.0 # Un robot en panne ne bouge plus
            
        # Le moteur gère les calculs physiques
        dv, domega = self.moteur.mettre_a_jour(v_cmd, omega_cmd, dt)
        
        # Cinématique finale
        self.theta += domega
        self.x += dv * math.cos(self.theta)
        self.y += dv * math.sin(self.theta)

class RobotStandard(RobotMobile):
    def __init__(self, id_robot, x, y, poids):
        super().__init__(id_robot, x, y, poids)
        self.probabilite_panne = 0.005
    def mettre_a_jour_etat(self):
        """Simule l'usure du robot."""
        if not self.en_panne and random.random() < self.probabilite_panne:
            self.en_panne = True

class RobotAmbulance(RobotMobile):
    def __init__(self, id_robot, x, y, capacite_max=50):
        super().__init__(id_robot, x, y, poids=0)
        self.capacite_max = capacite_max
        self.charge_actuelle = 0
        self.capteur = LidarMoustaches(self, [-math.pi/6, 0, math.pi/6], portee_max=80)