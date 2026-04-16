"""vue_pygame.py — Rendu graphique Pygame (respecte le MVC)."""
import pygame
import math


class VuePygame:
    """Affiche l'environnement : robots, obstacles, base et capteurs."""

    # ── Palette de couleurs ────────────────────────────────────────
    FOND        = (240, 240, 240)
    AMBULANCE   = (200,  50,  50)
    STANDARD    = ( 50, 150, 200)
    PANNE       = (100, 100, 100)
    SORTIE      = (255, 165,   0)
    REPARATION  = (180,   0, 180)
    DIRECTION   = (  0,   0,   0)
    OBS         = ( 80,  80,  80)
    LIDAR       = (  0, 200,   0)
    BASE        = ( 50, 200,  50)
    TEXTE       = (255, 255, 255)
    TEXTE_AMBU  = (255, 230,   0)

    R = 15

    def __init__(self, largeur, hauteur):
        pygame.init()
        self.ecran = pygame.display.set_mode((largeur, hauteur))
        pygame.display.set_caption("La Clinique des Robots")
        self.horloge = pygame.time.Clock()
        self.f_petit = pygame.font.SysFont("Arial", 10, bold=True)
        self.f_moyen = pygame.font.SysFont("Arial", 13, bold=True)

    # ── Dessin principal ──────────────────────────────────────────

    def dessiner(self, env):
        self.ecran.fill(self.FOND)

        for obs in env.obstacles:
            pygame.draw.circle(
                self.ecran, self.OBS,
                (int(obs.x), int(obs.y)), obs.rayon)

        pygame.draw.rect(
            self.ecran, self.BASE,
            (650, 50, 100, 100), border_radius=10)
        self.ecran.blit(
            self.f_moyen.render("BASE", True, self.TEXTE), (685, 92))

        for robot in env.robots:
            self._dessiner_robot(robot)

        pygame.display.flip()

    # ── Dessin d'un robot ─────────────────────────────────────────

    def _dessiner_robot(self, robot):
        x, y = int(robot.x), int(robot.y)
        r = self.R

        # Couleur selon l'état du robot
        if getattr(robot, "en_reparation", False):
            couleur = self.REPARATION
        elif getattr(robot, "en_sortie_base", False):
            couleur = self.SORTIE
        elif robot.en_panne:
            couleur = self.PANNE
        elif robot.type_robot == "ambulance":
            couleur = self.AMBULANCE
        else:
            couleur = self.STANDARD

        pygame.draw.circle(self.ecran, couleur, (x, y), r)

        # Trait d'orientation
        fx = x + int(math.cos(robot.theta) * r * 1.5)
        fy = y + int(math.sin(robot.theta) * r * 1.5)
        pygame.draw.line(self.ecran, self.DIRECTION, (x, y), (fx, fy), 3)

        # Rayons Lidar
        if hasattr(robot, "capteur"):
            for angle, dist in getattr(
                    robot.capteur, "dernieres_mesures", []):
                pygame.draw.line(
                    self.ecran, self.LIDAR, (x, y),
                    (int(robot.x + math.cos(angle) * dist),
                     int(robot.y + math.sin(angle) * dist)), 1)

        # Poids du robot
        label = self.f_petit.render(
            f"{robot.poids}kg", True, self.TEXTE)
        self.ecran.blit(label, (x - label.get_width() // 2, y - 6))

        # Infos spécifiques ambulance
        if robot.type_robot == "ambulance":
            charge = getattr(robot, "poids_charge", 0)
            cap = getattr(robot, "capacite_max", "?")
            total = getattr(robot, "poids_total", robot.poids)
            l1 = self.f_moyen.render(
                f"charge {charge}/{cap}kg", True, self.TEXTE_AMBU)
            l2 = self.f_petit.render(
                f"total {total}kg", True, self.TEXTE_AMBU)
            self.ecran.blit(l1, (x - l1.get_width() // 2, y - r - 30))
            self.ecran.blit(l2, (x - l2.get_width() // 2, y - r - 16))

        # Indicateur de panne
        if robot.en_panne:
            lbl = self.f_petit.render("PANNE", True, (255, 50, 50))
            self.ecran.blit(
                lbl, (x - lbl.get_width() // 2, y + r + 2))

        # Indicateur de réparation
        if getattr(robot, "en_reparation", False):
            t = getattr(robot, "temps_reparation_restant", 0)
            lbl = self.f_petit.render(
                f"rep. {t:.0f}s", True, (255, 50, 255))
            self.ecran.blit(
                lbl, (x - lbl.get_width() // 2, y + r + 2))

    def quitter(self):
        pygame.quit()

