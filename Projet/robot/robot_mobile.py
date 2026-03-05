import random


class RobotMobile:
    _nb_robots = 0

    def __init__(self, x=0.0, y=0.0, orientation=0.0, moteur=None, rayon=0.4):
        self._x = x
        self._y = y
        self.orientation = orientation
        self.moteur = moteur
        self.rayon = rayon

        self.x_prec = x
        self.y_prec = y
        self.orientation_prec = orientation

        RobotMobile._nb_robots += 1

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value

    def sauvegarder_etat(self):
        self.x_prec = self._x
        self.y_prec = self._y
        self.orientation_prec = self.orientation

    def annuler_deplacement(self):
        self._x = self.x_prec
        self._y = self.y_prec
        self.orientation = self.orientation_prec

    def commander(self, **kwargs):
        if self.moteur is not None:
            self.moteur.commander(**kwargs)

    def mettre_a_jour(self, dt):
        if self.moteur is not None:
            self.moteur.mettre_a_jour(self, dt)

    def __str__(self):
        return f"Robot({self.x:.2f}, {self.y:.2f}, theta={self.orientation:.2f})"


class RobotStandard(RobotMobile):
    def __init__(self, x, y, poids, moteur=None):
        super().__init__(x=x, y=y, orientation=0.0, moteur=moteur, rayon=0.35)
        self.poids = poids

        self.en_panne = False
        self.en_reparation = False

        self.temps_sans_signal = random.uniform(0.0, 5.0)
        self.limite_signal = random.uniform(20.0, 45.0)
        self.proba_panne = 0.35

        self.temps_reparation = 0.0
        self.duree_reparation = 6.0

    def emettre_signal(self):
        self.temps_sans_signal = 0.0

    def mettre_a_jour(self, dt):
        if self.en_reparation:
            return

        super().mettre_a_jour(dt)

        if not self.en_panne:
            self.temps_sans_signal += dt
            if self.temps_sans_signal >= self.limite_signal:
                if random.random() < self.proba_panne:
                    self.en_panne = True
                    self.commander(v=0.0, omega=0.0)
                self.temps_sans_signal = 0.0


class RobotAmbulance(RobotMobile):
    def __init__(self, x, y, capacite_max=50.0, moteur=None):
        super().__init__(x=x, y=y, orientation=0.0, moteur=moteur, rayon=0.45)
        self.capacite_max = capacite_max
        self.file_attente = []