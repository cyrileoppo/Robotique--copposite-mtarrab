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
        
        COULEUR_OBS = (80, 80, 80)
        for obs in environnement.obstacles:
            pygame.draw.circle(self.ecran, COULEUR_OBS, (int(obs.x), int(obs.y)), obs.rayon)
        
        COULEUR_RAYON = (0, 255, 0)
        
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
            
            if hasattr(robot, 'capteur') and hasattr(robot.capteur, 'dernieres_mesures'):
                    for angle_absolu, dist in robot.capteur.dernieres_mesures:
                        fin_x = int(robot.x + math.cos(angle_absolu) * dist)
                        fin_y = int(robot.y + math.sin(angle_absolu) * dist)
                        pygame.draw.line(self.ecran, COULEUR_RAYON, (int(robot.x), int(robot.y)), (fin_x, fin_y), 1) 

        # Dessiner la Base de Réparation (un carré vert en haut à droite)
        COULEUR_BASE = (50, 200, 50)
        pygame.draw.rect(self.ecran, COULEUR_BASE, (650, 50, 100, 100), border_radius=10)
        pygame.display.flip()

    def quitter(self):
        pygame.quit()