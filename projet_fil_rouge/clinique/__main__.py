import argparse
import logging
import pygame

from .logging_config import setup_logger
from .modele.environnement import Environnement
from .modele.robot import RobotStandard, RobotAmbulance
from .modele.obstacles import ObstacleCercle
from .vue.vue_pygame import VuePygame
from .controleur.strategies import Navigator, GoalAndAvoidStrategy

def parse_args():
    """Gère les arguments en ligne de commande."""
    parser = argparse.ArgumentParser(description="Simulation de la Clinique des Robots")
    parser.add_argument("--debug", action="store_true", help="Active les logs de niveau DEBUG")
    parser.add_argument("--nb-robots", type=int, default=3, help="Nombre de robots standards")
    return parser.parse_args()

def main():
    args = parse_args()
    setup_logger(args.debug)
    logger = logging.getLogger("Simulation")
    
    largeur, hauteur = 800, 600
    
    # ==========================================
    # 1. MODÈLE (Logique métier et physique)
    # ==========================================
    env = Environnement(largeur, hauteur)
    
    # Ajout de l'ambulance
    ambulance = RobotAmbulance("Ambu-1", x=100, y=150)
    env.ajouter_robot(ambulance)
    
    # Ajout des obstacles fixes
    env.ajouter_obstacle(ObstacleCercle(x=400, y=150, rayon=50))
    env.ajouter_obstacle(ObstacleCercle(x=600, y=300, rayon=80))
    
    # Ajout des robots standards
    for i in range(args.nb_robots):
        # On les place en bas de l'écran
        robot = RobotStandard(f"R-{i+1}", x=100 + i*150, y=500, poids=20)
        env.ajouter_robot(robot)
        
    # ==========================================
    # 2. VUE (Affichage graphique)
    # ==========================================
    vue = VuePygame(largeur, hauteur)
    
    # ==========================================
    # 3. CONTRÔLEUR (Intelligence et Navigation)
    # ==========================================
    # Création de la stratégie combinée (Évitement + Ciblage) [cite: 780-782]
    strategy_evitement_et_ciblage = GoalAndAvoidStrategy(distance_securite=50.0)
    
    en_cours = True
    dt = 0.1
    
    logger.info("Démarrage de la boucle graphique.")
    
    while en_cours:
        # a) Gestion des événements (fermer la fenêtre)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                en_cours = False
                
        # b) Mise à jour de l'état des robots standards (pannes potentielles)
        for robot in env.robots:
            if isinstance(robot, RobotStandard):
                robot.mettre_a_jour_etat()
                
        # c) L'ambulance cherche une cible (le premier robot en panne)
        robot_a_sauver = None
        for robot in env.robots:
            if robot.en_panne and isinstance(robot, RobotStandard):
                robot_a_sauver = robot
                break # On s'arrête au premier trouvé
                
        # d) Mise à jour de la cible dans la stratégie
        if robot_a_sauver:
            strategy_evitement_et_ciblage.set_cible(robot_a_sauver.x, robot_a_sauver.y)
        else:
            strategy_evitement_et_ciblage.set_cible(None, None)

        # e) Lecture des capteurs pour l'ambulance
        mesures = ambulance.capteur.read(env)
        
        # f) Décision du Contrôleur
        # On passe les mesures ET la position/orientation de l'ambulance à la stratégie
        cmd_ambu = strategy_evitement_et_ciblage.compute_command(mesures, ambulance.x, ambulance.y, ambulance.theta)
            
        # g) Application des commandes
        commandes = {"Ambu-1": cmd_ambu} 
        for i in range(args.nb_robots):
            robot_std = next(r for r in env.robots if r.id == f"R-{i+1}")
            # Les standards avancent un peu s'ils ne sont pas en panne
            if not robot_std.en_panne:
                commandes[f"R-{i+1}"] = (0.3, 0.0) 
            else:
                commandes[f"R-{i+1}"] = (0.0, 0.0)
                
        # h) Mise à jour du Modèle
        env.step(commandes, dt)
        
        # i) Mise à jour de la Vue
        vue.dessiner(env)
        
        # j) Limiter la vitesse de la boucle
        vue.horloge.tick(60)
        
    vue.quitter()
    logger.info("Fin de la simulation.")

if __name__ == "__main__":
    main()