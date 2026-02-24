class VueTerminal:
    def dessiner(self, robot):
        print(f"[Vue] Robot position : x={robot.x:.2f}, y={robot.y:.2f}, orientation={robot.orientation:.2f} rad")