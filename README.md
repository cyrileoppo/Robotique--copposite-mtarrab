# 🏥 La Clinique des Robots

**La Clinique des Robots** est une simulation de robotique autonome en 2D développée en Python avec Pygame. 

Dans cet environnement, des **robots standards** naviguent de manière autonome, évitent les obstacles grâce à des capteurs Lidar, mais peuvent tomber en panne aléatoirement. Un robot spécial, **l'ambulance**, est chargé d'aller secourir ces robots défectueux en optimisant ses tournées et sa charge utile avant de les ramener à la base pour réparation.

Ce projet met en pratique l'architecture logicielle **MVC (Modèle-Vue-Contrôleur)** ainsi que des algorithmes classiques d'optimisation et de navigation.

---

## ✨ Fonctionnalités Principales

* **Navigation Autonome & Évitement :** Les robots utilisent des capteurs (Lidar à moustaches simulés) pour détecter et esquiver les obstacles, les murs invisibles et les autres robots de manière fluide.
* **Système de Pannes et de Réparation :** Les robots ont une probabilité de tomber en panne. L'ambulance les charge, les ramène à la base où ils sont réparés avec un système de file d'attente et de gestion du sas de sortie.
* **Optimisation de la Collecte (Ambulance) :**
  * **Algorithme du Sac-à-dos (Programmation Dynamique) :** L'ambulance calcule la meilleure combinaison de robots à récupérer pour maximiser le sauvetage sans dépasser sa capacité de charge maximale.
  * **Heuristique du Plus Proche Voisin :** Une fois les robots sélectionnés, l'ambulance calcule un trajet optimisé (Greedy) pour les ramener le plus efficacement possible.
* **Architecture MVC :** Séparation stricte entre la logique de simulation (Modèle), le rendu graphique (Vue) et les décisions comportementales (Contrôleur).

---

## 🛠️ Prérequis et Installation

### 1. Prérequis
Pour faire tourner cette simulation, vous devez avoir installé :
* **Python 3.8** ou supérieur.

### 2. Installation des dépendances
Le projet repose sur la bibliothèque `pygame` pour le rendu graphique. 

Ouvrez votre terminal et installez la dépendance via la commande suivante :
```bash
pip install requirements.txt



