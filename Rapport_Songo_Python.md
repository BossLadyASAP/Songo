# Rapport de Projet : Développement du Jeu Songo (Version Python)

**Auteur :** MATAGNE DASSE PRESLIE CHANEL  
**Niveau :** LICENCE 2  
**Institution :** UNIVERSITÉ DE YAOUNDE I  
**Date :** 10 Juin 2026

---

## 1. Introduction
Ce rapport détaille la refonte du jeu **Songo** avec une architecture moderne basée sur Python. L'objectif était de créer une expérience multijoueur en temps réel, intuitive et mobile-first, intégrant des fonctionnalités avancées telles que la sélection d'avatars et un système d'indices. Cette version remplace l'implémentation PHP/AJAX précédente par un backend Flask avec WebSockets (Socket.IO).

## 2. Fonctionnement du Jeu Songo
Le Songo est un jeu de semailles traditionnel d'Afrique Centrale. Il se joue sur un plateau de 14 cases, initialement garnies de 5 graines chacune. Les règles fondamentales incluent :
- **Objectif :** Le premier joueur à capturer au moins 40 graines remporte la partie.
- **Déroulement :** Les joueurs choisissent une case de leur camp, ramassent toutes les graines qu'elle contient et les distribuent une à une dans les cases suivantes dans le sens horaire.
- **Captures :** Une capture a lieu dans le camp adverse si la dernière graine semée tombe dans une case qui contient alors 2, 3 ou 4 graines. Des captures en chaîne sont possibles si les cases précédentes respectent également cette condition.
- **Règles Spéciales :** Des règles de 
solidarité (obligation de nourrir l'adversaire si son camp est vide) et d'interdiction (ne pas vider complètement le camp adverse) sont également en vigueur.

## 3. Architecture Technique (Version Python)
Cette nouvelle version s'appuie sur une architecture client-serveur robuste, permettant une interaction en temps réel entre les joueurs distants.

### 3.1. Backend (Python - Flask & Socket.IO)
- **Flask :** Le micro-framework web Python est utilisé pour gérer les requêtes HTTP de base et servir les fichiers statiques (HTML, CSS, JS, images).
- **Flask-SocketIO :** Cette extension permet l'intégration de WebSockets, offrant une communication bidirectionnelle et en temps réel entre le serveur et les clients. Cela élimine le besoin de 
polling AJAX et assure une synchronisation instantanée de l'état du jeu.
- **`app.py` :** Fichier principal de l'application Flask. Il gère les routes, les événements Socket.IO (connexion, déconnexion, création/rejoindre de salle, jeu, indices, réinitialisation) et maintient l'état des salles de jeu et des sessions des joueurs.
- **`songo_engine.py` :** Ce module encapsule toute la logique métier du jeu Songo. Il contient la classe `SongoGame` qui gère le plateau, les scores, le joueur actuel, les règles de mouvement, de capture, de solidarité, de fin de partie, et la génération d'indices. Le moteur est indépendant de l'interface utilisateur, ce qui le rend réutilisable.
- **Gestion des Salles (`GameRoom`) :** Une classe `GameRoom` est utilisée pour gérer l'état de chaque partie multijoueur, incluant les joueurs connectés, leurs avatars, leurs rôles (Nord/Sud), et l'instance `SongoGame` associée à la salle.

### 3.2. Frontend (HTML, CSS, JavaScript & Socket.IO Client)
- **HTML (`templates/index.html`) :** Structure de l'interface utilisateur, divisée en plusieurs écrans (accueil, sélection d'avatar, sélection/création de salle, jeu, aide) pour une navigation fluide. Utilise Jinja2 pour l'intégration des fichiers statiques.
- **CSS (`static/css/style.css`) :** Design moderne et mobile-first, assurant une expérience utilisateur optimale sur différents appareils. Les éléments visuels du plateau (cases, graines) sont stylisés pour être intuitifs et esthétiques. Les avatars sont intégrés dynamiquement.
- **JavaScript (`static/js/app.js`) :** Gère l'interactivité côté client. Il établit la connexion WebSocket avec le serveur, envoie les actions du joueur (clics sur les cases, création/rejoindre de salle) et met à jour l'interface utilisateur en temps réel en fonction des événements reçus du serveur. Il inclut également la logique de navigation entre les écrans, la sélection d'avatars, et l'affichage des messages de statut.

### 3.3. Fonctionnalités Clés et Améliorations
- **Multijoueur en Temps Réel :** Grâce à Socket.IO, les actions des joueurs sont instantanément répercutées chez l'adversaire, offrant une expérience de jeu fluide et synchronisée.
- **Système de Salles :** Les joueurs peuvent créer des salles avec un code unique ou rejoindre une salle existante, facilitant les parties entre amis.
- **Avatars Personnalisables :** Les joueurs peuvent choisir entre un avatar 
de garçon ou de fille de style anime, ajoutant une touche personnelle à l'expérience de jeu. Ces avatars sont affichés dans les cartes de joueur pour identifier clairement les participants.
- **Design Mobile-First et Intuitif :** L'interface a été conçue en priorité pour les appareils mobiles, garantissant une adaptabilité et une ergonomie sur toutes les tailles d'écran. Les éléments visuels sont clairs, les interactions sont simples et le flux de jeu est facile à comprendre.
- **Visualisation des Graines :** Les graines sont représentées visuellement dans chaque case, avec un positionnement aléatoire pour simuler un aspect plus naturel et dynamique, améliorant l'immersion du joueur.
- **Système d'Indices :** Un bouton 
💡 "Indice" est disponible, offrant une suggestion de coup optimal (basée sur une heuristique simple de capture maximale) au joueur actif. Chaque joueur dispose de 3 indices par partie.
- **Indicateurs Visuels :** Les cartes de joueur affichent clairement qui est le joueur actif, et les cases jouables sont mises en évidence, rendant le jeu plus compréhensible.

## 4. Fonctionnement Détaillé du Multijoueur

### Création et Jonction de Salles
1.  **Création :** Un joueur entre son nom et choisit un avatar, puis clique sur "Créer une partie". Le serveur génère un `room_id` unique et le joueur est assigné au rôle "north". Le `room_id` est affiché pour être partagé.
2.  **Jonction :** Un deuxième joueur entre son nom, choisit un avatar et saisit le `room_id` fourni par le premier joueur. Il est alors assigné au rôle "south".

### Synchronisation en Temps Réel
-   Dès que deux joueurs sont connectés et prêts dans une salle, la partie commence.
-   Chaque action de jeu (clic sur une case) est envoyée au serveur via Socket.IO.
-   Le serveur valide le coup, met à jour l'état du jeu (`SongoGame` instance), et diffuse le nouvel état à tous les clients de la salle.
-   Les clients reçoivent l'état mis à jour et rafraîchissent leur interface utilisateur (plateau, scores, joueur actif, messages).

### Gestion des Joueurs
-   Le serveur maintient une liste des `player_sessions` (mapping `request.sid` à `player_id`) et des `game_rooms`.
-   En cas de déconnexion d'un joueur, le serveur met à jour l'état de la salle et informe les autres joueurs. Si une salle devient vide, elle est supprimée.

## 5. Conclusion
Cette implémentation du jeu Songo en Python (Flask + Socket.IO) offre une expérience de jeu multijoueur moderne et engageante. L'accent a été mis sur l'intuitivité, la réactivité mobile et la fluidité des interactions en temps réel. Le code est structuré de manière modulaire, séparant clairement la logique métier du jeu (dans `songo_engine.py`) de la gestion du serveur et de l'interface utilisateur, facilitant ainsi la maintenance et d'éventuelles évolutions futures.

## 6. Instructions pour Lancer le Projet

### Prérequis
-   Python 3.x
-   `pip` (gestionnaire de paquets Python)

### Étapes
1.  **Cloner le dépôt ou télécharger l'archive du projet.**
2.  **Naviguer vers le répertoire du projet :**
    ```bash
    cd /chemin/vers/songo_project
    ```
3.  **Installer les dépendances Python :**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Lancer le serveur Flask :**
    ```bash
    python app.py
    ```
    Le serveur démarrera sur `http://127.0.0.1:5000` par défaut. Vous pouvez accéder au jeu via votre navigateur à cette adresse.

### Jouer en Multijoueur
1.  Ouvrez l'URL du jeu dans deux navigateurs différents (ou sur deux appareils).
2.  Dans le premier navigateur, cliquez sur "Créer une partie", entrez votre nom et choisissez un avatar. Un code de salle sera généré.
3.  Dans le deuxième navigateur, cliquez sur "Rejoindre une partie", entrez votre nom, choisissez un avatar et saisissez le code de salle.
4.  Une fois les deux joueurs connectés, cliquez sur "Je suis prêt !" pour commencer la partie.
