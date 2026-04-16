"""planificateur.py — Algorithmes de planification de l'ambulance."""

import math


# =====================================================================
# Sélection des robots à charger (sac-à-dos, programmation dynamique)
# =====================================================================

def algorithme_sac_a_dos(robots_en_panne, capacite_max):
    """Maximise le nombre de robots récupérés sans dépasser la capacité."""
    n = len(robots_en_panne)
    dp = [[0] * (capacite_max + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        poids = robots_en_panne[i - 1].poids
        for w in range(capacite_max + 1):
            if poids <= w:
                dp[i][w] = max(dp[i - 1][w], dp[i - 1][w - poids] + 1)
            else:
                dp[i][w] = dp[i - 1][w]

    # Reconstruction de la solution
    selection = []
    w = capacite_max
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            selection.append(robots_en_panne[i - 1])
            w -= robots_en_panne[i - 1].poids

    return selection


# =====================================================================
# Ordre de visite (heuristique du plus proche voisin)
# =====================================================================

def optimiser_trajet_greedy(base_x, base_y, robots_selectionnes):
    """Ordonne la visite par plus proche voisin depuis la base."""
    if not robots_selectionnes:
        return []

    restants = list(robots_selectionnes)
    trajet = []
    pos_actuelle = (base_x, base_y)

    while restants:
        plus_proche = min(
            restants,
            key=lambda r: math.hypot(
                r.x - pos_actuelle[0], r.y - pos_actuelle[1]),
        )
        trajet.append(plus_proche)
        pos_actuelle = (plus_proche.x, plus_proche.y)
        restants.remove(plus_proche)

    return trajet
