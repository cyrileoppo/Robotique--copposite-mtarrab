import argparse
import logging
import pygame
import math

from .logging_config import setup_logger
from .modele.environnement import Environnement
from .modele.robot import RobotStandard, RobotAmbulance
from .modele.obstacles import ObstacleCercle
from .vue.vue_pygame import VuePygame
from .controleur.strategies import Navigator, GoalAndAvoidStrategy

def parse_args():
    parser = argparse.ArgumentParser(description="Simulation de la Clinique des Robots")
    parser.add_argument("--debug", action="store_true", help="Active les logs de niveau DEBUG")
    parser.add_argument("--nb-robots", type=int, default=3, help="Nombre de robots standards")
    return parser.parse_args()

def main():
    args = parse_args()
    setup_logger(args.debug)
    logger = logging.getLogger("Simulation")
    
    largeur, hauteur = 800, 600
    BASE_X, BASE_Y = 700, 100
    
    # ==========================================
    # 1. MODÈLE
    # ==========================================
    env = Environnement(largeur, hauteur)
    
    # BOOST DE L'AMBULANCE : v_max de 2.0 à 5.0, a_max de 0.5 à 1.5 [cite: 508, 529]
    ambulance = RobotAmbulance("Ambu-1", x=BASE_X, y=BASE_Y)
    ambulance.moteur.v_max = 5.0
    ambulance.moteur.a_max = 1.5
    ambulance.moteur.frottement = 0.05 # Moins de frottement pour glisser plus [cite: 522, 527]
    
    ambulance.robot_charge = None 
    env.ajouter_robot(ambulance)
    
    # Obstacles [cite: 187-190]
    env.ajouter_obstacle(ObstacleCercle(x=400, y=150, rayon=50))
    env.ajouter_obstacle(ObstacleCercle(x=600, y=300, rayon=80))
    env.ajouter_obstacle(ObstacleCercle(x=300, y=400, rayon=60))
    
    for i in range(args.nb_robots):
        robot = RobotStandard(f"R-{i+1}", x=100 + i*150, y=500, poids=20)
        robot.probabilite_panne = 0.002 
        env.ajouter_robot(robot)
        
    # ==========================================
    # 2. VUE
    # ==========================================
    vue = VuePygame(largeur, hauteur)
    
    # ==========================================
    # 3. CONTRÔLEUR
    # ==========================================
    # On augmente la distance de sécurité car l'ambulance va plus vite
    strategy_evitement_et_ciblage = GoalAndAvoidStrategy(distance_securite=70.0)
    
    en_cours = True
    dt = 0.1
    
    while en_cours:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                en_cours = False
                
        # a) Pannes
        for robot in env.robots:
            if isinstance(robot, RobotStandard):
                robot.mettre_a_jour_etat()
                
        # b) Machine à états (Sauvetage)
        if ambulance.robot_charge is None:
            robot_a_sauver = None
            for robot in env.robots:
                if robot.en_panne and isinstance(robot, RobotStandard):
                    robot_a_sauver = robot
                    break
                    
            if robot_a_sauver:
                dist_robot = math.hypot(ambulance.x - robot_a_sauver.x, ambulance.y - robot_a_sauver.y)
                if dist_robot < 30.0: 
                    ambulance.robot_charge = robot_a_sauver
                    env.robots.remove(robot_a_sauver)
                    logger.info(f"Chargement de {robot_a_sauver.id}")
                    strategy_evitement_et_ciblage.set_cible(BASE_X, BASE_Y)
                else:
                    strategy_evitement_et_ciblage.set_cible(robot_a_sauver.x, robot_a_sauver.y)
            else:
                dist_base = math.hypot(ambulance.x - BASE_X, ambulance.y - BASE_Y)
                if dist_base > 20.0:
                    strategy_evitement_et_ciblage.set_cible(BASE_X, BASE_Y)
                else:
                    strategy_evitement_et_ciblage.set_cible(None, None)
        else:
            strategy_evitement_et_ciblage.set_cible(BASE_X, BASE_Y)
            dist_base = math.hypot(ambulance.x - BASE_X, ambulance.y - BASE_Y)
            if dist_base < 30.0:
                repare = ambulance.robot_charge
                repare.en_panne = False
                repare.x, repare.y = BASE_X, BASE_Y + 120
                env.ajouter_robot(repare)
                logger.info(f"{repare.id} réparé !")
                ambulance.robot_charge = None

        # c) Commandes [cite: 804-805]
        mesures = ambulance.capteur.read(env)
        # On booste la vitesse de commande à 4.0 au lieu de 1.0
        v_cmd, omega_cmd = strategy_evitement_et_ciblage.compute_command(mesures, ambulance.x, ambulance.y, ambulance.theta)
        if v_cmd > 0: v_cmd = 4.0 
        
        commandes = {"Ambu-1": (v_cmd, omega_cmd)} 
        for robot in env.robots:
            if isinstance(robot, RobotStandard):
                commandes[robot.id] = (0.5, 0.02) if not robot.en_panne else (0.0, 0.0)
                
        env.step(commandes, dt)
        vue.dessiner(env)
        vue.horloge.tick(60)
        
    vue.quitter()

if __name__ == "__main__":
    main()