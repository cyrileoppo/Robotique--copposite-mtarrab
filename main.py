import math
from robot.robot_mobile import RobotMobile

robot = RobotMobile(0.0, 0.0, 0.0)
robot.avancer(1.0) 
angle_rad = math.radians(45)
robot.tourner(angle_rad)
robot.avancer(3.0)
print("État final du robot :")
robot.afficher()

"""
------- RÉSULTAT FINAL -------
État final du robot :
(x=3.12, y=2.12, orientation=0.79)
-------------------------------
"""