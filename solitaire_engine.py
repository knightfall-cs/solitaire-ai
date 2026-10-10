import random
import copy
import math
import time
import json

class Card:
    """
    Represents a playing card.
    rank: 1 (Ace) to 13 (King)
    suit: 1 (Spades), 2 (Hearts), 3 (Clubs), 4 (Diamonds)
    color: 1 (Black: Spades/Clubs), 2 (Red: Hearts/Diamonds)
    face_up: bool
    """
    SUIT_NAMES = {1: 'Spades', 2: 'Hearts', 3: 'Clubs', 4: 'Diamonds'}
    SUIT_SYMBOLS = {1: '♠', 2: '♥', 3: '♣', 4: '♦'}
    RANK_NAMES = {1: 'A', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7',
                  8: '8', 9: '9', 10: '10', 11: 'J', 12: 'Q', 13: 'K'}

    def __init__(self, rank, color, suit, face_up=True):
        self.rank = rank
        self.color = color
        self.suit = suit
        self.face_up = face_up

    @property
    def is_red(self):
        return self.color == 2

    @property
    def is_black(self):
        return self.color == 1

    @property
    def rank_str(self):
        return Card.RANK_NAMES.get(self.rank, str(self.rank))

    @property
    def suit_symbol(self):
        return Card.SUIT_SYMBOLS.get(self.suit, '')

    def to_legacy_list(self):
        """Converts to notebook legacy representation: [rank, color, suit]"""
        return [self.rank, self.color, self.suit]

    @classmethod
    def from_legacy_list(cls, l, face_up=True):
        if not l or l == -1 or l == 0:
            return None
        return cls(rank=l[0], color=l[1], suit=l[2], face_up=face_up)

    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return self.rank == other.rank and self.suit == other.suit and self.color == other.color

    def __repr__(self):
        if not self.face_up:
            return "[🂠 Back]"
        return f"[{self.rank_str}{self.suit_symbol}]"


class SolitaireEngine:
    """
    Klondike Solitaire Engine & Solver.
    Faithfully replicates the solver logic from InternalProcessor.ipynb
    """

    def __init__(self):
        self.mid_deck_strats = True
        self.random_strats = False
        self.board_range_val = 1
        self.new_game()

    @staticmethod
    def generate_52_deck():
        deck = []
        for r in range(1, 14):
            for s in range(1, 5):
                color = 1 if s in (1, 3) else 2
                deck.append(Card(r, color, s, face_up=False))
        return deck

    def new_game(self):
        self.deck52 = self.generate_52_deck()
        random.shuffle(self.deck52)

        # Tableau: list of 7 columns. Each column is a list of Card objects.
        self.tableau = [[] for _ in range(7)]
        for i in range(7):
            for j in range(i):
                card = self.deck52.pop()
                card.face_up = False
                self.tableau[i].append(card)
            card = self.deck52.pop()
            card.face_up = True
            self.tableau[i].append(card)

        # Stock deck: remaining cards (face down)
        self.stock = self.deck52
        for c in self.stock:
            c.face_up = False

        # Waste pile: cards drawn from stock
        self.waste = []

        # Foundations: 4 piles [Spades (1), Hearts (2), Clubs (3), Diamonds (4)]
        self.foundation = {1: [], 2: [], 3: [], 4: []}

        # Solver & Game Over tracking structures
        self.score = 0
        self.move_count = 0
        self.deck_loc = 0
        self.last_shift = False
        self.stock_draws_without_card_move = 0
        self.history = []  # Undo stack

        # Revealed cards tracking for engine logic
        self.rev = []
        for col in self.tableau:
            if col and col[-1].face_up:
                self.rev.append(col[-1].to_legacy_list())

    def save_snapshot(self):
        """Saves current state for Undo capability."""
        if not getattr(self, 'enable_history', True):
            return
        snapshot = {
            'tableau': copy.deepcopy(self.tableau),
            'stock': copy.deepcopy(self.stock),
            'waste': copy.deepcopy(self.waste),
            'foundation': copy.deepcopy(self.foundation),
            'score': self.score,
            'move_count': self.move_count,
            'rev': copy.deepcopy(self.rev),
            'deck_loc': self.deck_loc,
            'last_shift': self.last_shift,
            'stock_draws_without_card_move': self.stock_draws_without_card_move,
            'board_range_val': self.board_range_val
        }
        self.history.append(snapshot)
        if len(self.history) > 100:
            self.history.pop(0)

    def undo(self):
        if not self.history:
            return False
        snap = self.history.pop()
        self.tableau = snap['tableau']
        self.stock = snap['stock']
        self.waste = snap['waste']
        self.foundation = snap['foundation']
        self.score = snap['score']
        self.move_count = snap['move_count']
        self.rev = snap['rev']
        self.deck_loc = snap['deck_loc']
        self.last_shift = snap['last_shift']
        self.stock_draws_without_card_move = snap.get('stock_draws_without_card_move', 0)
        self.board_range_val = snap['board_range_val']
        return True

    def can_move_to_tableau(self, card, target_col_idx):
        """Checks if a card can be placed on target tableau column."""
        col = self.tableau[target_col_idx]
        if not col:
            return card.rank == 13  # Only Kings on empty columns
        top_card = col[-1]
        if not top_card.face_up:
            return False
        return (card.rank == top_card.rank - 1) and (card.color != top_card.color)

    def can_move_to_foundation(self, card):
        """Checks if a card can be moved to its suit foundation pile."""
        pile = self.foundation[card.suit]
        if not pile:
            return card.rank == 1  # Ace
        return card.rank == pile[-1].rank + 1

    def draw_stock_cards(self):
        """Draws cards from stock to waste (3 at a time or remaining)."""
        self.save_snapshot()
        self.stock_draws_without_card_move += 1

        if not self.stock:
            # Recycle waste back to stock
            if not self.waste:
                return 0
            self.stock = list(reversed(self.waste))
            for c in self.stock:
                c.face_up = False
            self.waste = []
            self.score = max(0, self.score - 20)
            return len(self.stock)

        count = min(3, len(self.stock))
        drawn = []
        for _ in range(count):
            c = self.stock.pop()
            c.face_up = True
            drawn.append(c)
            self.waste.append(c)
            c_leg = c.to_legacy_list()
            if c_leg not in self.rev:
                self.rev.append(c_leg)
        self.move_count += 1
        return count

    def move_tableau_to_tableau(self, src_col, card_idx, dest_col):
        """Moves a stack of face-up cards from src_col starting at card_idx to dest_col."""
        if src_col == dest_col:
            return False
        moving_cards = self.tableau[src_col][card_idx:]
        if not moving_cards or not moving_cards[0].face_up:
            return False
        if not self.can_move_to_tableau(moving_cards[0], dest_col):
            return False

        self.save_snapshot()
        self.stock_draws_without_card_move = 0
        self.tableau[src_col] = self.tableau[src_col][:card_idx]
        self.tableau[dest_col].extend(moving_cards)

        # Reveal new top card of source column if face down
        if self.tableau[src_col] and not self.tableau[src_col][-1].face_up:
            self.tableau[src_col][-1].face_up = True
            self.score += 20
            c_leg = self.tableau[src_col][-1].to_legacy_list()
            if c_leg not in self.rev:
                self.rev.append(c_leg)

        self.move_count += 1
        return True

    def move_tableau_to_foundation(self, src_col):
        """Moves the top card of a tableau column to foundation."""
        if not self.tableau[src_col]:
            return False
        card = self.tableau[src_col][-1]
        if not card.face_up or not self.can_move_to_foundation(card):
            return False

        self.save_snapshot()
        self.stock_draws_without_card_move = 0
        c = self.tableau[src_col].pop()
        self.foundation[c.suit].append(c)
        self.score += 100

        if self.tableau[src_col] and not self.tableau[src_col][-1].face_up:
            self.tableau[src_col][-1].face_up = True
            self.score += 20
            c_leg = self.tableau[src_col][-1].to_legacy_list()
            if c_leg not in self.rev:
                self.rev.append(c_leg)

        self.move_count += 1
        return True

    def move_waste_to_tableau(self, dest_col):
        """Moves top card of waste pile to tableau column."""
        if not self.waste:
            return False
        card = self.waste[-1]
        if not self.can_move_to_tableau(card, dest_col):
            return False

        self.save_snapshot()
        self.stock_draws_without_card_move = 0
        c = self.waste.pop()
        self.tableau[dest_col].append(c)
        self.score += 20
        self.move_count += 1
        return True

    def move_waste_to_foundation(self):
        """Moves top card of waste pile to foundation."""
        if not self.waste:
            return False
        card = self.waste[-1]
        if not self.can_move_to_foundation(card):
            return False

        self.save_snapshot()
        self.stock_draws_without_card_move = 0
        c = self.waste.pop()
        self.foundation[c.suit].append(c)
        self.score += 100
        self.move_count += 1
        return True

    def is_won(self):
        """Returns True if all 52 cards are on foundation piles."""
        return sum(len(p) for p in self.foundation.values()) == 52

    def is_stalemate(self):
        """Returns True if no playable moves remain after stock cycles."""
        max_draws = (len(self.stock) + len(self.waste)) * 2 + 10
        return self.stock_draws_without_card_move >= max_draws

    # --- AI SOLVER LOGIC (Refactored from InternalProcessor.ipynb) ---

    def _board_range(self, bR):
        mins = []
        for suit in range(1, 5):
            pile = self.foundation[suit]
            mins.append(pile[-1].rank if pile else 0)
        return min(mins) + bR if mins else bR

    def get_tableau_moves(self):
        """Calculates valid moves originating from tableau columns."""
        moves = []
        for i, col in enumerate(self.tableau):
            if not col:
                continue

            # Check moving top card of column to foundation
            top_card = col[-1]
            if top_card.face_up:
                suit_pile = self.foundation[top_card.suit]
                foundation_rank = suit_pile[-1].rank if suit_pile else 0
                if top_card.rank == foundation_rank + 1 and top_card.rank <= self._board_range(self.board_range_val):
                    hidden_under = sum(1 for c in col if not c.face_up)
                    moves.append((-1, (1, i, top_card.suit - 1), top_card.rank, hidden_under))

            # Check moving a sequence starting from first face-up card
            first_faceup_idx = next((idx for idx, c in enumerate(col) if c.face_up), None)
            if first_faceup_idx is not None:
                first_card = col[first_faceup_idx]
                for target_idx in range(7):
                    if target_idx != i and self.can_move_to_tableau(first_card, target_idx):
                        hidden_under = sum(1 for c in col if not c.face_up)
                        if hidden_under == 0 and first_card.rank == 13 and not self.tableau[target_idx]:
                            continue
                        moves.append((-1, (0, i, target_idx), first_card.rank, hidden_under))

        moves.sort(key=lambda m: m[3], reverse=True)
        return moves

    def get_waste_moves(self):
        """Calculates valid moves from current waste card."""
        moves = []
        if not self.waste:
            return moves
        card = self.waste[-1]

        # Check waste to foundation
        suit_pile = self.foundation[card.suit]
        foundation_rank = suit_pile[-1].rank if suit_pile else 0
        if card.rank == foundation_rank + 1:
            moves.append((0, (1, 0, card.suit - 1), card.rank))

        # Check waste to tableau
        for target_idx in range(7):
            if self.can_move_to_tableau(card, target_idx):
                moves.append((0, (0, 0, target_idx), card.rank))

        return moves

    def get_all_moves(self):
        """Combines all legal engine moves."""
        t_moves = self.get_tableau_moves()
        w_moves = self.get_waste_moves()
        return t_moves + w_moves

    def get_ai_best_move(self):
        """
        Returns the top priority move calculated by solver heuristics.
        Returns tuple describing action, or None if no moves available or stalemate.
        """
        if self.is_stalemate():
            return None

        moves = self.get_all_moves()
        if not moves:
            if (self.stock or self.waste) and not self.is_stalemate():
                return ('draw_stock',)
            return None

        # Prioritize foundation moves
        foundation_moves = [m for m in moves if m[1][0] == 1]
        if foundation_moves:
            m = foundation_moves[0]
            if m[0] == -1:
                return ('tableau_to_foundation', m[1][1])
            else:
                return ('waste_to_foundation',)

        # Otherwise pick top tableau or waste move
        m = moves[0]
        if m[0] == -1:
            src_col = m[1][1]
            dest_col = m[1][2]
            first_faceup_idx = next(idx for idx, c in enumerate(self.tableau[src_col]) if c.face_up)
            return ('tableau_to_tableau', src_col, first_faceup_idx, dest_col)
        else:
            dest_col = m[1][2]
            return ('waste_to_tableau', dest_col)

    def execute_ai_step(self):
        """Executes one step of the AI solver."""
        action = self.get_ai_best_move()
        if not action:
            return False

        kind = action[0]
        if kind == 'draw_stock':
            self.draw_stock_cards()
            return True
        elif kind == 'tableau_to_foundation':
            return self.move_tableau_to_foundation(action[1])
        elif kind == 'waste_to_foundation':
            return self.move_waste_to_foundation()
        elif kind == 'tableau_to_tableau':
            return self.move_tableau_to_tableau(action[1], action[2], action[3])
        elif kind == 'waste_to_tableau':
            return self.move_waste_to_tableau(action[1])

        return False

    def simulate_game(self, max_steps=600):
        """
        Executes automated AI solver steps until terminal state (win or stalemate).
        Returns a dict summary of the completed game.
        """
        steps = 0
        while steps < max_steps:
            if self.is_won() or self.is_stalemate():
                break
            moved = self.execute_ai_step()
            if not moved:
                break
            steps += 1

        cards_on_found = sum(len(p) for p in self.foundation.values())
        return {
            'won': self.is_won() or cards_on_found == 52,
            'moves': steps,
            'score': self.score,
            'cards_cleared': cards_on_found,
            'foundations': {suit: len(pile) for suit, pile in self.foundation.items()}
        }

    @classmethod
    def run_benchmark(cls, num_games=1000, start_seed=10000, export_path=None):
        """
        Executes an isolated Monte Carlo benchmark across num_games.
        Returns a comprehensive dictionary with summary statistics and winning seeds.
        """
        engine = cls()
        engine.enable_history = False

        start_time = time.time()
        wins = 0
        stalemates = 0
        scores = []
        moves_per_win = []
        foundation_counts = []
        winning_games = []

        brackets = {
            '0-10 cards': 0,
            '11-20 cards': 0,
            '21-30 cards': 0,
            '31-40 cards': 0,
            '41-51 cards': 0,
            '52 cards (WIN)': 0
        }

        for i in range(num_games):
            seed = start_seed + i
            random.seed(seed)
            engine.new_game()
            engine.enable_history = False

            res = engine.simulate_game()
            scores.append(res['score'])
            cards_cleared = res['cards_cleared']
            foundation_counts.append(cards_cleared)

            if res['won']:
                wins += 1
                moves_per_win.append(res['moves'])
                brackets['52 cards (WIN)'] += 1
                winning_games.append({
                    'seed': seed,
                    'moves': res['moves'],
                    'score': res['score'],
                    'foundations': res['foundations']
                })
            else:
                stalemates += 1
                if cards_cleared <= 10:
                    brackets['0-10 cards'] += 1
                elif cards_cleared <= 20:
                    brackets['11-20 cards'] += 1
                elif cards_cleared <= 30:
                    brackets['21-30 cards'] += 1
                elif cards_cleared <= 40:
                    brackets['31-40 cards'] += 1
                else:
                    brackets['41-51 cards'] += 1

        elapsed = time.time() - start_time
        win_rate = (wins / num_games) * 100
        avg_score = sum(scores) / len(scores) if scores else 0
        avg_moves_win = sum(moves_per_win) / len(moves_per_win) if moves_per_win else 0
        avg_found_cards = sum(foundation_counts) / len(foundation_counts) if foundation_counts else 0

        data = {
            'metadata': {
                'total_games': num_games,
                'start_seed': start_seed,
                'execution_time_seconds': round(elapsed, 3),
                'games_per_second': round(num_games / elapsed, 1) if elapsed > 0 else 0
            },
            'summary': {
                'wins': wins,
                'stalemates': stalemates,
                'win_rate_percent': round(win_rate, 2),
                'average_score': round(avg_score, 1),
                'average_turns_per_win': round(avg_moves_win, 1),
                'average_foundation_cards': round(avg_found_cards, 1),
                'distribution': brackets
            },
            'winning_seeds': winning_games
        }

        if export_path:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

        return data

