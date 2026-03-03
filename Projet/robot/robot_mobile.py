import math

class RobotMobile:
    """Classe de base représentant un robot mobile."""
    _nb_robots = 0 

    def __init__(self, x=0.0, y=0.0, orientation=0.0, moteur=None, rayon=15.0):
        self._x = x
        self._y = y
        self.orientation = orientation
        self.moteur = moteur 
        self.rayon = rayon
        self.x_prec = x
        self.y_prec = y
        self.orientation_prec = orientation
        
        RobotMobile._nb_robots += 1 [cite: 535]

    @property
    def x(self) -> float:
        return self._x

    @x.setter
    def x(self, value: float):
        self._x = value

    @property
    def y(self) -> float:
        return self._y

    @y.setter
    def y(self, value: float):
        self._y = value

    def sauvegarder_etat(self):
        """Sauvegarde la position avant un déplacement."""
        self.x_prec = self._x
        self.y_prec = self._y
        self.orientation_prec = self.orientation

    def annuler_deplacement(self):
        """Restaure la position précédente en cas de collision physique."""
        self._x = self.x_prec
        self._y = self.y_prec
        self.orientation = self.orientation_prec

    def commander(self, **kwargs):
        """Transmet les commandes au moteur."""
        if self.moteur is not None:
            self.moteur.commander(**kwargs)

    def mettre_a_jour(self, dt):
        """Met à jour le robot via son moteur."""
        if self.moteur is not None:
            self.moteur.mettre_a_jour(self, dt)

    def __str__(self):
        """Affiche l'état du robot."""
        return f"Robot({self.x:.2f}, {self.y:.2f}, theta={self.orientation:.2f})"


class RobotStandard(RobotMobile):
    """Robot pouvant tomber en panne."""
    def __init__(self, x, y, poids, moteur=None):
        super().__init__(x=x, y=y, orientation=0.0, moteur=moteur, rayon=15.0)
        self.poids = poids
        self.en_panne = False
        self.temps_sans_signal = 0.0
        self.limite_signal = 300.0

    def emettre_signal(self):
        """Réinitialise le compteur de temps (le robot va bien)."""
        self.temps_sans_signal = 0.0

    def mettre_a_jour(self, dt):
        """Met à jour le robot et vérifie s'il tombe en panne."""
        super().mettre_a_jour(dt)
        if not self.en_panne:
            self.temps_sans_signal += dt
            if self.temps_sans_signal >= self.limite_signal:
                self.en_panne = True
                self.commander(v=0.0, omega=0.0)


class RobotAmbulance(RobotMobile):
    """Robot chargé de secourir les autres."""
    def __init__(self, x, y, capacite_max=50.0, moteur=None):
        super().__init__(x=x, y=y, orientation=0.0, moteur=moteur, rayon=20.0)
        self.capacite_max = capacite_max
        self.file_attente = []
        self.charge_actuelle = 0.0