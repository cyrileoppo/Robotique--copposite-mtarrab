"""Tests unitaires pour MoteurDifferentielRealiste."""
import sys
import os
import math
import pytest

# Ajout du chemin racine pour les imports relatifs
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from projet_fil_rouge.clinique.modele.moteur import MoteurDifferentielRealiste


class TestMoteurDifferentielRealiste:

    def test_acceleration_limitee(self):
        """Le moteur ne peut pas dépasser a_max * dt en un seul pas."""
        moteur = MoteurDifferentielRealiste(a_max=1.0)
        dv, _ = moteur.mettre_a_jour(100.0, 0.0, dt=0.1)
        # dv = v * dt, et v ne peut avoir augmenté que de a_max * dt = 0.1
        assert moteur.v <= 0.1 + 1e-9

    def test_saturation_vitesse(self):
        """La vitesse ne dépasse jamais v_max."""
        moteur = MoteurDifferentielRealiste(v_max=5.0, a_max=100.0)
        for _ in range(100):
            moteur.mettre_a_jour(50.0, 0.0, dt=0.1)
        assert moteur.v <= 5.0 + 1e-9

    def test_frottement_ralentit(self):
        """Avec une commande nulle, le frottement doit ralentir le robot."""
        moteur = MoteurDifferentielRealiste(frottement=0.5)
        moteur.v = 10.0
        moteur.mettre_a_jour(0.0, 0.0, dt=0.1)
        assert moteur.v < 10.0

    def test_retour_deplacement(self):
        """mettre_a_jour retourne (dv, domega) cohérents avec dt."""
        moteur = MoteurDifferentielRealiste(v_max=10.0, a_max=100.0, frottement=0.0)
        dv, domega = moteur.mettre_a_jour(5.0, 0.0, dt=1.0)
        assert dv == pytest.approx(moteur.v * 1.0, rel=1e-3)

    def test_vitesse_negative(self):
        """Le moteur accepte les commandes négatives (marche arrière)."""
        moteur = MoteurDifferentielRealiste(v_max=5.0, a_max=100.0, frottement=0.0)
        moteur.mettre_a_jour(-5.0, 0.0, dt=1.0)
        assert moteur.v < 0
