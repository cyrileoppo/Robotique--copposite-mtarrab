import argparse
import logging
import pygame
import math
import itertools

from .logging_config import setup_logger
from .modele.environnement import Environnement
from .modele.robot import RobotStandard, RobotAmbulance
from .modele.obstacles import ObstacleCercle
from .vue.vue_pygame import VuePygame
from .controleur.strategies import Navigator, GoalAndAvoidStrategy, AvoidStrategy

def parse_args():
    parser = argparse.ArgumentParser(description="Simulation de la Clinique des Robots")
    parser.add_argument("--debug", action="store_true", help="Active les logs de niveau DEBUG")
    parser.add_argument("--nb-robots", type=int, default=5, help="Nombre de robots standards")
    return parser.parse_args()

def algorithme_sac_a_dos(robots_en_panne, capacite_max):
    n = len(robots_en_panne)
    dp = [[0] * (capacite_max + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        poids = robots_en_panne[i-1].poids
        for w in range(capacite_max + 1):
            if poids <= w:
                dp[i][w] = max(dp[i-1][w], dp[i-1][w-poids] + 1)
            else:
                dp[i][w] = dp[i-1][w]

    selection = []
    w = capacite_max
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            selection.append(robots_en_panne[i-1])
            w -= robots_en_panne[i-1].poids
    return selection

def optimiser_trajet_tsp(base_x, base_y, robots_selectionnes):
    if not robots_selectionnes:
        return []

    meilleur_trajet = None
    distance_min = float('inf')

    for permutation in itertools.permutations(robots_selectionnes):
        dist_totale = 0.0
        pos_actuelle = (base_x, base_y)

        for robot in permutation:
            dist_totale += math.hypot(robot.x - pos_actuelle[0], robot.y - pos_actuelle[1])
            pos_actuelle = (robot.x, robot.y)
            
        dist_totale += math.hypot(base_x - pos_actuelle[0], base_y - pos_actuelle[1])

        if dist_totale < distance_min:
            distance_min = dist_totale
            meilleur_trajet = list(permutation)

    return meilleur_trajet

def main():
    args = parse_args()
    setup_logger(args.debug)
    logger = logging.getLogger("Simulation")
    
    largeur, hauteur = 800, 600
    BASE_X, BASE_Y = 700, 100
    RAYON_ACTION = 40.0 
    
    env = Environnement(largeur, hauteur)
    
    ambulance = RobotAmbulance("Ambu-1", x=BASE_X, y=BASE_Y)
    # VITESSE X5 : L'ambulance devient un bolide !
    ambulance.moteur.v_max = 40.0
    ambulance.moteur.a_max = 15.0
    ambulance.moteur.frottement = 0.15 
    ambulance.capacite_max = 50
    ambulance.robots_charges = []
    ambulance.plan_sauvetage = []
    env.ajouter_robot(ambulance)
    
    env.ajouter_obstacle(ObstacleCercle(x=400, y=150, rayon=50))
    env.ajouter_obstacle(ObstacleCercle(x=600, y=300, rayon=80))
    env.ajouter_obstacle(ObstacleCercle(x=300, y=400, rayon=60))
    
    poids_test = [15, 20, 30, 25, 10]
    for i in range(args.nb_robots):
        poids = poids_test[i % len(poids_test)]
        # On les disperse un peu plus aléatoirement
        robot = RobotStandard(f"R-{i+1}", x=100 + (i*100)%600, y=400 + (i*50)%150, poids=poids)
        env.ajouter_robot(robot)
        
    vue = VuePygame(largeur, hauteur)
    
    strategy_evitement_et_ciblage = GoalAndAvoidStrategy(distance_securite=100.0)
    # Nouvelle stratégie pour les robots standards
    strategy_promenade_standards = AvoidStrategy(distance_securite=60.0)
    
    en_cours = True
    dt = 0.1
    
    while en_cours:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                en_cours = False
                
        for robot in env.robots:
            if isinstance(robot, RobotStandard):
                robot.mettre_a_jour_etat()
                
        charge_actuelle = sum(r.poids for r in ambulance.robots_charges)

        if ambulance.plan_sauvetage:
            cible = ambulance.plan_sauvetage[0]
            if cible in env.robots:
                dist_robot = math.hypot(ambulance.x - cible.x, ambulance.y - cible.y)
                if dist_robot <= RAYON_ACTION: 
                    ambulance.moteur.v = 0.0
                    ambulance.moteur.omega = 0.0
                    ambulance.robots_charges.append(cible)
                    env.robots.remove(cible)
                    ambulance.plan_sauvetage.pop(0)
                    logger.info(f"Chargement de {cible.id}. Charge: {charge_actuelle + cible.poids}/{ambulance.capacite_max}")
                else:
                    strategy_evitement_et_ciblage.set_cible(cible.x, cible.y)
            else:
                ambulance.plan_sauvetage.pop(0)
        else:
            if ambulance.robots_charges:
                strategy_evitement_et_ciblage.set_cible(BASE_X, BASE_Y)
                dist_base = math.hypot(ambulance.x - BASE_X, ambulance.y - BASE_Y)
                if dist_base <= RAYON_ACTION:
                    ambulance.moteur.v = 0.0
                    ambulance.moteur.omega = 0.0
                    for repare in ambulance.robots_charges:
                        repare.en_panne = False
                        repare.x, repare.y = BASE_X, BASE_Y + 120
                        env.ajouter_robot(repare)
                    logger.info(f"Base atteinte ! {len(ambulance.robots_charges)} robot(s) réparé(s).")
                    ambulance.robots_charges.clear()
                    strategy_evitement_et_ciblage.set_cible(None, None)
            else:
                robots_en_panne = [r for r in env.robots if isinstance(r, RobotStandard) and r.en_panne]
                if robots_en_panne:
                    selection = algorithme_sac_a_dos(robots_en_panne, ambulance.capacite_max)
                    ambulance.plan_sauvetage = optimiser_trajet_tsp(BASE_X, BASE_Y, selection)
                else:
                    dist_base = math.hypot(ambulance.x - BASE_X, ambulance.y - BASE_Y)
                    if dist_base > RAYON_ACTION:
                        strategy_evitement_et_ciblage.set_cible(BASE_X, BASE_Y)
                    else:
                        strategy_evitement_et_ciblage.set_cible(None, None)
                        ambulance.moteur.v = 0.0
                        ambulance.moteur.omega = 0.0

        # Commandes de l'ambulance
        mesures_ambu = ambulance.capteur.read(env)
        v_cmd_ambu, omega_cmd_ambu = strategy_evitement_et_ciblage.compute_command(mesures_ambu, ambulance.x, ambulance.y, ambulance.theta)
        
        if v_cmd_ambu == 1.0:
            if strategy_evitement_et_ciblage.cible_x is not None:
                dist_cible = math.hypot(ambulance.x - strategy_evitement_et_ciblage.cible_x, ambulance.y - strategy_evitement_et_ciblage.cible_y)
                # VITESSE X5
                v_cmd_ambu = 35.0 if dist_cible > 120.0 else 10.0
            else:
                v_cmd_ambu = 0.0
        
        commandes = {"Ambu-1": (v_cmd_ambu, omega_cmd_ambu)} 
        
        # Commandes dynamiques des robots standards
        for robot in env.robots:
            if isinstance(robot, RobotStandard):
                if not robot.en_panne:
                    # Les robots standards utilisent leur Lidar et leur stratégie d'évitement
                    mesures_std = robot.capteur.read(env)
                    cmd_std = strategy_promenade_standards.compute_command(mesures_std)
                    commandes[robot.id] = cmd_std
                else:
                    commandes[robot.id] = (0.0, 0.0)
                
        env.step(commandes, dt)
        vue.dessiner(env)
        vue.horloge.tick(60)
        
    vue.quitter()

if __name__ == "__main__":
    main()