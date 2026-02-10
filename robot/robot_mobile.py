import math

class RobotMobile:
    def __init__(self, x: float, y: float, orientation: float = 0.0):
        """
        Initialise un robot mobile.
        :param x: Position sur l'axe des abscisses
        :param y: Position sur l'axe des ordonnées
        :param orientation: Angle en radians (0.0 par défaut)
        """
        self.x = x
        self.y = y
        self.orientation = orientation
        
    import math

class RobotMobile:
    def __init__(self, x, y, orientation):
        self.x = x
        self.y = y
        self.orientation = orientation

    def avancer(self, distance):
        self.x = self.x + distance * math.cos(self.orientation)
        self.y = self.y + distance * math.sin(self.orientation)

    def tourner(self, angle):
        self.orientation = (self.orientation + angle) % (2 * math.pi)

    def afficher(self):
        print(f"(x={self.x:.2f}, y={self.y:.2f}, orientation={self.orientation:.2f})")
        