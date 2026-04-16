"""capteurs.py — Capteurs de distance (Lidar à moustaches)."""
import math
from .obstacles import ObstacleCercle
from .. import config


# ── Interface capteur ─────────────────────────────────────────────────

class CapteurDistance:
    """Interface commune pour tous les capteurs de distance."""

    def read(self, env):
        raise NotImplementedError


# ── Lidar à moustaches ────────────────────────────────────────────────

class LidarMoustaches(CapteurDistance):
    """Envoie N rayons en cône frontal et retourne la distance au plus proche obstacle."""

    def __init__(self, robot, angles, portee_max=100):
        self.robot = robot
        self.angles = angles
        self.portee_max = portee_max
        self.dernieres_mesures = []

    def _est_dans_la_base(self, robot):
        return (math.hypot(robot.x - config.BASE_X,
                           robot.y - config.BASE_Y)
                < config.RAYON_SORTIE_BASE)

    def read(self, env):
        """Retourne la liste des distances mesurées pour chaque rayon."""
        self.dernieres_mesures = []

        # Capteur désactivé tant que le robot est dans la base
        if self._est_dans_la_base(self.robot):
            self.dernieres_mesures = [
                (self.robot.theta + angle_relatif, self.portee_max)
                for angle_relatif in self.angles
            ]
            return [self.portee_max for _ in self.angles]

        tous_obs = (env.tous_obstacles
                    if hasattr(env, "tous_obstacles")
                    else env.obstacles)

        for angle_relatif in self.angles:
            angle_absolu = self.robot.theta + angle_relatif
            dx = math.cos(angle_absolu)
            dy = math.sin(angle_absolu)
            dist_min = self.portee_max

            # 1. Obstacles fixes + bordures invisibles
            for obs in tous_obs:
                dist = obs.intersection(self.robot.x, self.robot.y,
                                        dx, dy, self.portee_max)
                if dist is not None and dist < dist_min:
                    dist_min = dist

            # 2. Autres robots hors base (l'ambulance a un rayon de détection plus grand)
            for autre_robot in env.robots:
                if autre_robot == self.robot:
                    continue
                if getattr(autre_robot, "en_panne", False):
                    continue
                if self._est_dans_la_base(autre_robot):
                    continue

                est_ambulance = (getattr(autre_robot, "type_robot", "")
                                 == "ambulance")
                rayon_detection = 40 if est_ambulance else 30

                obs_robot = ObstacleCercle(
                    autre_robot.x, autre_robot.y, rayon_detection)
                dist = obs_robot.intersection(
                    self.robot.x, self.robot.y, dx, dy, self.portee_max
                )
                if dist is not None and dist < dist_min:
                    dist_min = dist

            self.dernieres_mesures.append((angle_absolu, dist_min))

        return [mesure[1] for mesure in self.dernieres_mesures]