import math

class ControleurAutonome:
    """Contrôleur centralisé qui gère l'IA de tous les robots."""
    
    def __init__(self, environnement):
        self.env = environnement
        self.cible_actuelle = None
        self.etat_ambulance = "A_LA_BASE"

    def mettre_a_jour_commandes(self):
        """Calcule et envoie les commandes (v, omega) à chaque robot."""
        self._gerer_robots_standards()
        self._gerer_ambulance()

    def _evitement_reactif(self, robot, v_cible, omega_cible):
        """Simule un capteur virtuel pour esquiver les obstacles."""
        distance_min = float('inf')
        obstacle_le_plus_proche = None
        
        for obs in self.env.obstacles:
            d = math.hypot(obs.x - robot.x, obs.y - robot.y) - obs.rayon - robot.rayon
            if d < distance_min:
                distance_min = d
                obstacle_le_plus_proche = obs

        rayon_detection = 1.5 # 
        
        if obstacle_le_plus_proche and distance_min < rayon_detection:
            angle_obs = math.atan2(obstacle_le_plus_proche.y - robot.y, obstacle_le_plus_proche.x - robot.x)
            diff_angle = (angle_obs - robot.orientation + math.pi) % (2*math.pi) - math.pi
            
            if abs(diff_angle) < math.pi / 2:
                v_cible = 0.0 # Freinage d'urgence
                omega_cible = 1.0 if diff_angle < 0 else -1.0 
                
        return v_cible, omega_cible

    def _gerer_robots_standards(self):
        """Fait avancer les robots sains avec évitement d'obstacles."""
        for robot in self.env.robots_standards:
            if not robot.en_panne:
                v, w = self._evitement_reactif(robot, v_cible=0.5, omega_cible=0.0)
                robot.commander(v=v, omega=w)

    def _algorithme_sac_a_dos(self, capacite, robots_en_panne):
        """Sélectionne les robots à sauver en maximisant le nombre sous contrainte de poids."""
        n = len(robots_en_panne)
        cap = int(capacite)
        dp = [[0 for _ in range(cap + 1)] for _ in range(n + 1)]
        
        for i in range(1, n + 1):
            poids = int(robots_en_panne[i-1].poids)
            for w in range(1, cap + 1):
                if poids <= w:
                    dp[i][w] = max(dp[i-1][w], 1 + dp[i-1][w-poids])
                else:
                    dp[i][w] = dp[i-1][w]
                    
        selection = []
        w = cap
        for i in range(n, 0, -1):
            if dp[i][w] != dp[i-1][w]:
                selection.append(robots_en_panne[i-1])
                w -= int(robots_en_panne[i-1].poids)
        return selection

    def _plus_court_chemin(self, depart_x, depart_y, cibles):
        """Heuristique du plus proche voisin pour trier la tournée."""
        trajet = []
        cx, cy = depart_x, depart_y
        restants = cibles[:]
        
        while restants:
            plus_proche = min(restants, key=lambda r: math.hypot(r.x - cx, r.y - cy))
            trajet.append(plus_proche)
            cx, cy = plus_proche.x, plus_proche.y
            restants.remove(plus_proche)
            
        return trajet

    def _gerer_ambulance(self):
        """Machine à états de l'ambulance."""
        amb = self.env.ambulance
        
        # 1. Si à la base et des robots sont en panne
        if self.etat_ambulance == "A_LA_BASE" and len(self.env.robots_standards) > 0:
            en_panne = [r for r in self.env.robots_standards if r.en_panne and r not in amb.file_attente]
            if en_panne:
                selection = self._algorithme_sac_a_dos(amb.capacite_max, en_panne)
                amb.file_attente = self._plus_court_chemin(self.env.base_x, self.env.base_y, selection)
                if amb.file_attente:
                    self.cible_actuelle = amb.file_attente.pop(0)
                    self.etat_ambulance = "EN_MISSION"
                    
        # 2. En mission de sauvetage
        elif self.etat_ambulance == "EN_MISSION" and self.cible_actuelle:
            dist_cible = math.hypot(self.cible_actuelle.x - amb.x, self.cible_actuelle.y - amb.y)
            
            if dist_cible < 0.5:
                self.cible_actuelle.en_panne = False
                self.cible_actuelle.emettre_signal()
                
                if amb.file_attente:
                    self.cible_actuelle = amb.file_attente.pop(0)
                else:
                    self.cible_actuelle = None
                    self.etat_ambulance = "RETOUR_BASE"
            else:
                self._naviguer_vers(amb, self.cible_actuelle.x, self.cible_actuelle.y)

        # 3. Retour à la base
        elif self.etat_ambulance == "RETOUR_BASE":
            dist_base = math.hypot(self.env.base_x - amb.x, self.env.base_y - amb.y)
            if dist_base < 0.5:
                amb.commander(v=0.0, omega=0.0)
                self.etat_ambulance = "A_LA_BASE"
            else:
                self._naviguer_vers(amb, self.env.base_x, self.env.base_y)

    def _naviguer_vers(self, robot, cible_x, cible_y):
        """Pilote le robot vers un point (x, y) avec évitement."""
        angle_cible = math.atan2(cible_y - robot.y, cible_x - robot.x)
        diff_angle = (angle_cible - robot.orientation + math.pi) % (2*math.pi) - math.pi
        
        omega = 1.5 * diff_angle
        v = 1.0 if abs(diff_angle) < 0.5 else 0.2
        v_final, omega_final = self._evitement_reactif(robot, v, omega)
        robot.commander(v=v_final, omega=omega_final)