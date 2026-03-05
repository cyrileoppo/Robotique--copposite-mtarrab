import pygame
import math
from ..modele.robot import RobotAmbulance

class VuePygame:
    def __init__(self, largeur, hauteur):
        pygame.init()
        self.ecran = pygame.display.set_mode((largeur, hauteur))
        pygame.display.set_caption("La Clinique des Robots")
        self.horloge = pygame.time.Clock()
        
        # Couleurs
        self.COULEUR_FOND = (240, 240, 240)
        self.COULEUR_AMBULANCE = (200, 50, 50)  # Rouge
        self.COULEUR_STANDARD = (50, 150, 200)  # Bleu
        self.COULEUR_PANNE = (100, 100, 100)    # Gris
        self.COULEUR_DIRECTION = (0, 0, 0)      # Noir

    def dessiner(self, environnement):
        """Dessine tout l'environnement [cite: 467-468]."""
        self.ecran.fill(self.COULEUR_FOND)

        for robot in environnement.robots:
            # 1. Choix de la couleur selon le type et l'état
            if robot.en_panne:
                couleur = self.COULEUR_PANNE
            elif isinstance(robot, RobotAmbulance):
                couleur = self.COULEUR_AMBULANCE
            else:
                couleur = self.COULEUR_STANDARD

            # 2. Dessiner le corps du robot (un cercle)
            x_px, y_px = int(robot.x), int(robot.y)
            rayon = 15
            pygame.draw.circle(self.ecran, couleur, (x_px, y_px), rayon)

            # 3. Dessiner un trait pour montrer l'orientation (theta)
            fin_x = x_px + int(math.cos(robot.theta) * rayon * 1.5)
            fin_y = y_px + int(math.sin(robot.theta) * rayon * 1.5)
            pygame.draw.line(self.ecran, self.COULEUR_DIRECTION, (x_px, y_px), (fin_x, fin_y), 3)

        pygame.display.flip()

    def quitter(self):
        pygame.quit()