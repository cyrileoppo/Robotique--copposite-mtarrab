import math
from robot.robot_mobile import RobotMobile
from robot.moteur import MoteurDifferentiel, MoteurOmnidirectionnel

def main():
    # 1. Test du compteur de robots
    print(f"Nombre de robots au départ : {RobotMobile.nombre_robots()}")

    # 2. Création d'un robot avec moteur différentiel
    m_diff = MoteurDifferentiel()
    robot1 = RobotMobile(moteur=m_diff)
    
    print("\n--- Test Robot Différentiel ---")
    robot1.commander(v=1.0, omega=math.pi/4) # Avance et tourne
    robot1.mettre_a_jour(dt=1.0)
    print(robot1) # Utilise __str__ automatiquement

    # 3. Création d'un robot avec moteur omnidirectionnel
    m_omni = MoteurOmnidirectionnel()
    robot2 = RobotMobile(moteur=m_omni)
    
    print("\n--- Test Robot Omnidirectionnel ---")
    # Déplacement latéral pur (vx=0, vy=1)
    robot2.commander(vx=0.0, vy=1.0, omega=0.0)
    robot2.mettre_a_jour(dt=1.0)
    print(robot2)

    # 4. Vérification finale des membres statiques
    print(f"\nNombre total de robots créés : {RobotMobile.nombre_robots()}")
    
    # Test de la méthode statique
    est_valide = RobotMobile.moteur_valide(m_diff)
    print(f"Le moteur différentiel est-il valide ? {est_valide}")

if __name__ == "__main__":
    main()