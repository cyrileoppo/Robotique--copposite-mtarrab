"""environnement.py — Monde de la simulation : robots, obstacles et physique."""
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

    # ── Ajout d'entités ───────────────────────────────────────────────

    def ajouter_robot(self, robot):
        self.robots.append(robot)
        self.logger.debug(
            f"Robot {robot.id} ajouté à ({robot.x:.1f}, {robot.y:.1f})")

    def ajouter_obstacle(self, obs):
        self.obstacles.append(obs)

    # ── Bordures invisibles (4 grands cercles aux bords) ──────────────

    @staticmethod
    def _creer_bordures(largeur, hauteur):
        m = _RAYON_ROBOT
        r = 2000
        return [
            ObstacleCercle(x=-r + m, y=hauteur / 2, rayon=r),
            ObstacleCercle(x=largeur + r - m, y=hauteur / 2, rayon=r),
            ObstacleCercle(x=largeur / 2, y=-r + m, rayon=r),
            ObstacleCercle(x=largeur / 2, y=hauteur + r - m, rayon=r),
        ]

    def _est_dans_la_base(self, robot):
        return (math.hypot(robot.x - config.BASE_X,
                           robot.y - config.BASE_Y)
                < config.RAYON_SORTIE_BASE)

    # ── Pas de simulation ─────────────────────────────────────────────

    def step(self, commandes, dt):
        """Avance d'un pas de temps : applique commandes et gère les collisions."""
        for robot in self.robots:
            v_cmd, omega_cmd = commandes.get(robot.id, (0.0, 0.0))
            old_x, old_y, old_theta = robot.x, robot.y, robot.theta
            robot_dans_base = self._est_dans_la_base(robot)

            # ── Sas de sortie de base (file d'attente) ────────────
            dist_base = math.hypot(
                robot.x - config.BASE_X, robot.y - config.BASE_Y)
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
                    est_ambulance = (
                        getattr(autre_robot, "type_robot", "")
                        == "ambulance"
                    )

                    if self._est_dans_la_base(autre_robot):
                        continue

                    # Un robot hors base bloque la sortie
                    if (not est_ambulance
                            and config.RAYON_ACTION
                            <= dist_autre < config.RAYON_SORTIE_BASE):
                        sortie_occupee = True
                        break

                    # Priorité au plus petit ID
                    if (not est_ambulance
                            and dist_autre < config.RAYON_ACTION
                            and autre_robot.id < robot.id
                            and not getattr(autre_robot,
                                            "en_panne", False)):
                        sortie_occupee = True
                        break

                if sortie_occupee:
                    v_cmd = 0.0
                    omega_cmd = 0.0

            # ── Application de la commande moteur ─────────────────
            robot.appliquer_commande(v_cmd, omega_cmd, dt)

            # ── Détection de collisions ───────────────────────────

            # 1. Collision avec obstacles fixes
            collision_obstacle = any(
                math.hypot(robot.x - obs.x, robot.y - obs.y)
                < obs.rayon + _RAYON_ROBOT
                for obs in self.obstacles
            )

            # 2. Collision avec un autre robot (hors base uniquement)
            collision_robot = False
            robot_bloquant = None
            if not collision_obstacle and not robot_dans_base:
                for autre_robot in self.robots:
                    if autre_robot.id == robot.id:
                        continue
                    if self._est_dans_la_base(autre_robot):
                        continue
                    if (math.hypot(robot.x - autre_robot.x,
                                   robot.y - autre_robot.y)
                            < 2 * _RAYON_ROBOT):
                        collision_robot = True
                        robot_bloquant = autre_robot
                        break

            # 3. Collision avec les bordures de la fenêtre
            collision_bordure = False
            if not collision_obstacle and not collision_robot:
                collision_bordure = (
                    robot.x < _RAYON_ROBOT
                    or robot.x > self.largeur - _RAYON_ROBOT
                    or robot.y < _RAYON_ROBOT
                    or robot.y > self.hauteur - _RAYON_ROBOT
                )

            # ── Réponse aux collisions ────────────────────────────

            if collision_obstacle or collision_bordure:
                # Annuler le déplacement et stopper
                robot.x, robot.y = old_x, old_y
                robot.theta = old_theta
                robot.moteur.v = 0.0
                robot.moteur.omega = 0.0

            elif collision_robot:
                # Annuler le déplacement mais dévier pour éviter le blocage mutuel
                robot.x, robot.y = old_x, old_y
                robot.moteur.v = 0.0
                robot.moteur.omega = 0.0
                # Produit vectoriel → tourner du côté opposé au robot bloquant
                dx = robot_bloquant.x - robot.x
                dy = robot_bloquant.y - robot.y
                cross = (math.cos(old_theta) * dy
                         - math.sin(old_theta) * dx)
                perturbation = -0.5 if cross >= 0 else 0.5
                robot.theta = old_theta + perturbation

    @property
    def tous_obstacles(self):
        """Obstacles fixes + bordures invisibles."""
        return self.obstacles + self._bordures