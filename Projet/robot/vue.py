import pygame
import math


class VuePygame:
    def __init__(self, largeur=1000, hauteur=700, scale=35):
        pygame.init()
        self.screen = pygame.display.set_mode((largeur, hauteur))
        pygame.display.set_caption("La Clinique des Robots")
        self.largeur = largeur
        self.hauteur = hauteur
        self.scale = scale
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 22)

    def ajuster_echelle_auto(self, environnement, marge_px=40):
        xs = [environnement.base_x]
        ys = [environnement.base_y]

        for r in environnement.robots_standards + [environnement.ambulance]:
            xs.append(r.x)
            ys.append(r.y)

        for o in environnement.obstacles:
            xs.extend([o.x - o.rayon, o.x + o.rayon])
            ys.extend([o.y - o.rayon, o.y + o.rayon])

        max_abs_x = max(abs(x) for x in xs) if xs else 1.0
        max_abs_y = max(abs(y) for y in ys) if ys else 1.0

        scale_x = (self.largeur / 2 - marge_px) / max(1e-6, max_abs_x)
        scale_y = (self.hauteur / 2 - marge_px) / max(1e-6, max_abs_y)

        self.scale = max(15, min(scale_x, scale_y))

    def convertir_coordonnees(self, x, y):
        px = int(self.largeur / 2 + (x * self.scale))
        py = int(self.hauteur / 2 - (y * self.scale))
        return px, py

    def _dessiner_robot(self, x, y, orientation, rayon, couleur):
        px, py = self.convertir_coordonnees(x, y)
        r_pixels = max(3, int(rayon * self.scale))

        pygame.draw.circle(self.screen, couleur, (px, py), r_pixels)

        x_dir = px + int(r_pixels * math.cos(orientation))
        y_dir = py - int(r_pixels * math.sin(orientation))
        pygame.draw.line(self.screen, (0, 0, 0), (px, py), (x_dir, y_dir), 2)

    def dessiner_environnement(self, environnement):
        self.ajuster_echelle_auto(environnement)
        self.screen.fill((240, 240, 240))

        # Base
        base_px, base_py = self.convertir_coordonnees(environnement.base_x, environnement.base_y)
        taille_base = max(12, int(1.4 * self.scale))
        pygame.draw.rect(
            self.screen,
            (100, 150, 255),
            (base_px - taille_base // 2, base_py - taille_base // 2, taille_base, taille_base),
        )

        # Obstacles
        for obs in environnement.obstacles:
            px, py = self.convertir_coordonnees(obs.x, obs.y)
            r_pixels = max(3, int(obs.rayon * self.scale))
            pygame.draw.circle(self.screen, (80, 80, 80), (px, py), r_pixels)

        # Robots standards
        for robot in environnement.robots_standards:
            if robot.en_reparation:
                couleur = (80, 80, 255)       # bleu = en réparation
            elif robot.en_panne:
                couleur = (255, 165, 0)       # orange = panne
            else:
                couleur = (50, 200, 50)       # vert = OK
            self._dessiner_robot(robot.x, robot.y, robot.orientation, robot.rayon, couleur)

        # Ambulance
        amb = environnement.ambulance
        self._dessiner_robot(amb.x, amb.y, amb.orientation, amb.rayon, (220, 20, 20))

        # Légende
        txt = self.font.render("Vert=OK  Orange=Panne  Bleu=Réparation  Rouge=Ambulance", True, (20, 20, 20))
        self.screen.blit(txt, (10, 10))

        pygame.display.flip()

    def tick(self, fps=60):
        self.clock.tick(fps)