# La Clinique des Robots

**La Clinique des Robots** est une simulation de robotique autonome en 2D développée en Python avec Pygame.

Des **robots standards** naviguent de manière autonome et évitent les obstacles grâce à des capteurs Lidar, mais peuvent tomber en panne aléatoirement. Un robot spécial, **l'ambulance**, est chargé d'aller secourir ces robots défectueux en optimisant ses tournées et sa charge utile, puis de les ramener à la base pour réparation.

Le projet met en pratique l'architecture **MVC (Modèle-Vue-Contrôleur)** ainsi que des algorithmes classiques d'optimisation et de navigation.

---

## Fonctionnalités

- **Navigation autonome et évitement** — capteurs Lidar à moustaches (rayons en cône frontal) pour détecter obstacles, bordures et autres robots. Déviation fluide basée sur la répartition du danger gauche/droite.
- **Détection et déblocage** — chaque robot surveille sa propre position sur les dernières frames et déclenche une manœuvre d'échappatoire s'il est bloqué (blocage mutuel entre robots).
- **Collisions inter-robots** — en cas de contact, le robot dévie automatiquement du côté opposé au robot bloquant (produit vectoriel) au lieu de simplement s'arrêter.
- **Pannes aléatoires et réparation** — les robots standards ont une probabilité de tomber en panne à chaque frame. L'ambulance les collecte, les ramène à la base, où ils sont réparés puis redéployés via un sas de sortie avec file d'attente.
- **Optimisation de la collecte (ambulance)** :
  - **Algorithme du sac-à-dos (programmation dynamique)** — sélection optimale des robots à charger sans dépasser la capacité maximale (75 kg).
  - **Heuristique du plus proche voisin** — ordonnancement du trajet de collecte pour minimiser la distance parcourue.
- **Architecture MVC** — séparation entre la logique de simulation (Modèle), le rendu graphique Pygame (Vue) et les stratégies de navigation (Contrôleur).

---

## Structure du projet

```
projet_fil_rouge/clinique/
├── __main__.py              # Point d'entrée, boucle de simulation
├── config.py                # Constantes centralisées
├── logging_config.py        # Configuration du logger
├── modele/
│   ├── robot.py             # RobotMobile, RobotStandard, RobotAmbulance
│   ├── moteur.py            # Moteur différentiel réaliste (accélération, frottements)
│   ├── capteurs.py          # Lidar à moustaches (rayons + détection inter-robots)
│   ├── obstacles.py         # Obstacle circulaire + intersection rayon/cercle
│   └── environnement.py     # Monde : robots, obstacles, bordures, collisions
├── controleur/
│   ├── strategies.py        # AvoidStrategy, GoalAndAvoidStrategy (pattern Strategy)
│   └── planificateur.py     # Sac-à-dos + plus proche voisin
└── vue/
    └── vue_pygame.py        # Rendu graphique Pygame
```

---

## Installation pas à pas

### 1. Cloner le dépôt

```bash
git clone <url-du-repo>
cd Robotique--copposite-mtarrab
```

### 2. Créer un environnement virtuel (recommandé)

```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate          # Windows
```

### 3. Installer les dépendances

```bash
pip install -r projet_fil_rouge/requirements.txt
```

Cela installe :
- **pygame** — rendu graphique 2D
- **pytest** — exécution des tests unitaires (optionnel)

### 4. Vérifier l'installation

```bash
python3 -c "import pygame; print('pygame', pygame.ver)"
```

---

## Lancement

Depuis la **racine du dépôt** :

```bash
python -m projet_fil_rouge.clinique
```

### Options

| Option | Description |
|---|---|
| `--debug` | Active les logs détaillés (niveau DEBUG) |
| `--nb-robots N` | Nombre de robots standards (défaut : 5) |

### Exemples

```bash
# Lancement par défaut (5 robots, logs INFO)
python -m projet_fil_rouge.clinique

# Mode debug avec 8 robots
python -m projet_fil_rouge.clinique --debug --nb-robots 8
```

Pour quitter la simulation, fermez la fenêtre Pygame.

---

## Légende visuelle

| Couleur | Signification |
|---|---|
| Rouge | Ambulance |
| Bleu | Robot standard (actif) |
| Gris | Robot en panne |
| Orange | Robot en sortie de base |
| Violet | Robot en réparation |
| Vert (traits) | Rayons Lidar |
| Vert (rectangle) | Base de réparation |

---

## Tests

Depuis la racine du dépôt :

```bash
pytest tests/ -v
```

