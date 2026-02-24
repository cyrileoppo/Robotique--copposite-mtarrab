import math

class ObstacleCirculaire:
    def __init__(self, x, y, rayon):
        self.x, self.y, self.rayon = x, y, rayon

    def collision(self, rx, ry, r_rayon):
        return math.sqrt((self.x - rx)**2 + (self.y - ry)**2) <= (self.rayon + r_rayon)

class Environnement:
    def __init__(self, robot):
        self.robot = robot
        self.obstacles = []

    def ajouter_obstacle(self, obs):
        self.obstacles.append(obs)

    def mettre_a_jour(self, v, omega, dt):
        old_x, old_y = self.robot.x, self.robot.y
        self.robot.mettre_a_jour(v, omega, dt)
        
        for obs in self.obstacles:
            if obs.collision(self.robot.x, self.robot.y, self.robot.rayon):
                self.robot.x, self.robot.y = old_x, old_y # On annule si collision
                break