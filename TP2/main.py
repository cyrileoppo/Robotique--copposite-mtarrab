from robot.robot_mobile import RobotMobile
from robot.moteur import MoteurDifferentiel
from robot.controleur import ControleurTerminal
from robot.vue import VuePygame

def main():
    robot = RobotMobile(moteur=MoteurDifferentiel())
    vue = VuePygame()
    ctrl = ControleurTerminal()
    
    while True:
        v, omega = ctrl.lire_commande() # Bloque en attendant l'entrée terminal
        robot.mettre_a_jour(v, omega, dt=0.5)
        vue.dessiner(robot)

if __name__ == "__main__":
    main()