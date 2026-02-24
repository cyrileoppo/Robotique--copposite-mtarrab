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