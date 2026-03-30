"""Tests unitaires pour les stratégies de navigation."""
import sys
import os
import math
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from projet_fil_rouge.clinique.controleur.strategies import AvoidStrategy, GoalAndAvoidStrategy


class TestAvoidStrategy:

    def test_voie_libre_avance(self):
        """Sans obstacle proche, le robot doit avancer tout droit."""
        strat = AvoidStrategy(distance_securite=40.0)
        v, omega = strat.compute_command([100, 100, 100])
        assert v > 0
        assert omega == 0.0

    def test_obstacle_devant_ralentit(self):
        """Un obstacle devant doit faire ralentir et tourner."""
        strat = AvoidStrategy(distance_securite=40.0)
        v, omega = strat.compute_command([100, 20, 100])  # obstacle centre
        assert v < 1.0
        assert omega != 0.0

    def test_tourne_vers_espace_libre(self):
        """Si gauche est bloquée, on doit tourner à droite (omega > 0)."""
        strat = AvoidStrategy(distance_securite=40.0)
        v, omega = strat.compute_command([10, 100, 100])  # obstacle gauche
        assert omega > 0  # tourne à droite

    def test_tourne_vers_gauche_si_droite_bloquee(self):
        """Si droite est bloquée, on doit tourner à gauche (omega < 0)."""
        strat = AvoidStrategy(distance_securite=40.0)
        v, omega = strat.compute_command([100, 100, 10])  # obstacle droite
        assert omega < 0


class TestGoalAndAvoidStrategy:

    def test_sans_cible_retourne_zero(self):
        """Sans cible définie, la commande doit être (0, 0)."""
        strat = GoalAndAvoidStrategy(distance_securite=50.0)
        v, omega = strat.compute_command([100, 100, 100], 0, 0, 0)
        assert v == 0.0
        assert omega == 0.0

    def test_avec_cible_avance(self):
        """Avec une cible devant, le robot doit avancer."""
        strat = GoalAndAvoidStrategy(distance_securite=50.0)
        strat.set_cible(100, 0)
        v, omega = strat.compute_command([100, 100, 100], 0, 0, 0)
        assert v > 0

    def test_obstacle_prioritaire_sur_cible(self):
        """Un obstacle proche doit prendre le dessus sur la navigation vers la cible."""
        strat = GoalAndAvoidStrategy(distance_securite=50.0)
        strat.set_cible(100, 0)
        # Obstacle très proche devant
        v, omega = strat.compute_command([100, 10, 100], 0, 0, 0)
        assert omega != 0.0  # esquive activée

    def test_set_cible_none(self):
        """set_cible(None, None) doit remettre la cible à None."""
        strat = GoalAndAvoidStrategy()
        strat.set_cible(100, 200)
        strat.set_cible(None, None)
        assert strat.cible_x is None
        assert strat.cible_y is None
