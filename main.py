from robot.robot_mobile import RobotMobile
from robot.moteur import MoteurDifferentiel, MoteurOmnidirectionnel

moteur_diff = MoteurDifferentiel()
est_valide = RobotMobile.moteur_valide(moteur_diff)
print(f"Le moteur est-il valide ? {est_valide}")

print(f"Nombre de robots au début : {RobotMobile.nombre_robots()}")

robot1 = RobotMobile(moteur=moteur_diff)
robot2 = RobotMobile(moteur=MoteurOmnidirectionnel())

print(f"Nombre de robots après créations : {RobotMobile.nombre_robots()}")

dt = 1.0
print("\n--- Test Robot 1 ---")
robot1.afficher()
robot1.commander(v=1.0, omega=0.5)
robot1.mettre_a_jour(dt)
robot1.afficher()