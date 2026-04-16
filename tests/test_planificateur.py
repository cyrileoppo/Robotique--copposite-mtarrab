"""Tests unitaires pour le planificateur (sac-à-dos + greedy TSP)."""
import sys
import os
import math
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from projet_fil_rouge.clinique.controleur.planificateur import (
    algorithme_sac_a_dos,
    optimiser_trajet_greedy,
)


# Objet minimal simulant un robot avec poids et position
class _FakeRobot:
    def __init__(self, id_, poids, x=0, y=0):
        self.id = id_
        self.poids = poids
        self.x = x
        self.y = y


class TestAlgorithmeSacADos:

    def test_liste_vide(self):
        assert algorithme_sac_a_dos([], 50) == []

    def test_selection_simple(self):
        """Avec capacité 30, on doit prendre les robots de poids 10 et 20."""
        robots = [_FakeRobot("A", 10), _FakeRobot("B", 20), _FakeRobot("C", 25)]
        selection = algorithme_sac_a_dos(robots, 30)
        poids_total = sum(r.poids for r in selection)
        assert poids_total <= 30
        assert len(selection) == 2  # A + B = 30

    def test_capacite_zero(self):
        robots = [_FakeRobot("A", 10)]
        assert algorithme_sac_a_dos(robots, 0) == []

    def test_tous_rentrent(self):
        robots = [_FakeRobot(f"R{i}", 5) for i in range(4)]
        selection = algorithme_sac_a_dos(robots, 20)
        assert len(selection) == 4

    def test_poids_depasse_capacite(self):
        robots = [_FakeRobot("A", 100)]
        assert algorithme_sac_a_dos(robots, 50) == []


class TestOptimiserTrajetGreedy:

    def test_liste_vide(self):
        assert optimiser_trajet_greedy(0, 0, []) == []

    def test_un_robot(self):
        r = _FakeRobot("A", 10, x=100, y=0)
        trajet = optimiser_trajet_greedy(0, 0, [r])
        assert trajet == [r]

    def test_ordre_plus_proche(self):
        """Le robot le plus proche de la base doit être visité en premier."""
        r_proche = _FakeRobot("Proche", 10, x=10, y=0)
        r_loin = _FakeRobot("Loin", 10, x=500, y=0)
        trajet = optimiser_trajet_greedy(0, 0, [r_loin, r_proche])
        assert trajet[0] == r_proche

    def test_tous_visites(self):
        robots = [_FakeRobot(f"R{i}", 5, x=i * 50, y=0) for i in range(5)]
        trajet = optimiser_trajet_greedy(0, 0, robots)
        assert len(trajet) == 5
        assert set(trajet) == set(robots)
