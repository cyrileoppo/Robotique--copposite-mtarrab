import logging

class Environnement:
    def __init__(self, largeur, hauteur):
        self.largeur = largeur
        self.hauteur = hauteur
        self.robots = []
        self.logger = logging.getLogger(__name__)

    def ajouter_robot(self, robot):
        self.robots.append(robot)
        self.logger.debug(f"Robot {robot.id} ajouté à ({robot.x}, {robot.y})")

    def step(self, commandes, dt):
        """Fait avancer la simulation d'un pas de temps dt."""
        for robot in self.robots:
            # Récupère la commande associée à ce robot (ou (0,0) par défaut)
            v_cmd, omega_cmd = commandes.get(robot.id, (0.0, 0.0))
            robot.appliquer_commande(v_cmd, omega_cmd, dt)