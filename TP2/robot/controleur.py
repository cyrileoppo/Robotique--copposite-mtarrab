import pygame
from .controleur import Controleur

class ControleurClavierPygame(Controleur):
    def lire_commande(self):
        keys = pygame.key.get_pressed()
        v, omega = 0.0, 0.0
        if keys[pygame.K_UP]: v = 2.0
        if keys[pygame.K_DOWN]: v = -2.0
        if keys[pygame.K_LEFT]: omega = 1.5
        if keys[pygame.K_RIGHT]: omega = -1.5
        return v, omega