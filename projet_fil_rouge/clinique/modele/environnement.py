import logging
import math
from .obstacles import ObstacleCercle
from .. import config

_RAYON_ROBOT = config.STANDARD_RAYON_COLLISION


class Environnement:
    """Conteneur de la simulation : robots, obstacles et bordures invisibles."""

    def __init__(self, largeur, hauteur):
        self.largeur = largeur
        self.hauteur = hauteur
        self.robots = []
        self.obstacles = []
        self.logger = logging.getLogger(__name__)
        self._bordures = self._creer_bordures(largeur, hauteur)

    def ajouter_robot(self, robot):
        self.robots.append(robot)
        self.logger.debug(f"Robot {robot.id} ajouté à ({robot.x:.1f}, {robot.y:.1f})")

    def ajouter_obstacle(self, obs):
        self.obstacles.append(obs)

    @staticmethod
    def _creer_bordures(largeur, hauteur):
        m = _RAYON_ROBOT
        r = 2000
        return [
            ObstacleCercle(x=-r + m, y=hauteur / 2, rayon=r),               # gauche
            ObstacleCercle(x=largeur + r - m, y=hauteur / 2, rayon=r),     # droite
            ObstacleCercle(x=largeur / 2, y=-r + m, rayon=r),              # haut
            ObstacleCercle(x=largeur / 2, y=hauteur + r - m, rayon=r),     # bas
        ]

    def _est_dans_la_base(self, robot):
        return math.hypot(robot.x - config.BASE_X, robot.y - config.BASE_Y) < config.RAYON_SORTIE_BASE

    def step(self, commandes, dt):
        """Avance la simulation d'un pas de temps avec détection de collisions."""
        for robot in self.robots:
            v_cmd, omega_cmd = commandes.get(robot.id, (0.0, 0.0))
            old_x, old_y, old_theta = robot.x, robot.y, robot.theta
            robot_dans_base = self._est_dans_la_base(robot)

            # --- GESTION DE LA SORTIE DE BASE (sas d'attente) ---
            dist_base = math.hypot(robot.x - config.BASE_X, robot.y - config.BASE_Y)
            est_a_la_base = dist_base < config.RAYON_ACTION

            if est_a_la_base and v_cmd > 0:
                sortie_occupee = False

                for autre_robot in self.robots:
                    if autre_robot.id == robot.id:
                        continue

                    dist_autre = math.hypot(
                        autre_robot.x - config.BASE_X,
                        autre_robot.y - config.BASE_Y
                    )

                    est_ambulance = getattr(autre_robot, "type_robot", "") == "ambulance"

                    # On ignore totalement les robots encore dans la base
                    if self._est_dans_la_base(autre_robot):
                        continue

                    # Cas 1 : un robot standard hors base bouche la sortie
                    if (
                        not est_ambulance
                        and config.RAYON_ACTION <= dist_autre < config.RAYON_SORTIE_BASE
                    ):
                        sortie_occupee = True
                        break

                    # Cas 2 : un autre robot standard prioritaire
                    if (
                        not est_ambulance
                        and dist_autre < config.RAYON_ACTION
                        and autre_robot.id < robot.id
                        and getattr(autre_robot, "en_panne", False) is False
                    ):
                        sortie_occupee = True
                        break

                if sortie_occupee:
                    v_cmd = 0.0
                    omega_cmd = 0.0
            # ----------------------------------------------------

            robot.appliquer_commande(v_cmd, omega_cmd, dt)

            # Collision avec obstacles fixes
            collision = any(
                math.hypot(robot.x - obs.x, robot.y - obs.y) < obs.rayon + _RAYON_ROBOT
                for obs in self.obstacles
            )

            # Collision avec les autres robots :
            # seulement si le robot courant est hors de la base
            if not collision and not robot_dans_base:
                for autre_robot in self.robots:
                    if autre_robot.id == robot.id:
                        continue

                    # Les robots encore dans la base ne comptent pas
                    if self._est_dans_la_base(autre_robot):
                        continue

                    if math.hypot(robot.x - autre_robot.x, robot.y - autre_robot.y) < 2 * _RAYON_ROBOT:
                        collision = True
                        break

            # Collision avec les bordures :
            # on les garde actives partout
            if not collision:
                collision = (
                    robot.x < _RAYON_ROBOT
                    or robot.x > self.largeur - _RAYON_ROBOT
                    or robot.y < _RAYON_ROBOT
                    or robot.y > self.hauteur - _RAYON_ROBOT
                )

            if collision:
                # Annuler le déplacement et stopper le robot
                robot.x, robot.y = old_x, old_y
                robot.theta = old_theta
                robot.moteur.v = 0.0
                robot.moteur.omega = 0.0

    @property
    def tous_obstacles(self):
        return self.obstacles + self._bordures