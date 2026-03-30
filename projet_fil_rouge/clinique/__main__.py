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
from .controleur.planificateur import algorithme_sac_a_dos, optimiser_trajet_greedy


def parse_args():
    p = argparse.ArgumentParser(description="Simulation de la Clinique des Robots")
    p.add_argument("--debug", action="store_true")
    p.add_argument("--nb-robots", type=int, default=5)
    return p.parse_args()


def main():
    args = parse_args()
    setup_logger(args.debug)
    logger = logging.getLogger("Simulation")

    # --- Environnement ---
    env = Environnement(LARGEUR, HAUTEUR)

    # --- Ambulance (poids propre 100 kg, capacité 75 kg) ---
    ambulance = RobotAmbulance("Ambu-1", x=BASE_X, y=BASE_Y)
    ambulance.moteur.v_max = AMBULANCE_V_MAX
    ambulance.moteur.a_max = AMBULANCE_A_MAX
    ambulance.moteur.frottement = AMBULANCE_FROTTEMENT
    env.ajouter_robot(ambulance)

    # --- Obstacles fixes ---
    for cfg in OBSTACLES:
        env.ajouter_obstacle(ObstacleCercle(**cfg))

    # --- Robots standards (direction initiale aléatoire via RobotMobile.__init__) ---
    for i in range(args.nb_robots):
        robot = RobotStandard(
            f"R-{i + 1}",
            x=100 + (i * 100) % 600,
            y=400 + (i * 50) % 150,
            poids=POIDS_ROBOTS[i % len(POIDS_ROBOTS)],
        )
        env.ajouter_robot(robot)

    vue = VuePygame(LARGEUR, HAUTEUR)
    strat_ambu = GoalAndAvoidStrategy(distance_securite=AMBULANCE_DISTANCE_SECURITE)
    strat_std  = AvoidStrategy(distance_securite=STANDARD_DISTANCE_SECURITE)

    en_cours = True
    while en_cours:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                en_cours = False

        # Pannes aléatoires
        for r in env.robots:
            if isinstance(r, RobotStandard):
                r.mettre_a_jour_etat()

        # Décompte des réparations en cours
        _avancer_reparations(env, logger)

        # Logique ambulance
        _gerer_ambulance(ambulance, env, strat_ambu, logger)

        # Calcul des commandes
        commandes = _calculer_commandes(ambulance, env, strat_ambu, strat_std)

        env.step(commandes, DT)

        # Avancement de la sortie de base
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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _avancer_reparations(env, logger):
    """Décrémente le compteur de réparation des robots en attente à la base."""
    for r in env.robots:
        if isinstance(r, RobotStandard) and getattr(r, "en_reparation", False):
            r.temps_reparation_restant -= DT
            if r.temps_reparation_restant <= 0:
                r.en_reparation = False
                r.en_sortie_base = True
                r.dist_sortie_parcourue = 0.0
                r.theta = random.uniform(-math.pi, math.pi)  # direction aléatoire
                logger.info(f"{r.id} réparé, déploiement en cours.")


def _gerer_ambulance(ambulance, env, strategy, logger):
    """Gère le cycle complet de l'ambulance : collecte → base → déploiement."""

    if ambulance.plan_sauvetage:
        cible = ambulance.plan_sauvetage[0]
        if cible in env.robots:
            if math.hypot(ambulance.x - cible.x, ambulance.y - cible.y) <= RAYON_ACTION:
                ambulance.moteur.v = ambulance.moteur.omega = 0.0
                ambulance.robots_charges.append(cible)
                env.robots.remove(cible)
                ambulance.plan_sauvetage.pop(0)
                logger.info(f"Chargé {cible.id} — charge {ambulance.poids_charge}/{ambulance.capacite_max} kg")
            else:
                strategy.set_cible(cible.x, cible.y)
        else:
            ambulance.plan_sauvetage.pop(0)

    elif ambulance.robots_charges:
        strategy.set_cible(BASE_X, BASE_Y)
        if math.hypot(ambulance.x - BASE_X, ambulance.y - BASE_Y) <= RAYON_ACTION:
            ambulance.moteur.v = ambulance.moteur.omega = 0.0
            for r in ambulance.robots_charges:
                # Délai de réparation aléatoire
                r.temps_reparation_restant = random.uniform(REPARATION_MIN_S, REPARATION_MAX_S)
                r.en_reparation = True
                r.en_panne = False
                r.x, r.y = BASE_X, BASE_Y
                env.ajouter_robot(r)
            logger.info(f"Base atteinte — {len(ambulance.robots_charges)} robot(s) en réparation.")
            ambulance.robots_charges.clear()
            strategy.set_cible(None, None)

    else:
        en_panne = [r for r in env.robots if isinstance(r, RobotStandard) and r.en_panne]
        if en_panne:
            selection = algorithme_sac_a_dos(en_panne, ambulance.capacite_max)
            ambulance.plan_sauvetage = optimiser_trajet_greedy(BASE_X, BASE_Y, selection)
            logger.info(f"Plan : {[r.id for r in ambulance.plan_sauvetage]}")
        else:
            if math.hypot(ambulance.x - BASE_X, ambulance.y - BASE_Y) > RAYON_ACTION:
                strategy.set_cible(BASE_X, BASE_Y)
            else:
                strategy.set_cible(None, None)
                ambulance.moteur.v = ambulance.moteur.omega = 0.0


def _calculer_commandes(ambulance, env, strat_ambu, strat_std):
    """Retourne le dictionnaire {robot_id: (v_cmd, omega_cmd)} pour tous les robots."""
    commandes = {}

    # Ambulance
    mesures = ambulance.capteur.read(env)
    v, omega = strat_ambu.compute_command(mesures, ambulance.x, ambulance.y, ambulance.theta)
    if v == 1.0:
        if strat_ambu.cible_x is not None:
            d = math.hypot(ambulance.x - strat_ambu.cible_x, ambulance.y - strat_ambu.cible_y)
            v = AMBULANCE_V_CROISIERE if d > AMBULANCE_DIST_CROISIERE else AMBULANCE_V_APPROCHE
        else:
            v = 0.0
    commandes[ambulance.id] = (v, omega)

    # Robots standards
    for r in env.robots:
        if not isinstance(r, RobotStandard):
            continue
        if getattr(r, "en_reparation", False):
            commandes[r.id] = (0.0, 0.0)
        elif r.en_sortie_base:
            commandes[r.id] = (AMBULANCE_V_APPROCHE, 0.0)
        elif not r.en_panne:
            commandes[r.id] = strat_std.compute_command(r.capteur.read(env))
        else:
            commandes[r.id] = (0.0, 0.0)

    return commandes


if __name__ == "__main__":
    main()
