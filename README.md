# TP2 : Simulation de Robot Mobile (Architecture MVC)

### Membres du groupe : Cyrile Opposite & Mohamad Tarrab

Ce projet est une simulation cinématique d'un robot mobile à entraînement différentiel. Il a été réalisé dans le but de mettre en pratique l'architecture logicielle **MVC (Modèle-Vue-Contrôleur)** en Python, ainsi que la gestion d'un environnement avec détection de collisions.

## Fonctionnalités

* **Modèle Cinématique :** Calcul du déplacement du robot (vitesses linéaire $v$ et angulaire $\omega$).
* **Architecture MVC stricte :** Séparation claire entre la logique physique (Modèle), l'affichage (Vue) et les entrées utilisateur (Contrôleur).
* **Rendu Graphique :** Visualisation en temps réel avec Pygame.
* **Environnement & Collisions :** Détection de collisions avec des obstacles circulaires (le robot est bloqué s'il touche un obstacle).

## Prérequis et Installation

1. Assurez-vous d'avoir Python 3.x installé sur votre machine.
2. Clonez ce dépôt et placez-vous à la racine du projet dans votre terminal.
3. Installez les dépendances requises à l'aide du fichier `requirements.txt` :
   ```bash
   pip install -r requirements.txt