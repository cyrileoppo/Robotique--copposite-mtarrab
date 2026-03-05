import argparse
import logging
import pygame
from .logging_config import setup_logger
from .modele.environnement import Environnement
from .modele.robot import RobotStandard, RobotAmbulance
from .vue.vue_pygame import VuePygame

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
    
    # 1. Modèle
    env = Environnement(largeur, hauteur)
    ambulance = RobotAmbulance("Ambu-1", x=400, y=300)
    env.ajouter_robot(ambulance)
    
    # Ajouter des robots standards
    for i in range(args.nb_robots):
        robot = RobotStandard(f"R-{i+1}", x=100 + i*150, y=100, poids=20)
        env.ajouter_robot(robot)
        
    # 2. Vue
    vue = VuePygame(largeur, hauteur)
    
    # 3. Contrôleur (Boucle principale) 
    en_cours = True
    dt = 0.1
    
    logger.info("Démarrage de la boucle graphique.")
    
    while en_cours:
        # a) Gestion des événements (fermer la fenêtre)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                en_cours = False
                
        # Commandes basiques pour tester que ça bouge
        commandes = {"Ambu-1": (1.0, 0.2)} # Vitesse 1.0, rotation lente
        for i in range(args.nb_robots):
            commandes[f"R-{i+1}"] = (0.5, 0.0) # Les standards avancent tout droit
            
        # b) Mise à jour du Modèle
        env.step(commandes, dt)
        
        # c) Mise à jour de la Vue
        vue.dessiner(env)
        
        # d) Limiter les FPS (ex: 60 images par seconde)
        vue.horloge.tick(60)
        
    vue.quitter()
    logger.info("Fin de la simulation.")

if __name__ == "__main__":
    main()