import math

class MoteurDifferentiel:
    def calculer_mouvement(self, v, omega, orientation, dt):
        dx = v * math.cos(orientation) * dt
        dy = v * math.sin(orientation) * dt
        dtheta = omega * dt
        return dx, dy, dtheta