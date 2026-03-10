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
        self.moteur = MoteurDifferentielRealiste()

    def appliquer_commande(self, v_cmd, omega_cmd, dt):
        if self.en_panne:
            v_cmd, omega_cmd = 0.0, 0.0
        dv, domega = self.moteur.mettre_a_jour(v_cmd, omega_cmd, dt)
        self.theta += domega
        self.x += dv * math.cos(self.theta)
        self.y += dv * math.sin(self.theta)

class RobotStandard(RobotMobile):
    def __init__(self, id_robot, x, y, poids):
        super().__init__(id_robot, x, y, poids)
        self.probabilite_panne = 0.0002 # Panne très rare (baisse drastique)
        # Moteur x5 pour le standard
        self.moteur.v_max = 15.0
        self.moteur.a_max = 8.0
        # Moustaches un peu plus courtes que l'ambulance
        self.capteur = LidarMoustaches(self, [-math.pi/6, 0, math.pi/6], portee_max=70)

    def mettre_a_jour_etat(self):
        if not self.en_panne and random.random() < self.probabilite_panne:
            self.en_panne = True

class RobotAmbulance(RobotMobile):
    def __init__(self, id_robot, x, y, capacite_max=50):
        super().__init__(id_robot, x, y, poids=0)
        self.capacite_max = capacite_max
        self.charge_actuelle = 0
        self.capteur = LidarMoustaches(self, [-math.pi/6, 0, math.pi/6], portee_max=120)