class RobotMobile:
    def __init__(self, x=0, y=0, orientation=0, rayon=0.3, moteur=None):
        self.x = x
        self.y = y
        self.orientation = orientation
        self.rayon = rayon
        self.moteur = moteur

    def mettre_a_jour(self, v, omega, dt):
        if self.moteur:
            dx, dy, dtheta = self.moteur.calculer_mouvement(v, omega, self.orientation, dt)
            self.x += dx
            self.y += dy
            self.orientation += dtheta