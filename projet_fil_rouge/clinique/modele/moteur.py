"""moteur.py — Modèle physique du moteur différentiel réaliste."""
import math


class MoteurDifferentielRealiste:
    """Simule un moteur différentiel avec accélération, frottements et saturation."""

    def __init__(self, v_max=2.0, omega_max=1.0, a_max=0.5, frottement=0.1):
        # Paramètres physiques
        self.v_max = v_max
        self.omega_max = omega_max
        self.a_max = a_max
        self.frottement = frottement

        # Vitesses réelles actuelles
        self.v = 0.0
        self.omega = 0.0

    def clip(self, valeur, min_val, max_val):
        """Bride une valeur entre un minimum et un maximum."""
        return max(min_val, min(valeur, max_val))

    def mettre_a_jour(self, v_cmd, omega_cmd, dt):
        """Met à jour les vitesses et retourne (delta_v, delta_omega)."""
        # 1. Limitation d'accélération
        self.v += self.clip(v_cmd - self.v, -self.a_max * dt, self.a_max * dt)
        self.omega += self.clip(omega_cmd - self.omega, -self.a_max * dt, self.a_max * dt)

        # 2. Frottements
        self.v *= (1 - self.frottement * dt)
        self.omega *= (1 - self.frottement * dt)

        # 3. Saturation
        self.v = self.clip(self.v, -self.v_max, self.v_max)
        self.omega = self.clip(self.omega, -self.omega_max, self.omega_max)

        return self.v * dt, self.omega * dt