# =============================================================================
# config.py — Centralisation de toutes les constantes de la simulation
# =============================================================================

# --- Fenêtre ---
LARGEUR = 800
HAUTEUR = 600

# --- Base de réparation ---
BASE_X = 700
BASE_Y = 100
RAYON_ACTION = 40.0          

# --- Ambulance ---
AMBULANCE_POIDS_PROPRE = 100  
AMBULANCE_CAPACITE_MAX = 75   
AMBULANCE_V_MAX = 60.0          # Vitesse max boostée (était à 40)
AMBULANCE_A_MAX = 30.0          # Freinage/Accélération doublés pour éviter les murs
AMBULANCE_FROTTEMENT = 0.15
AMBULANCE_V_CROISIERE = 55.0    # Vitesse de croisière boostée (était à 35)
AMBULANCE_V_APPROCHE = 15.0     # Vitesse d'approche plus rapide
AMBULANCE_DIST_CROISIERE = 120.0

# Capteurs Ambulance (Minuscules)
AMBULANCE_LIDAR_PORTEE = 40         # Coupé en deux
AMBULANCE_DISTANCE_SECURITE = 40.0  
AMBULANCE_NB_RAYONS = 9             

# --- Robots standards ---
STANDARD_V_MAX = 15.0
STANDARD_A_MAX = 8.0

# Capteurs Standards (Minuscules)
STANDARD_LIDAR_PORTEE = 30          # Coupé en deux
STANDARD_DISTANCE_SECURITE = 30.0   
STANDARD_PROBA_PANNE = 0.0002
STANDARD_RAYON_COLLISION = 15
STANDARD_NB_RAYONS = 7              

# --- Physique / Moteur ---
DT = 0.1                            
FPS = 60                            

# --- Obstacles fixes ---
OBSTACLES = [
    {"x": 400, "y": 150, "rayon": 50},
    {"x": 600, "y": 300, "rayon": 80},
    {"x": 300, "y": 400, "rayon": 60},
]

# --- Robots standards (poids cycliques) ---
POIDS_ROBOTS = [15, 20, 30, 25, 10]

# --- Sortie de base ---
RAYON_SORTIE_BASE = 80              

# --- Réparation à la base ---
REPARATION_MIN_S = 0                
REPARATION_MAX_S = 60