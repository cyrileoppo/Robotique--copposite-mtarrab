import pygame
from abc import ABC, abstractmethod

class Controleur(ABC):
    @abstractmethod
    def lire_commande(self): pass

class ControleurTerminal(Controleur):
    def lire_commande(self):
        try:
            entree = input("Commande (v omega) : ").split()
            return float(entree[0]), float(entree[1])
        except:
            return 0.0, 0.0

class ControleurClavierPygame(Controleur):
    def lire_commande(self):
        keys = pygame.key.get_pressed()
        v, omega = 0.0, 0.0
        if keys[pygame.K_UP]: v = 2.0
        if keys[pygame.K_DOWN]: v = -2.0
        if keys[pygame.K_LEFT]: omega = 1.5
        if keys[pygame.K_RIGHT]: omega = -1.5
        return v, omega