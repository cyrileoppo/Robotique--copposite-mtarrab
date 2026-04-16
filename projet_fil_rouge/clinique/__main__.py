"""
__main__.py — Point d'entrée de la simulation "La Clinique des Robots".
Architecture MVC : Modèle / Vue / Contrôleur.
"""

import argparse
import logging
import math
import random

import pygame

from .config import (
    LARGEUR, HAUTEUR,
    BASE_X, BASE_Y, RAYON_ACTION,
    AMBULANCE_V_MAX, AMBULANCE_A_MAX, AMBULANCE_FROTTEMENT,
    AMBULANCE_V_CROISIERE, AMBULANCE_V_APPROCHE, AMBULANCE_DIST_CROISIERE,
    AMBULANCE_DISTANCE_SECURITE, STANDARD_DISTANCE_SECURITE,
    OBSTACLES, POIDS_ROBOTS, DT, FPS,
    RAYON_SORTIE_BASE, REPARATION_MIN_S, REPARATION_MAX_S,
)
from .logging_config import setup_logger
from .modele.environnement import Environnement
from .modele.robot import RobotStandard, RobotAmbulance
from .modele.obstacles import ObstacleCercle
from .vue.vue_pygame import VuePygame
from .controleur.strategies import GoalAndAvoidStrategy, AvoidStrategy
from .controleur.planificateur import (
    algorithme_sac_a_dos, optimiser_trajet_greedy,
)


# =====================================================================
# Utilitaires
# =====================================================================

def parse_args():
    p = argparse.ArgumentParser(
        description="Simulation de la Clinique des Robots")
    p.add_argument("--debug", action="store_true")
    p.add_argument("--nb-robots", type=int, default=5)
    return p.parse_args()


def _position_reparation(index):
    """Position distincte dans la base pour chaque robot en réparation."""
    emplacements = [
        (BASE_X - 20, BASE_Y - 20),
        (BASE_X + 20, BASE_Y - 20),
        (BASE_X - 20, BASE_Y + 20),
        (BASE_X + 20, BASE_Y + 20),
        (BASE_X, BASE_Y),
        (BASE_X - 30, BASE_Y),
        (BASE_X + 30, BASE_Y),
        (BASE_X, BASE_Y - 30),
        (BASE_X, BASE_Y + 30),
    ]
    return emplacements[index % len(emplacements)]


def _prochaine_direction_sortie():
    """Alterne les directions de sortie (gauche / bas)."""
    if not hasattr(_prochaine_direction_sortie, "toggle"):
        _prochaine_direction_sortie.toggle = 0
    direction = ("gauche"
                 if _prochaine_direction_sortie.toggle % 2 == 0
                 else "bas")
    _prochaine_direction_sortie.toggle += 1
    return direction


# =====================================================================
# Boucle principale
# =====================================================================

def main():
    args = parse_args()
    setup_logger(args.debug)
    logger = logging.getLogger("Simulation")

    # ── Initialisation du monde ───────────────────────────────────
    env = Environnement(LARGEUR, HAUTEUR)

    ambulance = RobotAmbulance("Ambu-1", x=BASE_X, y=BASE_Y)
    ambulance.moteur.v_max = AMBULANCE_V_MAX
    ambulance.moteur.a_max = AMBULANCE_A_MAX
    ambulance.moteur.frottement = AMBULANCE_FROTTEMENT
    env.ajouter_robot(ambulance)

    for cfg in OBSTACLES:
        env.ajouter_obstacle(ObstacleCercle(**cfg))

    for i in range(args.nb_robots):
        robot = RobotStandard(
            f"R-{i + 1}",
            x=100 + (i * 100) % 600,
            y=400 + (i * 50) % 150,
            poids=POIDS_ROBOTS[i % len(POIDS_ROBOTS)],
        )
        env.ajouter_robot(robot)

    # ── Stratégies et vue ─────────────────────────────────────────
    vue = VuePygame(LARGEUR, HAUTEUR)
    strat_ambu = GoalAndAvoidStrategy(
        distance_securite=AMBULANCE_DISTANCE_SECURITE)
    strat_std = AvoidStrategy(
        distance_securite=STANDARD_DISTANCE_SECURITE)

    # ── Boucle de simulation ──────────────────────────────────────
    en_cours = True
    while en_cours:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                en_cours = False

        # Pannes aléatoires
        for r in env.robots:
            if isinstance(r, RobotStandard):
                r.mettre_a_jour_etat()

        _avancer_reparations(env, logger)
        _gerer_ambulance(ambulance, env, strat_ambu, logger)

        commandes = _calculer_commandes(
            ambulance, env, strat_ambu, strat_std)
        env.step(commandes, DT)

        # Progression de la sortie de base
        for r in env.robots:
            if isinstance(r, RobotStandard) and r.en_sortie_base:
                r.dist_sortie_parcourue += AMBULANCE_V_APPROCHE * DT
                if r.dist_sortie_parcourue >= RAYON_SORTIE_BASE:
                    r.en_sortie_base = False
                    r.dist_sortie_parcourue = 0.0
                    logger.info(f"{r.id} a quitté la base.")

        vue.dessiner(env)
        vue.horloge.tick(FPS)

    vue.quitter()


# =====================================================================
# Gestion des réparations
# =====================================================================

def _avancer_reparations(env, logger):
    """Décrémente les compteurs de réparation et lance la sortie de base."""
    for r in env.robots:
        if isinstance(r, RobotStandard) and getattr(r, "en_reparation", False):
            r.temps_reparation_restant -= DT
            if r.temps_reparation_restant <= 0:
                r.en_reparation = False
                r.en_sortie_base = True
                r.dist_sortie_parcourue = 0.0
                r.direction_sortie = _prochaine_direction_sortie()

                if r.direction_sortie == "gauche":
                    r.theta = math.pi
                else:
                    r.theta = math.pi / 2

                logger.info(
                    f"{r.id} réparé, sortie {r.direction_sortie}.")


# =====================================================================
# Machine à états de l'ambulance
# =====================================================================

def _gerer_ambulance(ambulance, env, strategy, logger):
    """Cycle de l'ambulance : collecte → retour base → déploiement."""

    # ── État 1 : collecte en cours ────────────────────────────────
    if ambulance.plan_sauvetage:
        cible = ambulance.plan_sauvetage[0]
        if cible in env.robots:
            dist = math.hypot(ambulance.x - cible.x,
                              ambulance.y - cible.y)
            if dist <= RAYON_ACTION:
                ambulance.moteur.v = 0.0
                ambulance.moteur.omega = 0.0
                ambulance.robots_charges.append(cible)
                env.robots.remove(cible)
                ambulance.plan_sauvetage.pop(0)
                logger.info(
                    f"Chargé {cible.id} "
                    f"({ambulance.poids_charge}/{ambulance.capacite_max} kg)")
            else:
                strategy.set_cible(cible.x, cible.y)
        else:
            ambulance.plan_sauvetage.pop(0)

    # ── État 2 : retour à la base avec robots chargés ─────────────
    elif ambulance.robots_charges:
        strategy.set_cible(BASE_X, BASE_Y)
        dist = math.hypot(ambulance.x - BASE_X,
                          ambulance.y - BASE_Y)
        if dist <= RAYON_ACTION:
            ambulance.moteur.v = 0.0
            ambulance.moteur.omega = 0.0

            for i, r in enumerate(ambulance.robots_charges):
                r.temps_reparation_restant = random.uniform(
                    REPARATION_MIN_S, REPARATION_MAX_S)
                r.en_reparation = True
                r.en_panne = False
                r.en_sortie_base = False
                r.dist_sortie_parcourue = 0.0
                r.direction_sortie = None
                r.x, r.y = _position_reparation(i)
                env.ajouter_robot(r)

            nb = len(ambulance.robots_charges)
            logger.info(f"Base atteinte — {nb} robot(s) en réparation.")
            ambulance.robots_charges.clear()
            strategy.set_cible(None, None)

    # ── État 3 : planification ou attente ─────────────────────────
    else:
        en_panne = [
            r for r in env.robots
            if isinstance(r, RobotStandard) and r.en_panne
        ]
        if en_panne:
            selection = algorithme_sac_a_dos(
                en_panne, ambulance.capacite_max)
            ambulance.plan_sauvetage = optimiser_trajet_greedy(
                BASE_X, BASE_Y, selection)
            logger.info(
                f"Plan : {[r.id for r in ambulance.plan_sauvetage]}")
        else:
            dist = math.hypot(ambulance.x - BASE_X,
                              ambulance.y - BASE_Y)
            if dist > RAYON_ACTION:
                strategy.set_cible(BASE_X, BASE_Y)
            else:
                strategy.set_cible(None, None)
                ambulance.moteur.v = 0.0
                ambulance.moteur.omega = 0.0


# =====================================================================
# Calcul des commandes (v, omega) pour chaque robot
# =====================================================================

def _calculer_commandes(ambulance, env, strat_ambu, strat_std):
    """Retourne {robot_id: (v_cmd, omega_cmd)} pour tous les robots."""
    commandes = {}

    # ── Ambulance ─────────────────────────────────────────────────
    mesures = ambulance.capteur.read(env)
    ambulance.verifier_blocage(seuil=5.0, taille=60)

    if ambulance._bloque and strat_ambu.cible_x is not None:
        v, omega = -0.3, 2.5
        v = AMBULANCE_V_APPROCHE * v
    else:
        v, omega = strat_ambu.compute_command(
            mesures, ambulance.x, ambulance.y, ambulance.theta)
        if v == 1.0:
            if strat_ambu.cible_x is not None:
                d = math.hypot(
                    ambulance.x - strat_ambu.cible_x,
                    ambulance.y - strat_ambu.cible_y)
                v = (AMBULANCE_V_CROISIERE
                     if d > AMBULANCE_DIST_CROISIERE
                     else AMBULANCE_V_APPROCHE)
            else:
                v = 0.0
    commandes[ambulance.id] = (v, omega)

    # ── File de sortie de base (priorité au plus petit ID) ────────
    robots_sortie = sorted(
        [r for r in env.robots
         if isinstance(r, RobotStandard) and r.en_sortie_base],
        key=lambda r: r.id,
    )
    robot_prioritaire_id = (
        robots_sortie[0].id if robots_sortie else None)

    # ── Robots standards ──────────────────────────────────────────
    for r in env.robots:
        if not isinstance(r, RobotStandard):
            continue

        if getattr(r, "en_reparation", False):
            commandes[r.id] = (0.0, 0.0)

        elif r.en_sortie_base:
            if r.id == robot_prioritaire_id:
                direction = getattr(r, "direction_sortie", "gauche")
                r.theta = (math.pi if direction == "gauche"
                           else math.pi / 2)
                commandes[r.id] = (AMBULANCE_V_APPROCHE, 0.0)
            else:
                commandes[r.id] = (0.0, 0.0)

        elif not r.en_panne:
            mesures = r.capteur.read(env)
            r.verifier_blocage()
            if r._bloque:
                commandes[r.id] = strat_std.compute_escape(mesures)
            else:
                commandes[r.id] = strat_std.compute_command(mesures)
        else:
            commandes[r.id] = (0.0, 0.0)

    return commandes


if __name__ == "__main__":
    main()
