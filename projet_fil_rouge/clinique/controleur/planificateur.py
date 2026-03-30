"""
planificateur.py — Logique métier de l'ambulance.

Contient :
  - algorithme_sac_a_dos : sélection optimale des robots à charger (DP)
  - optimiser_trajet_greedy : ordre de visite (heuristique plus proche voisin, O(n²))
"""

import math


# ---------------------------------------------------------------------------
# Algorithme du sac-à-dos (programmation dynamique)
# ---------------------------------------------------------------------------

def algorithme_sac_a_dos(robots_en_panne, capacite_max):
    """
    Sélectionne le sous-ensemble de robots en panne qui maximise le nombre
    de robots récupérés sans dépasser capacite_max en poids total.

    Complexité : O(n × capacite_max)
    """
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


# ---------------------------------------------------------------------------
# Heuristique du plus proche voisin (remplace le TSP exact O(n!))
# ---------------------------------------------------------------------------

def optimiser_trajet_greedy(base_x, base_y, robots_selectionnes):
    """
    Construit un trajet de visite en choisissant à chaque étape le robot
    non encore visité le plus proche de la position courante.

    Complexité : O(n²) — scalable même avec de nombreux robots.
    """
    if not robots_selectionnes:
        return []

    restants = list(robots_selectionnes)
    trajet = []
    pos_actuelle = (base_x, base_y)

    while restants:
        # Trouver le robot le plus proche
        plus_proche = min(
            restants,
            key=lambda r: math.hypot(r.x - pos_actuelle[0], r.y - pos_actuelle[1]),
        )
        trajet.append(plus_proche)
        pos_actuelle = (plus_proche.x, plus_proche.y)
        restants.remove(plus_proche)

    return trajet
