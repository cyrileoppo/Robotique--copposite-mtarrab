"""obstacles.py — Représentation des obstacles circulaires et intersection rayon/cercle."""
import math


class ObstacleCercle:
    """Obstacle circulaire défini par un centre (x, y) et un rayon."""

    def __init__(self, x, y, rayon):
        self.x = x
        self.y = y
        self.rayon = rayon

    def intersection(self, ox, oy, dx, dy, max_range):
        """Intersection rayon/cercle (équation quadratique). Retourne la distance ou None."""
        fx = ox - self.x
        fy = oy - self.y

        a = dx*dx + dy*dy
        b = 2 * (fx*dx + fy*dy)
        c = fx*fx + fy*fy - self.rayon*self.rayon

        discriminant = b*b - 4*a*c

        if discriminant < 0:
            return None

        t1 = (-b - math.sqrt(discriminant)) / (2*a)
        t2 = (-b + math.sqrt(discriminant)) / (2*a)

        # Plus petite intersection valide dans la portée
        distances_valides = [t for t in (t1, t2) if 0 < t <= max_range]

        if distances_valides:
            return min(distances_valides)
        return None