class Environnement:
    def __init__(self, ambulance, base_x=0.0, base_y=0.0):
        self.ambulance = ambulance
        self.robots_standards = []
        self.obstacles = []
        self.base_x = base_x
        self.base_y = base_y

    def ajouter_robot(self, robot):
        self.robots_standards.append(robot)

    def ajouter_obstacle(self, obstacle):
        self.obstacles.append(obstacle)

    def tester_collisions(self, robot):
        for obs in self.obstacles:
            if obs.collision(robot.x, robot.y, robot.rayon):
                return True
        return False

    def mettre_a_jour(self, dt):
        # Ambulance
        self.ambulance.sauvegarder_etat()
        self.ambulance.mettre_a_jour(dt)
        if self.tester_collisions(self.ambulance):
            self.ambulance.annuler_deplacement()

        # Robots standards
        for robot in self.robots_standards:
            if robot.en_reparation:
                robot.temps_reparation += dt
                if robot.temps_reparation >= robot.duree_reparation:
                    robot.en_reparation = False
                    robot.en_panne = False
                    robot.emettre_signal()
                    robot.commander(v=0.5, omega=0.0)
                continue

            robot.sauvegarder_etat()
            robot.mettre_a_jour(dt)

            if self.tester_collisions(robot):
                robot.annuler_deplacement()