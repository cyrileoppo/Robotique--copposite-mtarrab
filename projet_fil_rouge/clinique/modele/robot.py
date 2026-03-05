import math
from .moteur import MoteurDifferentielRealiste

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
        # On pourrait ajouter un timer "silence radio" ici plus tard

class RobotAmbulance(RobotMobile):
    def __init__(self, id_robot, x, y, capacite_max=50):
        super().__init__(id_robot, x, y, poids=0)
        self.capacite_max = capacite_max
        self.charge_actuelle = 0