import pygame
from robot.moteur import MoteurDifferentiel
from robot.robot_mobile import RobotStandard, RobotAmbulance
from robot.environnement import Environnement
from robot.obstacle import ObstacleCirculaire
from robot.vue import VuePygame
from robot.controleur import ControleurAutonome


def main():
    # 1) Modèle
    ambulance = RobotAmbulance(x=0.0, y=0.0, capacite_max=50.0, moteur=MoteurDifferentiel())
    env = Environnement(ambulance=ambulance, base_x=0.0, base_y=0.0)

    # Robots (orientations variées pour qu'ils se dispersent dès le départ)
    r1 = RobotStandard(x=7.0, y=6.0, poids=20.0, moteur=MoteurDifferentiel())
    r2 = RobotStandard(x=-8.0, y=4.0, poids=35.0, moteur=MoteurDifferentiel())
    r3 = RobotStandard(x=5.0, y=-5.0, poids=15.0, moteur=MoteurDifferentiel())
    r4 = RobotStandard(x=-6.0, y=-7.0, poids=25.0, moteur=MoteurDifferentiel())

    r1.orientation = 0.4
    r2.orientation = 2.2
    r3.orientation = -0.8
    r4.orientation = 1.4

    env.ajouter_robot(r1)
    env.ajouter_robot(r2)
    env.ajouter_robot(r3)
    env.ajouter_robot(r4)

    env.ajouter_obstacle(ObstacleCirculaire(x=3.0, y=3.0, rayon=1.2))
    env.ajouter_obstacle(ObstacleCirculaire(x=-4.0, y=-3.0, rayon=1.6))
    env.ajouter_obstacle(ObstacleCirculaire(x=-2.0, y=5.0, rayon=0.9))

    # 2) Vue
    vue = VuePygame(largeur=1000, hauteur=700, scale=35)

    # 3) Contrôleur
    controleur = ControleurAutonome(environnement=env)

    dt = 0.1
    running = True

    print("Simulation lancée : La Clinique des Robots")
    print("Fermez la fenêtre pour quitter.")

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        controleur.mettre_a_jour_commandes()
        env.mettre_a_jour(dt)
        vue.dessiner_environnement(env)
        vue.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()