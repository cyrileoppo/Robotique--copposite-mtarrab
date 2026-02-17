import math
from robot.robot_mobile import RobotMobile
from robot.moteur import MoteurDifferentiel, MoteurOmnidirectionnel


dt = 1.0

print("=== Robot différentiel ===")
moteur_diff = MoteurDifferentiel()
robot1 = RobotMobile(moteur=moteur_diff)

robot1.afficher()
robot1.commander(v=1.0, omega=0.5)
robot1.mettre_a_jour(dt)
robot1.afficher()

print("\n=== Robot omnidirectionnel ===")
moteur_omni = MoteurOmnidirectionnel()
robot2 = RobotMobile(moteur=moteur_omni)

robot2.afficher()
robot2.commander(vx=1.0, vy=1.0, omega=0.5)
robot2.mettre_a_jour(dt)
robot2.afficher()
