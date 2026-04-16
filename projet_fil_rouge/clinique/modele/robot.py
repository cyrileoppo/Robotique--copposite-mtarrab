"""robot.py — Modèles des robots mobiles (standard et ambulance)."""
import math
import random
from .moteur import MoteurDifferentielRealiste
from .capteurs import LidarMoustaches
from .. import config


# ── Utilitaire ────────────────────────────────────────────────────────

def _angles_cone(nb_rayons, angle_total_deg=90):
    """Génère nb_rayons angles répartis sur un cône frontal."""
    if nb_rayons <= 1:
        return [0.0]
    angle_rad = math.radians(angle_total_deg)
    return [angle_rad * i / (nb_rayons - 1) - angle_rad / 2 for i in range(nb_rayons)]


# ── Classe de base ────────────────────────────────────────────────────

class RobotMobile:
    """Classe de base pour tous les robots mobiles."""

    def __init__(self, id_robot, x, y, poids=0):
        self.id = id_robot
        self.x = x
        self.y = y
        self.theta = 0.0
        self.poids = poids
        self.en_panne = False
        self.moteur = MoteurDifferentielRealiste()
        self.type_robot = "standard"
        self._historique_pos = []
        self._bloque = False

    def verifier_blocage(self, seuil=3.0, taille=50):
        """Détecte si le robot est bloqué (n'a pas bougé significativement)."""
        self._historique_pos.append((self.x, self.y))
        if len(self._historique_pos) > taille:
            self._historique_pos.pop(0)
        if len(self._historique_pos) >= taille:
            x0, y0 = self._historique_pos[0]
            self._bloque = math.hypot(self.x - x0, self.y - y0) < seuil
        else:
            self._bloque = False
        return self._bloque

    def appliquer_commande(self, v_cmd, omega_cmd, dt):
        """Applique la commande moteur et met à jour la position."""
        if self.en_panne:
            v_cmd, omega_cmd = 0.0, 0.0
        dv, domega = self.moteur.mettre_a_jour(v_cmd, omega_cmd, dt)
        self.theta = (self.theta + domega + math.pi) % (2 * math.pi) - math.pi
        self.x += dv * math.cos(self.theta)
        self.y += dv * math.sin(self.theta)


# ── Robot standard ────────────────────────────────────────────────────

class RobotStandard(RobotMobile):
    """Robot standard : se promène, peut tomber en panne, peut être réparé."""

    def __init__(self, id_robot, x, y, poids):
        super().__init__(id_robot, x, y, poids)
        self.theta = random.uniform(-math.pi, math.pi)
        self.moteur.v_max = config.STANDARD_V_MAX
        self.moteur.a_max = config.STANDARD_A_MAX
        self.capteur = LidarMoustaches(
            self,
            _angles_cone(config.STANDARD_NB_RAYONS, angle_total_deg=90),
            portee_max=config.STANDARD_LIDAR_PORTEE
        )
        self.en_sortie_base = False
        self.dist_sortie_parcourue = 0.0
        self.temps_reparation_restant = 0.0

    def mettre_a_jour_etat(self):
        """Tire une panne aléatoire à chaque frame."""
        if not self.en_panne and not self.en_sortie_base:
            if random.random() < config.STANDARD_PROBA_PANNE:
                self.en_panne = True


# ── Robot ambulance ───────────────────────────────────────────────────

class RobotAmbulance(RobotMobile):
    """Ambulance : récupère les robots en panne et les ramène à la base."""

    def __init__(self, id_robot, x, y):
        super().__init__(id_robot, x, y, poids=config.AMBULANCE_POIDS_PROPRE)
        self.type_robot = "ambulance"
        self.capacite_max = config.AMBULANCE_CAPACITE_MAX
        self.robots_charges = []
        self.plan_sauvetage = []
        self.capteur = LidarMoustaches(
            self,
            _angles_cone(config.AMBULANCE_NB_RAYONS, angle_total_deg=90),
            portee_max=config.AMBULANCE_LIDAR_PORTEE
        )

    @property
    def poids_charge(self):
        return sum(r.poids for r in self.robots_charges)

    @property
    def poids_total(self):
        return self.poids + self.poids_charge