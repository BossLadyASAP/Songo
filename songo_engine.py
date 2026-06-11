"""
Moteur de jeu Songo - Backend Python
Implémente les règles complètes du Songo
"""

class SongoGame:
    """Classe principale gérant la logique du jeu Songo"""
    
    def __init__(self):
        """Initialiser une nouvelle partie"""
        self.board = [5] * 14  # 14 cases, 5 graines chacune
        self.scores = {'north': 0, 'south': 0}
        self.current_player = 'south'
        self.game_over = False
        self.winner = None
        self.move_history = []
        
    def get_state(self):
        """Retourner l'état actuel du jeu"""
        return {
            'board': self.board,
            'scores': self.scores,
            'current_player': self.current_player,
            'game_over': self.game_over,
            'winner': self.winner,
            'move_history': self.move_history
        }
    
    def is_valid_move(self, index, player):
        """Vérifier si un coup est valide"""
        # Vérifier si c'est le bon joueur
        if self.current_player != player:
            return False, "Ce n'est pas votre tour"
        
        # Vérifier si l'index est dans le bon camp
        is_north_hole = 0 <= index <= 6
        if player == 'north' and not is_north_hole:
            return False, "Vous jouez au Nord, choisissez une case Nord"
        if player == 'south' and is_north_hole:
            return False, "Vous jouez au Sud, choisissez une case Sud"
        
        # Vérifier si la case n'est pas vide
        if self.board[index] == 0:
            return False, "Cette case est vide"
        
        return True, "Coup valide"
    
    def play_move(self, index, player):
        """Jouer un coup"""
        valid, msg = self.is_valid_move(index, player)
        if not valid:
            return False, msg
        
        # Ramasser les graines
        seeds = self.board[index]
        self.board[index] = 0
        
        # Distribuer les graines
        current_index = index
        for _ in range(seeds):
            current_index = (current_index + 1) % 14
            
            # Règle: Si >13 graines, sauter la case de départ au tour complet
            if seeds > 13 and current_index == index:
                current_index = (current_index + 1) % 14
            
            self.board[current_index] += 1
        
        # Gérer les captures
        captures = self._handle_captures(current_index, player)
        self.scores[player] += captures
        
        # Enregistrer le coup
        self.move_history.append({
            'player': player,
            'index': index,
            'seeds': seeds,
            'captures': captures
        })
        
        # Vérifier fin de partie
        self._check_game_over()
        
        # Changer de joueur
        if not self.game_over:
            self.current_player = 'north' if player == 'south' else 'south'
        
        return True, f"Coup joué avec succès. Captures: {captures}"
    
    def _handle_captures(self, last_index, player):
        """Gérer les captures selon les règles du Songo"""
        captures = 0
        index = last_index
        
        # Déterminer le camp adverse
        is_adverse = (player == 'south' and 0 <= index <= 6) or \
                    (player == 'north' and 7 <= index <= 13)
        
        if not is_adverse:
            return 0
        
        # Boucle de capture en chaîne
        while True:
            # Vérifier si on est toujours dans le camp adverse
            is_still_adverse = (player == 'south' and 0 <= index <= 6) or \
                              (player == 'north' and 7 <= index <= 13)
            
            if not is_still_adverse:
                break
            
            # Cas spécial: case 1 de l'adversaire (index 0 pour Nord, 7 pour Sud)
            first_case = 0 if player == 'south' else 7
            if index == first_case and index == last_index:
                # Pas de capture directe sur la case 1 si c'est la fin
                break
            
            # Vérifier la condition de capture (2-4 graines)
            if 2 <= self.board[index] <= 4:
                captures += self.board[index]
                self.board[index] = 0
                # Reculer pour la prise en chaîne
                index = (index - 1) % 14
            else:
                break
        
        # Vérifier si on a vidé tout le camp adverse (Interdit)
        adverse_range = range(0, 7) if player == 'south' else range(7, 14)
        all_empty = all(self.board[i] == 0 for i in adverse_range)
        
        if all_empty and captures > 0:
            # Annuler la prise
            return 0
        
        return captures
    
    def _check_game_over(self):
        """Vérifier les conditions de fin de partie"""
        # Condition 1: Au moins 40 graines
        if self.scores['north'] >= 40:
            self.game_over = True
            self.winner = 'north'
            return
        
        if self.scores['south'] >= 40:
            self.game_over = True
            self.winner = 'south'
            return
        
        # Condition 2: Moins de 10 graines au total
        total_seeds = sum(self.board)
        if total_seeds < 10:
            # Distribuer les graines restantes
            for i in range(7):
                self.scores['north'] += self.board[i]
            for i in range(7, 14):
                self.scores['south'] += self.board[i]
            
            self.game_over = True
            if self.scores['north'] > self.scores['south']:
                self.winner = 'north'
            elif self.scores['south'] > self.scores['north']:
                self.winner = 'south'
            else:
                self.winner = 'draw'
    
    def reset(self):
        """Réinitialiser la partie"""
        self.__init__()
    
    def get_hint(self, player):
        """Suggérer le meilleur coup pour un joueur"""
        if self.current_player != player:
            return None
        
        player_range = range(7, 14) if player == 'south' else range(0, 7)
        best_move = None
        max_capture = -1
        
        for index in player_range:
            if self.board[index] > 0:
                # Simulation simple du coup
                seeds = self.board[index]
                last_pos = (index + seeds) % 14
                
                # Vérifier si c'est dans le camp adverse
                is_adverse = (player == 'south' and 0 <= last_pos <= 6) or \
                            (player == 'north' and 7 <= last_pos <= 13)
                
                if is_adverse:
                    potential = self.board[last_pos] + 1
                    if 2 <= potential <= 4:
                        if potential > max_capture:
                            max_capture = potential
                            best_move = index
        
        # Si aucun coup ne capture, retourner le premier coup valide
        if best_move is None:
            for index in player_range:
                if self.board[index] > 0:
                    best_move = index
                    break
        
        return best_move
