# =============================================================================
# config.py — Centralisation de toutes les constantes de la simulation
# =============================================================================

# ── Fenêtre de simulation ─────────────────────────────────────────────
LARGEUR = 800
HAUTEUR = 600

# ── Base de réparation ────────────────────────────────────────────────
BASE_X = 700
BASE_Y = 100
RAYON_ACTION = 40.0

# ── Ambulance — dynamique ─────────────────────────────────────────────
AMBULANCE_POIDS_PROPRE = 100
AMBULANCE_CAPACITE_MAX = 75
AMBULANCE_V_MAX = 60.0
AMBULANCE_A_MAX = 30.0
AMBULANCE_FROTTEMENT = 0.15
AMBULANCE_V_CROISIERE = 55.0
AMBULANCE_V_APPROCHE = 15.0
AMBULANCE_DIST_CROISIERE = 120.0

# ── Ambulance — capteurs ──────────────────────────────────────────────
AMBULANCE_LIDAR_PORTEE = 40
AMBULANCE_DISTANCE_SECURITE = 40.0
AMBULANCE_NB_RAYONS = 9

# ── Robots standards — dynamique ──────────────────────────────────────
STANDARD_V_MAX = 15.0
STANDARD_A_MAX = 8.0

# ── Robots standards — capteurs et comportement ───────────────────────
STANDARD_LIDAR_PORTEE = 30
STANDARD_DISTANCE_SECURITE = 30.0
STANDARD_PROBA_PANNE = 0.002
STANDARD_RAYON_COLLISION = 15
STANDARD_NB_RAYONS = 7

# ── Physique générale ─────────────────────────────────────────────────
DT = 0.1
FPS = 60

# ── Obstacles fixes (cercles) ─────────────────────────────────────────
OBSTACLES = [
    {"x": 400, "y": 150, "rayon": 50},
    {"x": 600, "y": 300, "rayon": 80},
    {"x": 300, "y": 400, "rayon": 60},
]

# ── Poids cycliques des robots standards ──────────────────────────────
POIDS_ROBOTS = [15, 20, 30, 25, 10]

# ── Sortie de base ────────────────────────────────────────────────────
RAYON_SORTIE_BASE = 80              

# --- Réparation à la base ---
REPARATION_MIN_S = 0                
REPARATION_MAX_S = 60