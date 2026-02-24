import pygame
from robot.robot_mobile import RobotMobile
from robot.moteur import MoteurDifferentiel
from robot.controleur import ControleurClavierPygame
from robot.vue import VuePygame
from robot.environnement import Environnement, ObstacleCirculaire

def main():
    robot = RobotMobile(moteur=MoteurDifferentiel())
    env = Environnement(robot)
    env.ajouter_obstacle(ObstacleCirculaire(2, 2, 0.5))
    env.ajouter_obstacle(ObstacleCirculaire(-3, 1, 0.8))
    
    vue = VuePygame()
    ctrl = ControleurClavierPygame()
    running, dt = True, 0.05
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
                
        v, omega = ctrl.lire_commande()
        env.mettre_a_jour(v, omega, dt) # Le modèle passe par l'environnement
        
        vue.dessiner(robot, env.obstacles)
        vue.tick()
        
    pygame.quit()

if __name__ == "__main__":
    main()