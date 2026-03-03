class Environnement:
    """Représente le monde simulé dans lequel évolue le robot."""
    
    def __init__(self, ambulance, base_x=0.0, base_y=0.0):
        self.ambulance = ambulance
        self.robots_standards = []
        self.obstacles = []
        self.base_x = base_x
        self.base_y = base_y

    def ajouter_robot(self, robot):
        """Méthode pour ajouter un robot."""
        self.robots_standards.append(robot)

    def ajouter_obstacle(self, obstacle):
        """Méthode pour ajouter des obstacles."""
        self.obstacles.append(obstacle)

    def tester_collisions(self, robot):
        """L'environnement délègue ce calcul à chaque obstacle individuellement."""
        for obs in self.obstacles:
            if obs.collision(robot.x, robot.y, robot.rayon):
                return True
        return False

    def mettre_a_jour(self, dt):
        """Met à jour la simulation et teste les collisions."""
        self.ambulance.sauvegarder_etat()
        self.ambulance.mettre_a_jour(dt)
        
        if self.tester_collisions(self.ambulance):
            self.ambulance.annuler_deplacement()

        for robot in self.robots_standards:
            robot.sauvegarder_etat()
            robot.mettre_a_jour(dt)
            
            if self.tester_collisions(robot):
                robot.annuler_deplacement()

            if robot.en_panne and robot not in self.ambulance.file_attente:
                self.ambulance.file_attente.append(robot)