"""
Application Flask pour Songo avec WebSockets (Socket.IO)
Gère les sessions multijoueurs en temps réel
"""
 
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
import uuid
from songo_engine import SongoGame
 
app = Flask(__name__)
app.config['SECRET_KEY'] = 'songo_secret_key_2024'
socketio = SocketIO(app, cors_allowed_origins="*")
 
# Stockage des salons et des parties
game_rooms = {}
player_sessions = {}
 
class GameRoom:
    """Classe représentant une salle de jeu"""
    def __init__(self, room_id):
        self.room_id = room_id
        self.game = SongoGame()
        self.players = {}  # {player_id: {'name', 'avatar', 'role'}}
        self.ready = {}    # {player_id: True/False}
        
    def add_player(self, player_id, name, avatar):
        """Ajouter un joueur à la salle"""
        if len(self.players) >= 2:
            return False, "La salle est pleine"
        
        # Assigner le rôle (nord ou sud)
        role = 'north' if len(self.players) == 0 else 'south'
        
        self.players[player_id] = {
            'name': name,
            'avatar': avatar,
            'role': role
        }
        self.ready[player_id] = False
        return True, role
    
    def remove_player(self, player_id):
        """Retirer un joueur de la salle"""
        if player_id in self.players:
            del self.players[player_id]
        if player_id in self.ready:
            del self.ready[player_id]
    
    def are_all_ready(self):
        """Vérifier si tous les joueurs sont prêts"""
        return len(self.players) == 2 and all(self.ready.values())
    
    def get_state(self):
        """Retourner l'état complet de la salle"""
        game_state = self.game.get_state()
        return {
            'room_id': self.room_id,
            'players': self.players,
            'game': game_state,
            'ready': self.ready
        }
 
@app.route('/')
def index():
    """Page d'accueil"""
    return render_template('index.html')
 
@socketio.on('connect')
def handle_connect():
    """Gestion de la connexion"""
    player_id = str(uuid.uuid4())
    player_sessions[request.sid] = player_id
    emit('connection_response', {'player_id': player_id})
 
@socketio.on('disconnect')
def handle_disconnect():
    """Gestion de la déconnexion"""
    player_id = player_sessions.pop(request.sid, None)
    
    # Trouver et quitter la salle
    for room_id, room in list(game_rooms.items()):
        if player_id in room.players:
            room.remove_player(player_id)
            socketio.emit('player_left', {'player_id': player_id}, room=room_id)
            
            # Supprimer la salle si elle est vide
            if len(room.players) == 0:
                del game_rooms[room_id]
 
@socketio.on('create_room')
def handle_create_room(data):
    """Créer une nouvelle salle"""
    name = data.get('name', 'Joueur')
    avatar = data.get('avatar', 'boy')
    
    room_id = str(uuid.uuid4())[:8]
    room = GameRoom(room_id)
    
    success, role = room.add_player(player_sessions[request.sid], name, avatar)
    
    if success:
        game_rooms[room_id] = room
        join_room(room_id)
        emit('room_created', {
            'room_id': room_id,
            'role': role,
            'state': room.get_state()
        })
    else:
        emit('error', {'message': 'Impossible de créer la salle'})
 
@socketio.on('join_room')
def handle_join_room(data):
    """Rejoindre une salle existante"""
    room_id = data.get('room_id')
    name = data.get('name', 'Joueur')
    avatar = data.get('avatar', 'girl')
    
    if room_id not in game_rooms:
        emit('error', {'message': 'Salle non trouvée'})
        return
    
    room = game_rooms[room_id]
    player_id = player_sessions[request.sid]
    
    success, role = room.add_player(player_id, name, avatar)
    
    if success:
        join_room(room_id)
        socketio.emit('player_joined', {
            'player_id': player_id,
            'name': name,
            'avatar': avatar,
            'role': role,
            'state': room.get_state()
        }, room=room_id)
    else:
        emit('error', {'message': 'Impossible de rejoindre la salle'})
 
@socketio.on('player_ready')
def handle_player_ready(data):
    """Marquer un joueur comme prêt"""
    room_id = data.get('room_id')
    
    if room_id not in game_rooms:
        return
    
    room = game_rooms[room_id]
    player_id = player_sessions[request.sid]
    
    room.ready[player_id] = True
    
    socketio.emit('player_ready_update', {
        'ready': room.ready,
        'all_ready': room.are_all_ready()
    }, room=room_id)
 
@socketio.on('play_move')
def handle_play_move(data):
    """Traiter un coup joué"""
    room_id = data.get('room_id')
    index = data.get('index')
    
    if room_id not in game_rooms:
        emit('error', {'message': 'Salle non trouvée'})
        return
    
    room = game_rooms[room_id]
    player_id = player_sessions[request.sid]
    
    # Trouver le rôle du joueur
    player_info = room.players.get(player_id)
    if not player_info:
        emit('error', {'message': 'Joueur non trouvé'})
        return
    
    role = player_info['role']
    
    # Jouer le coup
    success, msg = room.game.play_move(index, role)
    
    if success:
        socketio.emit('move_played', {
            'state': room.game.get_state(),
            'message': msg
        }, room=room_id)
    else:
        emit('error', {'message': msg})
 
@socketio.on('get_hint')
def handle_get_hint(data):
    """Obtenir un indice"""
    room_id = data.get('room_id')
    
    if room_id not in game_rooms:
        emit('error', {'message': 'Salle non trouvée'})
        return
    
    room = game_rooms[room_id]
    player_id = player_sessions[request.sid]
    
    player_info = room.players.get(player_id)
    if not player_info:
        emit('error', {'message': 'Joueur non trouvé'})
        return
    
    role = player_info['role']
    hint = room.game.get_hint(role)
    
    emit('hint_received', {'hint': hint})
 
@socketio.on('reset_game')
def handle_reset_game(data):
    """Réinitialiser la partie"""
    room_id = data.get('room_id')
    
    if room_id not in game_rooms:
        return
    
    room = game_rooms[room_id]
    room.game.reset()
    room.ready = {pid: False for pid in room.players}
    
    socketio.emit('game_reset', {
        'state': room.game.get_state(),
        'ready': room.ready
    }, room=room_id)
 
if __name__ == '__main__':
    # FIX: debug=False pour éviter le conflit avec Werkzeug en production
    socketio.run(app, debug=False, host='0.0.0.0', port=5000)
