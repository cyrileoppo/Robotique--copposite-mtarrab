import math

class RobotMobile:

    def __init__(self, x: float, y: float, orientation: float = 0.0):
        self.__x = x
        self.__y = y
        self.__orientation = orientation

    # ===== Getter x =====
    @property
    def x(self) -> float:
        return self.__x

    # ===== Setter x =====
    @x.setter
    def x(self, value: float):
        self.__x = float(value)

    # ===== Getter y =====
    @property
    def y(self) -> float:
        return self.__y

    @y.setter
    def y(self, value: float):
        self.__y = float(value)

    # ===== Getter orientation =====
    @property
    def orientation(self) -> float:
        return self.__orientation

    @orientation.setter
    def orientation(self, value: float):
        self.__orientation = value % (2 * math.pi)

    # ===== Méthodes =====
    def avancer(self, distance: float):
        self.__x += distance * math.cos(self.__orientation)
        self.__y += distance * math.sin(self.__orientation)

    def tourner(self, angle: float):
        self.__orientation = (self.__orientation + angle) % (2 * math.pi)

    def afficher(self):
        print(f"(x={self.__x:.2f}, y={self.__y:.2f}, orientation={self.__orientation:.2f})")
