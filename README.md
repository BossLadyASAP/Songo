# Projet Songo - Jeu Multijoueur (Version Python)

Bienvenue dans l'implémentation numérique du jeu de **Songo**, refondue avec un backend Python (Flask) et des WebSockets (Socket.IO) pour une expérience multijoueur en temps réel.

## Fonctionnalités Clés
- **Multijoueur en Temps Réel** : Jouez avec un ami en ligne grâce à une communication instantanée.
- **Design Mobile-First** : Interface intuitive et responsive, adaptée à tous les appareils.
- **Avatars Personnalisables** : Choisissez votre avatar (garçon ou fille style anime) pour personnaliser votre expérience.
- **Système de Salles** : Créez ou rejoignez des parties facilement avec un code unique.
- **Moteur de Jeu Complet** : Implémentation fidèle des règles du Songo, y compris les captures en chaîne et la solidarité.
- **Indices Intégrés** : Bénéficiez de 3 indices par partie pour vous aider à prendre les meilleures décisions.
- **Visualisation Dynamique** : Les graines sont représentées visuellement dans les cases pour une meilleure immersion.
- **Indicateurs Visuels** : Sachez toujours qui joue et qui est connecté.

## Structure du Projet
- `app.py` : Application Flask principale gérant le serveur web et les communications Socket.IO.
- `songo_engine.py` : Logique métier du jeu Songo (règles, plateau, mouvements, captures).
- `static/` :
    - `css/style.css` : Styles CSS pour le design de l'interface.
    - `js/app.js` : Logique JavaScript côté client pour l'interaction et Socket.IO.
    - `images/` : Logo du jeu et avatars.
- `templates/` :
    - `index.html` : Template HTML principal de l'application.
- `requirements.txt` : Liste des dépendances Python.
- `Rapport_Songo_Python.md` : Rapport technique détaillé du projet.

## Installation et Utilisation

### Prérequis
- Python 3.x
- `pip` (gestionnaire de paquets Python)

### Étapes
1.  **Téléchargez ou clonez le projet.**
2.  **Naviguez vers le répertoire racine du projet :**
    ```bash
    cd /chemin/vers/songo_project
    ```
3.  **Installez les dépendances Python :**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Lancez le serveur Flask :**
    ```bash
    python app.py
    ```
    Le serveur démarrera sur `http://127.0.0.1:5000` par défaut. Ouvrez cette adresse dans votre navigateur.

### Jouer en Multijoueur
1.  Ouvrez l'URL du jeu dans deux navigateurs différents (ou sur deux appareils connectés au même réseau).
2.  **Premier joueur :** Sur l'écran d'accueil, cliquez sur "Créer une partie". Entrez votre nom, choisissez un avatar et cliquez sur "Créer une partie". Un code de salle unique vous sera affiché.
3.  **Deuxième joueur :** Sur l'écran d'accueil, cliquez sur "Rejoindre une partie". Entrez votre nom, choisissez un avatar et saisissez le code de salle fourni par le premier joueur.
4.  Une fois les deux joueurs connectés et affichés dans la salle d'attente, cliquez sur "Je suis prêt !" pour commencer la partie.

---
**Réalisé par :** MATAGNE DASSE PRESLIE CHANEL  
**Licence 2** - UNIVERSITÉ DE YAOUNDE I
