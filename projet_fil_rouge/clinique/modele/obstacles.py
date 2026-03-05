import math

class ObstacleCercle:
    def __init__(self, x, y, rayon):
        self.x = x
        self.y = y
        self.rayon = rayon

    def intersection(self, ox, oy, dx, dy, max_range):
        """Calcul d'intersection rayon/cercle selon le cours ."""
        fx = ox - self.x
        fy = oy - self.y
        
        a = dx*dx + dy*dy
        b = 2 * (fx*dx + fy*dy)
        c = fx*fx + fy*fy - self.rayon*self.rayon
        
        discriminant = b*b - 4*a*c
        
        if discriminant < 0:
            return None # Le rayon ne touche jamais le cercle [cite: 233]
            
        t1 = (-b - math.sqrt(discriminant)) / (2*a)
        t2 = (-b + math.sqrt(discriminant)) / (2*a)
        
        # On garde la plus petite intersection valide dans la portée [cite: 228-230, 236]
        distances_valides = [t for t in (t1, t2) if 0 < t <= max_range]
        
        if distances_valides:
            return min(distances_valides)
        return None