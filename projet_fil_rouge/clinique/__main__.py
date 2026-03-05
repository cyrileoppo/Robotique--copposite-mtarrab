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
from .controleur.strategies import Navigator, GoalAndAvoidStrategy

def parse_args():
    """Gère les arguments en ligne de commande [cite: 35-46]."""
    parser = argparse.ArgumentParser(description="Simulation de la Clinique des Robots")
    parser.add_argument("--debug", action="store_true", help="Active les logs de niveau DEBUG")
    parser.add_argument("--nb-robots", type=int, default=4, help="Nombre de robots standards")
    return parser.parse_args()

def algorithme_sac_a_dos(robots_en_panne, capacite_max):
    """Algorithme de programmation dynamique pour le problème du Sac à Dos."""
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
    """
    Algorithme du Voyageur de Commerce (Brute-force pour petit N).
    Trouve l'ordre de visite qui minimise la distance: Base -> R1 -> R2 -> ... -> Base.
    """
    if not robots_selectionnes:
        return []

    meilleur_trajet = None
    distance_min = float('inf')

    # On teste toutes les combinaisons possibles d'ordre de visite
    for permutation in itertools.permutations(robots_selectionnes):
        dist_totale = 0.0
        pos_actuelle = (base_x, base_y)

        # Calcul de la distance pour cette permutation 
        for robot in permutation:
            dist_totale += math.hypot(robot.x - pos_actuelle[0], robot.y - pos_actuelle[1])
            pos_actuelle = (robot.x, robot.y)
            
        # Ajout du retour à la base
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
    
    # ==========================================
    # 1. MODÈLE
    # ==========================================
    env = Environnement(largeur, hauteur)
    
    ambulance = RobotAmbulance("Ambu-1", x=BASE_X, y=BASE_Y)
    ambulance.moteur.v_max = 5.0
    ambulance.moteur.a_max = 1.5
    ambulance.moteur.frottement = 0.05
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
        robot = RobotStandard(f"R-{i+1}", x=100 + i*150, y=500, poids=poids)
        robot.probabilite_panne = 0.005 
        env.ajouter_robot(robot)
        
    # ==========================================
    # 2. VUE
    # ==========================================
    vue = VuePygame(largeur, hauteur)
    
    # ==========================================
    # 3. CONTRÔLEUR
    # ==========================================
    strategy_evitement_et_ciblage = GoalAndAvoidStrategy(distance_securite=70.0)
    
    en_cours = True
    dt = 0.1
    
    while en_cours:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                en_cours = False
                
        # a) Pannes aléatoires
        for robot in env.robots:
            if isinstance(robot, RobotStandard):
                robot.mettre_a_jour_etat()
                
        # b) Machine à états de l'ambulance
        charge_actuelle = sum(r.poids for r in ambulance.robots_charges)

        if ambulance.plan_sauvetage:
            cible = ambulance.plan_sauvetage[0]
            if cible in env.robots:
                dist_robot = math.hypot(ambulance.x - cible.x, ambulance.y - cible.y)
                if dist_robot < 30.0: 
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
                if dist_base < 30.0:
                    for repare in ambulance.robots_charges:
                        repare.en_panne = False
                        repare.x, repare.y = BASE_X, BASE_Y + 120
                        env.ajouter_robot(repare)
                    logger.info(f"Base atteinte ! {len(ambulance.robots_charges)} robot(s) réparé(s).")
                    ambulance.robots_charges.clear()
            else:
                robots_en_panne = [r for r in env.robots if isinstance(r, RobotStandard) and r.en_panne]
                if robots_en_panne:
                    # 1. Sélection (Sac à dos)
                    selection = algorithme_sac_a_dos(robots_en_panne, ambulance.capacite_max)
                    # 2. Optimisation du trajet (TSP)
                    ambulance.plan_sauvetage = optimiser_trajet_tsp(BASE_X, BASE_Y, selection)
                    
                    ids_selectionnes = [r.id for r in ambulance.plan_sauvetage]
                    logger.info(f"Mission optiisée (TSP) ! Ordre de ramassage : {ids_selectionnes}")
                else:
                    dist_base = math.hypot(ambulance.x - BASE_X, ambulance.y - BASE_Y)
                    if dist_base > 20.0:
                        strategy_evitement_et_ciblage.set_cible(BASE_X, BASE_Y)
                    else:
                        strategy_evitement_et_ciblage.set_cible(None, None)

        # c) Lecture des capteurs et Stratégie [cite: 746-753, 804]
        mesures = ambulance.capteur.read(env)
        v_cmd, omega_cmd = strategy_evitement_et_ciblage.compute_command(mesures, ambulance.x, ambulance.y, ambulance.theta)
        if v_cmd > 0: v_cmd = 4.0 
        
        commandes = {"Ambu-1": (v_cmd, omega_cmd)} 
        for robot in env.robots:
            if isinstance(robot, RobotStandard):
                commandes[robot.id] = (0.5, 0.02) if not robot.en_panne else (0.0, 0.0)
                
        # d) Application et Affichage
        env.step(commandes, dt)
        vue.dessiner(env)
        vue.horloge.tick(60)
        
    vue.quitter()

if __name__ == "__main__":
    main()