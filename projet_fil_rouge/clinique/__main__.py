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
    """Gère les arguments en ligne de commande."""
    parser = argparse.ArgumentParser(description="Simulation de la Clinique des Robots")
    parser.add_argument("--debug", action="store_true", help="Active les logs de niveau DEBUG")
    parser.add_argument("--nb-robots", type=int, default=4, help="Nombre de robots standards")
    return parser.parse_args()

def algorithme_sac_a_dos(robots_en_panne, capacite_max):
    """
    Algorithme de programmation dynamique pour le problème du Sac à Dos.
    Objectif : Maximiser le nombre de robots sauvés sans dépasser la capacité max.
    """
    n = len(robots_en_panne)
    # Matrice DP : dp[i][w] stocke le maximum de robots qu'on peut sauver
    dp = [[0] * (capacite_max + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        poids = robots_en_panne[i-1].poids
        for w in range(capacite_max + 1):
            if poids <= w:
                # On choisit le max entre "ne pas prendre ce robot" et "prendre ce robot"
                dp[i][w] = max(dp[i-1][w], dp[i-1][w-poids] + 1)
            else:
                dp[i][w] = dp[i-1][w]

    # Backtracking pour retrouver exactement quels robots ont été sélectionnés
    selection = []
    w = capacite_max
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            selection.append(robots_en_panne[i-1])
            w -= robots_en_panne[i-1].poids
            
    return selection

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
    
    # Nouvelles propriétés pour gérer plusieurs robots
    ambulance.capacite_max = 50
    ambulance.robots_charges = []
    ambulance.plan_sauvetage = []
    
    env.ajouter_robot(ambulance)
    
    env.ajouter_obstacle(ObstacleCercle(x=400, y=150, rayon=50))
    env.ajouter_obstacle(ObstacleCercle(x=600, y=300, rayon=80))
    env.ajouter_obstacle(ObstacleCercle(x=300, y=400, rayon=60))
    
    # Création des robots avec des poids différents pour tester le sac à dos
    poids_test = [15, 20, 30, 25, 10]
    for i in range(args.nb_robots):
        poids = poids_test[i % len(poids_test)]
        robot = RobotStandard(f"R-{i+1}", x=100 + i*150, y=500, poids=poids)
        # Probabilité augmentée pour avoir plusieurs pannes en même temps
        robot.probabilite_panne = 0.0005 
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
                
        # b) Machine à états avec Sac à Dos
        charge_actuelle = sum(r.poids for r in ambulance.robots_charges)

        # SI l'ambulance a un plan de sauvetage en cours...
        if ambulance.plan_sauvetage:
            cible = ambulance.plan_sauvetage[0]
            
            # Vérification de sécurité (au cas où la cible aurait un bug)
            if cible in env.robots:
                dist_robot = math.hypot(ambulance.x - cible.x, ambulance.y - cible.y)
                
                if dist_robot < 30.0: 
                    # On charge le robot !
                    ambulance.robots_charges.append(cible)
                    env.robots.remove(cible)
                    ambulance.plan_sauvetage.pop(0) # On le retire de la liste des courses
                    logger.info(f"Chargement de {cible.id} ({cible.poids} kg). Charge: {charge_actuelle + cible.poids}/{ambulance.capacite_max}")
                else:
                    strategy_evitement_et_ciblage.set_cible(cible.x, cible.y)
            else:
                ambulance.plan_sauvetage.pop(0)

        # SI l'ambulance n'a pas (ou plus) de plan...
        else:
            if ambulance.robots_charges:
                # Elle est pleine ou a fini sa liste, elle rentre !
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
                # Elle est vide et à la base, elle analyse la carte
                robots_en_panne = [r for r in env.robots if isinstance(r, RobotStandard) and r.en_panne]
                
                if robots_en_panne:
                    # LE SAC À DOS EN ACTION
                    selection = algorithme_sac_a_dos(robots_en_panne, ambulance.capacite_max)
                    ambulance.plan_sauvetage = selection
                    
                    ids_selectionnes = [r.id for r in selection]
                    poids_total = sum(r.poids for r in selection)
                    logger.info(f"Nouvelle mission ! Le sac à dos a sélectionné : {ids_selectionnes} (Total: {poids_total} kg)")
                else:
                    # Rien à faire, attente à la base
                    dist_base = math.hypot(ambulance.x - BASE_X, ambulance.y - BASE_Y)
                    if dist_base > 20.0:
                        strategy_evitement_et_ciblage.set_cible(BASE_X, BASE_Y)
                    else:
                        strategy_evitement_et_ciblage.set_cible(None, None)

        # c) Lecture des capteurs et Stratégie
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