import math
from .obstacles import ObstacleCercle
from .. import config


class CapteurDistance:
    """Interface commune pour tous les capteurs de distance."""

    def read(self, env):
        raise NotImplementedError


class LidarMoustaches(CapteurDistance):
    """
    Capteur Lidar à moustaches : envoie N rayons dans des directions relatives
    à l'orientation du robot et retourne la distance au premier obstacle détecté.
    Prend en compte les obstacles fixes, les bordures invisibles ET les autres robots,
    sauf quand le robot est encore dans la base.
    """

    def __init__(self, robot, angles, portee_max=100):
        self.robot = robot
        self.angles = angles
        self.portee_max = portee_max
        self.dernieres_mesures = []

    def _est_dans_la_base(self, robot):
        return math.hypot(robot.x - config.BASE_X, robot.y - config.BASE_Y) < config.RAYON_SORTIE_BASE

    def read(self, env):
        self.dernieres_mesures = []

        # Si le robot est encore dans la base, son capteur est "éteint"
        if self._est_dans_la_base(self.robot):
            self.dernieres_mesures = [
                (self.robot.theta + angle_relatif, self.portee_max)
                for angle_relatif in self.angles
            ]
            return [self.portee_max for _ in self.angles]

        # Tous les obstacles : fixes + bordures invisibles
        tous_obs = env.tous_obstacles if hasattr(env, "tous_obstacles") else env.obstacles

        for angle_relatif in self.angles:
            angle_absolu = self.robot.theta + angle_relatif
            dx = math.cos(angle_absolu)
            dy = math.sin(angle_absolu)

            dist_min = self.portee_max

            # 1. Détection des obstacles fixes + bordures
            for obs in tous_obs:
                dist = obs.intersection(self.robot.x, self.robot.y, dx, dy, self.portee_max)
                if dist is not None and dist < dist_min:
                    dist_min = dist

            # 2. Détection des autres robots actifs, uniquement s'ils sont eux aussi hors base
            for autre_robot in env.robots:
                if autre_robot == self.robot:
                    continue

                if getattr(autre_robot, "en_panne", False):
                    continue

                # Les robots encore dans la base ne sont pas pris en compte
                if self._est_dans_la_base(autre_robot):
                    continue

                obs_robot = ObstacleCercle(autre_robot.x, autre_robot.y, 25)
                dist = obs_robot.intersection(
                    self.robot.x, self.robot.y, dx, dy, self.portee_max
                )
                if dist is not None and dist < dist_min:
                    dist_min = dist

            self.dernieres_mesures.append((angle_absolu, dist_min))

        return [mesure[1] for mesure in self.dernieres_mesures]