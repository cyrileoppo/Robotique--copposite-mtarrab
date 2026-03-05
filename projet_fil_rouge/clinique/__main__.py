import argparse
import logging
import pygame

from .logging_config import setup_logger
from .modele.environnement import Environnement
from .modele.robot import RobotStandard, RobotAmbulance
from .modele.obstacles import ObstacleCercle
from .vue.vue_pygame import VuePygame
from .controleur.strategies import Navigator, AvoidStrategy

def parse_args():
    """Gère les arguments en ligne de commande [cite: 35-46]."""
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
    
    # Ajout de l'ambulance (orientée vers le premier obstacle)
    ambulance = RobotAmbulance("Ambu-1", x=100, y=150)
    env.ajouter_robot(ambulance)
    
    # Ajout des obstacles fixes
    env.ajouter_obstacle(ObstacleCercle(x=400, y=150, rayon=50))
    env.ajouter_obstacle(ObstacleCercle(x=600, y=300, rayon=80))
    
    # Ajout des robots standards
    for i in range(args.nb_robots):
        # On les place en bas de l'écran pour l'instant
        robot = RobotStandard(f"R-{i+1}", x=100 + i*150, y=500, poids=20)
        env.ajouter_robot(robot)
        
    # ==========================================
    # 2. VUE (Affichage graphique)
    # ==========================================
    vue = VuePygame(largeur, hauteur)
    
    # ==========================================
    # 3. CONTRÔLEUR (Intelligence et Navigation)
    # ==========================================
    # Création de la stratégie d'évitement directionnel [cite: 770-773, 791-792]
    strategy_evitement = AvoidStrategy(distance_securite=50.0)
    
    # Le Navigator utilise la stratégie de manière transparente [cite: 740-753, 793-795]
    navigator = Navigator(strategy_evitement)
    
    en_cours = True
    dt = 0.1
    
    logger.info("Démarrage de la boucle graphique.")
    
    # Boucle principale de simulation [cite: 801-805]
    while en_cours:
        # a) Gestion des événements utilisateur (fermer la fenêtre)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                en_cours = False
                
        # b) Lecture des capteurs pour l'ambulance [cite: 802-803]
        mesures = ambulance.capteur.read(env)
        
        # c) Décision du Contrôleur (Navigation réactive) [cite: 804]
        if mesures:
            cmd_ambu = navigator.step(mesures)
        else:
            # S'il n'y a pas de mesures, on avance tout droit par défaut
            cmd_ambu = (1.0, 0.0)
            
        # Préparation des commandes pour tous les robots
        commandes = {"Ambu-1": cmd_ambu} 
        for i in range(args.nb_robots):
            commandes[f"R-{i+1}"] = (0.0, 0.0) # Les standards restent immobiles pour le moment
            
        # d) Mise à jour du Modèle (Application de la physique) [cite: 805]
        env.step(commandes, dt)
        
        # e) Mise à jour de la Vue (Dessin) [cite: 468]
        vue.dessiner(env)
        
        # f) Limiter la vitesse de la boucle (ex: 60 FPS)
        vue.horloge.tick(60)
        
    vue.quitter()
    logger.info("Fin de la simulation.")

if __name__ == "__main__":
    main()