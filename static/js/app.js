/**
 * SONGO - Frontend avec Socket.IO
 * Gestion de l'interface et communication en temps réel
 */

const socket = io();

let gameState = {
    roomId: null,
    playerId: null,
    playerRole: null,
    selectedAvatar: 'boy',
    playerName: '',
    hintsRemaining: 3
};

// ===== SCREEN NAVIGATION =====
function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById(screenId).classList.add('active');
}

function goToWelcome() {
    showScreen('welcome-screen');
}

function goToAvatarScreen() {
    gameState.selectedAvatar = 'boy';
    document.querySelectorAll('.avatar-option').forEach(a => a.classList.remove('selected'));
    document.querySelector('.avatar-option').classList.add('selected');
    document.getElementById('player-name').value = '';
    showScreen('avatar-screen');
}

function goToRoomScreen(mode) {
    gameState.selectedAvatar = 'boy';
    document.querySelectorAll('.avatar-option').forEach(a => a.classList.remove('selected'));
    document.querySelector('.avatar-option').classList.add('selected');
    document.getElementById('player-name-join').value = '';
    document.getElementById('room-code-input').value = '';
    showScreen('room-screen');
}

// ===== AVATAR SELECTION =====
function selectAvatar(avatar) {
    gameState.selectedAvatar = avatar;
    document.querySelectorAll('.avatar-option').forEach(a => a.classList.remove('selected'));
    event.target.closest('.avatar-option').classList.add('selected');
}

// ===== ROOM CREATION =====
function createRoom() {
    const name = document.getElementById('player-name').value.trim();
    if (!name) {
        alert('Veuillez entrer votre nom');
        return;
    }
    
    gameState.playerName = name;
    socket.emit('create_room', {
        name: name,
        avatar: gameState.selectedAvatar
    });
}

function joinRoom() {
    const name = document.getElementById('player-name-join').value.trim();
    const roomCode = document.getElementById('room-code-input').value.trim().toUpperCase();
    
    if (!name || !roomCode) {
        alert('Veuillez entrer votre nom et le code de la salle');
        return;
    }
    
    gameState.playerName = name;
    socket.emit('join_room', {
        room_id: roomCode,
        name: name,
        avatar: gameState.selectedAvatar
    });
}

// ===== SOCKET EVENTS =====
socket.on('connection_response', (data) => {
    gameState.playerId = data.player_id;
});

socket.on('room_created', (data) => {
    gameState.roomId = data.room_id;
    gameState.playerRole = data.role;
    document.getElementById('room-code-display').textContent = data.room_id;
    updateWaitingScreen(data.state);
    showScreen('waiting-screen');
});

socket.on('player_joined', (data) => {
    gameState.roomId = data.room_id || gameState.roomId;
    updateWaitingScreen(data.state);
});

socket.on('player_joined', (data) => {
    gameState.roomId = data.room_id || gameState.roomId;
    updateWaitingScreen(data.state);
    
    // Si tous les joueurs sont présents, afficher le bouton "Prêt"
    if (Object.keys(data.state.players).length === 2) {
        const waitingDiv = document.getElementById('waiting-players');
        waitingDiv.innerHTML = '<button class="btn-primary" onclick="playerReady()" style="width: 100%;">Je suis prêt !</button>';
    }
});

socket.on('player_ready_update', (data) => {
    if (data.all_ready) {
        startGame(gameState.roomId);
    }
});

socket.on('move_played', (data) => {
    updateGameBoard(data.state);
    showMessage(data.message, 'success');
});

socket.on('game_reset', (data) => {
    updateGameBoard(data.state);
    showMessage('Partie réinitialisée', 'info');
});

socket.on('hint_received', (data) => {
    if (data.hint !== null) {
        highlightHint(data.hint);
    }
});

socket.on('error', (data) => {
    showMessage(data.message, 'error');
});

socket.on('player_left', (data) => {
    showMessage('Un joueur a quitté la partie', 'error');
    setTimeout(() => goToWelcome(), 2000);
});

// ===== GAME FUNCTIONS =====
function updateWaitingScreen(state) {
    const waitingDiv = document.getElementById('waiting-players');
    let html = '<div style="text-align: center;">';
    
    Object.entries(state.players).forEach(([id, player]) => {
        html += `
            <div style="margin: 15px 0;">
                <img src="/static/images/avatar_${player.avatar}.png" alt="${player.name}" 
                     style="width: 80px; height: 80px; border-radius: 50%; border: 3px solid #d4af37;">
                <p><strong>${player.name}</strong></p>
                <p style="color: #999; font-size: 0.9rem;">${player.role === 'north' ? 'NORD' : 'SUD'}</p>
            </div>
        `;
    });
    
    html += '</div>';
    waitingDiv.innerHTML = html;
}

function playerReady() {
    socket.emit('player_ready', { room_id: gameState.roomId });
}

function startGame(roomId) {
    showScreen('game-screen');
    socket.emit('play_move', { room_id: roomId, index: -1 }); // Trigger initial state
}

function updateGameBoard(state) {
    // Mettre à jour les scores
    document.getElementById('player-north-score').textContent = state.game.scores.north;
    document.getElementById('player-south-score').textContent = state.game.scores.south;
    
    // Mettre à jour les joueurs
    Object.entries(state.players).forEach(([id, player]) => {
        const card = document.getElementById(`player-${player.role}-card`);
        card.querySelector('.player-avatar').src = `/static/images/avatar_${player.avatar}.png`;
        card.querySelector('.player-name').textContent = player.name;
        
        if (state.game.current_player === player.role) {
            card.classList.add('active');
        } else {
            card.classList.remove('active');
        }
    });
    
    // Mettre à jour le plateau
    state.game.board.forEach((count, index) => {
        const hole = document.querySelector(`.hole[data-index="${index}"]`);
        const countSpan = hole.querySelector('.seed-count');
        const visualDiv = hole.querySelector('.seeds-visual');
        
        countSpan.textContent = count;
        
        // Visualisation des graines
        visualDiv.innerHTML = '';
        const visualCount = Math.min(count, 12);
        for (let i = 0; i < visualCount; i++) {
            const seed = document.createElement('div');
            seed.className = 'seed';
            seed.style.transform = `translate(${Math.random()*8-4}px, ${Math.random()*8-4}px)`;
            visualDiv.appendChild(seed);
        }
        
        // Gérer les classes
        hole.classList.remove('playable', 'disabled');
        const isMyHole = (gameState.playerRole === 'north' && index <= 6) || 
                        (gameState.playerRole === 'south' && index >= 7);
        const isMyTurn = state.game.current_player === gameState.playerRole;
        
        if (isMyTurn && isMyHole && count > 0) {
            hole.classList.add('playable');
            hole.onclick = () => playMove(index);
        } else {
            hole.classList.add('disabled');
            hole.onclick = null;
        }
    });
    
    // Mettre à jour le message de statut
    if (state.game.game_over) {
        let message = '';
        if (state.game.winner === 'draw') {
            message = '🤝 Match nul !';
        } else {
            const winner = state.game.winner === 'north' ? 'NORD' : 'SUD';
            message = `🎉 ${winner} a gagné !`;
        }
        showMessage(message, 'success');
        document.getElementById('btn-reset').style.display = 'block';
    } else {
        const player = Object.values(state.players).find(p => p.role === state.game.current_player);
        showMessage(`À ${player.name} de jouer !`, 'info');
    }
}

function playMove(index) {
    socket.emit('play_move', {
        room_id: gameState.roomId,
        index: index
    });
}

function getHint() {
    if (gameState.hintsRemaining <= 0) {
        showMessage('Vous avez épuisé vos indices', 'error');
        return;
    }
    
    socket.emit('get_hint', { room_id: gameState.roomId });
    gameState.hintsRemaining--;
}

function highlightHint(hintIndex) {
    const hole = document.querySelector(`.hole[data-index="${hintIndex}"]`);
    hole.classList.add('hint-highlight');
    setTimeout(() => hole.classList.remove('hint-highlight'), 2000);
}

function resetGame() {
    socket.emit('reset_game', { room_id: gameState.roomId });
    gameState.hintsRemaining = 3;
    document.getElementById('btn-reset').style.display = 'none';
}

// ===== UI HELPERS =====
function showMessage(msg, type = 'info') {
    const msgEl = document.getElementById('status-message');
    msgEl.textContent = msg;
    msgEl.className = `status-message ${type}`;
}

function showHelp() {
    document.getElementById('help-modal').classList.add('active');
}

function closeHelp() {
    document.getElementById('help-modal').classList.remove('active');
}
