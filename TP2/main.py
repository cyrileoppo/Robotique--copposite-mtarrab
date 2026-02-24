from robot.robot_mobile import RobotMobile
from robot.moteur import MoteurDifferentiel
from robot.controleur import ControleurTerminal
from robot.vue import VueTerminal

def main():
    robot = RobotMobile(moteur=MoteurDifferentiel())
    vue = VueTerminal()
    ctrl = ControleurTerminal()
    
    for _ in range(3): # Boucle de test courte (3 tours)
        v, omega = ctrl.lire_commande()
        robot.mettre_a_jour(v, omega, dt=0.5)
        vue.dessiner(robot)

if __name__ == "__main__":
    main()