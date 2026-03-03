import pygame
import math

class VuePygame:
    """Classe responsable de l'affichage de la simulation."""
    
    def __init__(self, largeur=800, hauteur=600, scale=30):
        pygame.init()
        self.screen = pygame.display.set_mode((largeur, hauteur))
        pygame.display.set_caption("La Clinique des Robots") 
        self.largeur = largeur 
        self.hauteur = hauteur 
        self.scale = scale 
        self.clock = pygame.time.Clock() 

    def convertir_coordonnees(self, x, y):
        """Convertit les coordonnées (mètres) en pixels à l'écran."""
        px = int(self.largeur / 2 + (x * self.scale))
        py = int(self.hauteur / 2 - (y * self.scale)) 
        return px, py

    def _dessiner_robot(self, x, y, orientation, rayon, couleur):
        """Méthode utilitaire interne pour dessiner un robot et son orientation."""
        px, py = self.convertir_coordonnees(x, y)
        r_pixels = int(rayon * self.scale)
        
        pygame.draw.circle(self.screen, couleur, (px, py), r_pixels)
        
        x_dir = px + int(r_pixels * math.cos(orientation))
        y_dir = py - int(r_pixels * math.sin(orientation)) 
        
        pygame.draw.line(self.screen, (0, 0, 0), (px, py), (x_dir, y_dir), 2)

    def dessiner_environnement(self, environnement):
        """Affiche l'état global du monde simulé."""
        self.screen.fill((240, 240, 240)) 
        base_px, base_py = self.convertir_coordonnees(environnement.base_x, environnement.base_y)
        taille_base = int(2.0 * self.scale)
        pygame.draw.rect(self.screen, (100, 150, 255), 
                         (base_px - taille_base//2, base_py - taille_base//2, taille_base, taille_base))

        for obs in environnement.obstacles:
            px, py = self.convertir_coordonnees(obs.x, obs.y)
            r_pixels = int(obs.rayon * self.scale)
            pygame.draw.circle(self.screen, (80, 80, 80), (px, py), r_pixels)

        for robot in environnement.robots_standards:
            couleur = (255, 165, 0) if robot.en_panne else (50, 200, 50)
            self._dessiner_robot(robot.x, robot.y, robot.orientation, robot.rayon, couleur)

        amb = environnement.ambulance
        self._dessiner_robot(amb.x, amb.y, amb.orientation, amb.rayon, (220, 20, 20))

        pygame.display.flip() 
    def tick(self, fps=60):
        """Gère le temps d'affichage."""
        self.clock.tick(fps) 