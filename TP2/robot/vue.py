import pygame
import math

class VuePygame:
    def __init__(self, largeur=800, hauteur=600, scale=50):
        pygame.init()
        self.screen = pygame.display.set_mode((largeur, hauteur))
        self.scale, self.largeur, self.hauteur = scale, largeur, hauteur
        self.clock = pygame.time.Clock()

    def convertir_coordonnees(self, x, y):
        return int(self.largeur / 2 + (x * self.scale)), int(self.hauteur / 2 - (y * self.scale))

    def dessiner(self, robot, obstacles=[]): # obstacles par anticipation
        self.screen.fill((240, 240, 240))
        rx, ry = self.convertir_coordonnees(robot.x, robot.y)
        r_px = int(robot.rayon * self.scale)
        pygame.draw.circle(self.screen, (0, 0, 255), (rx, ry), r_px)
        
        # Orientation
        fx = rx + int(r_px * math.cos(robot.orientation))
        fy = ry - int(r_px * math.sin(robot.orientation))
        pygame.draw.line(self.screen, (0, 0, 0), (rx, ry), (fx, fy), 3)
        pygame.display.flip()

    def tick(self, fps=60):
        self.clock.tick(fps)