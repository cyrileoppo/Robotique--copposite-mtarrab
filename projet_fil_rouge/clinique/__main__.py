import argparse
import logging
from .logging_config import setup_logger
from .modele.environnement import Environnement
from .modele.robot import RobotStandard, RobotAmbulance

def parse_args():
    parser = argparse.ArgumentParser(description="Simulation de la Clinique des Robots")
    parser.add_argument("--debug", action="store_true", help="Active les logs de niveau DEBUG")
    # Argument optionnel pour le nombre de robots
    parser.add_argument("--nb-robots", type=int, default=3, help="Nombre de robots standards")
    return parser.parse_args()

def main():
    args = parse_args()
    setup_logger(args.debug)
    logger = logging.getLogger("Simulation")
    
    # 1. Création du Modèle
    env = Environnement(largeur=800, hauteur=600)
    
    # Ajout de l'ambulance et d'un robot standard
    ambulance = RobotAmbulance("Ambu-1", x=100, y=100)
    robot1 = RobotStandard("R-1", x=200, y=200, poids=20)
    
    env.ajouter_robot(ambulance)
    env.ajouter_robot(robot1)
    
    # 2. Petite boucle de test (Contrôleur fictif)
    logger.info("Début de la simulation (10 itérations)")
    dt = 0.1
    
    for i in range(10):
        # On demande à l'ambulance d'avancer tout droit, le robot 1 reste sur place
        commandes = {"Ambu-1": (1.0, 0.0)} 
        env.step(commandes, dt)
        
        logger.debug(f"Itération {i+1} | Ambu-1 Pos: ({ambulance.x:.2f}, {ambulance.y:.2f}) - Vitesse: {ambulance.moteur.v:.2f}")

if __name__ == "__main__":
    main()