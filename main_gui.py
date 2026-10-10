import sys
import time
import pygame
from solitaire_engine import SolitaireEngine, Card
from card_renderer import CardRenderer, FELT_GREEN, FELT_DARK, TOOLBAR_BG, BUTTON_BG, BUTTON_HOVER, BUTTON_ACTIVE, TEXT_WHITE, TEXT_GOLD, GOLD_HIGHLIGHT, HINT_GLOW, CYAN_HIGHLIGHT
from animator import AnimationManager

# System Window Setup
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 880
FPS = 60


class SolitaireGUIApp:
    def __init__(self, seed=None):
        pygame.init()
        pygame.font.init()

        self.initial_seed = seed
        if seed is not None:
            import random
            random.seed(seed)

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Solitaire AI - Klondike Animated GUI Game")
        self.clock = pygame.time.Clock()

        # Engine & Rendering
        self.engine = SolitaireEngine()
        self.renderer = CardRenderer(card_width=110, card_height=154)
        self.animator = AnimationManager()

        # UI State
        self.ai_auto_play = False
        self.ai_speed_mult = 1.0
        self.last_ai_step_time = 0
        self.current_hint = None
        self.victory_celebrated = False

        # Drag & Drop State
        self.dragging = False
        self.drag_source = None  # ('tableau', col_idx, card_idx) or ('waste',)
        self.drag_cards = []
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.drag_start_pos = (0, 0)

        # Slot Coordinate Geometry
        self.update_geometry()

        # Fonts - Royal Serif Stack
        ROYAL_FONT = "Georgia, Times New Roman, DejaVu Serif, Liberation Serif, URW Bookman, serif"
        self.font_toolbar = pygame.font.SysFont(ROYAL_FONT, 16, bold=True)
        self.font_status = pygame.font.SysFont(ROYAL_FONT, 19, bold=True)
        self.font_win = pygame.font.SysFont(ROYAL_FONT, 42, bold=True)

        # Buttons Definition: (id, text, rect)
        self.buttons = [
            {'id': 'new', 'text': 'New Game', 'rect': pygame.Rect(20, 12, 110, 36)},
            {'id': 'undo', 'text': 'Undo', 'rect': pygame.Rect(140, 12, 80, 36)},
            {'id': 'hint', 'text': 'AI Hint', 'rect': pygame.Rect(230, 12, 90, 36)},
            {'id': 'ai_bot', 'text': 'AI Auto-Play', 'rect': pygame.Rect(330, 12, 130, 36)},
            {'id': 'speed', 'text': 'Speed: 1x', 'rect': pygame.Rect(470, 12, 110, 36)},
        ]

    def update_geometry(self):
        """Calculates screen positions for all slots."""
        self.card_w = self.renderer.width
        self.card_h = self.renderer.height
        self.margin_x = 40
        self.spacing_x = 30
        self.top_y = 80
        self.tableau_y = 260
        self.hidden_overlap = 14
        self.faceup_overlap = 32

        # Stock & Waste
        self.stock_pos = (self.margin_x, self.top_y)
        self.waste_pos = (self.margin_x + self.card_w + self.spacing_x, self.top_y)

        # Foundations (Spades=1, Hearts=2, Clubs=3, Diamonds=4)
        self.foundation_pos = {}
        found_start_x = self.margin_x + (self.card_w + self.spacing_x) * 3
        for suit_idx, suit_id in enumerate([1, 2, 3, 4]):
            self.foundation_pos[suit_id] = (found_start_x + suit_idx * (self.card_w + self.spacing_x), self.top_y)

        # Tableau Columns (7 columns)
        self.tableau_pos = []
        for i in range(7):
            self.tableau_pos.append((self.margin_x + i * (self.card_w + self.spacing_x), self.tableau_y))

    def get_card_screen_pos(self, location):
        """Gets exact (x, y) screen coordinates for a card or pile slot."""
        loc_type = location[0]
        if loc_type == 'stock':
            return self.stock_pos
        elif loc_type == 'waste':
            return self.waste_pos
        elif loc_type == 'foundation':
            suit = location[1]
            return self.foundation_pos[suit]
        elif loc_type == 'tableau':
            col_idx = location[1]
            card_idx = location[2]
            base_x, base_y = self.tableau_pos[col_idx]
            col = self.engine.tableau[col_idx]

            y_offset = 0
            for idx in range(card_idx):
                if idx < len(col):
                    y_offset += self.faceup_overlap if col[idx].face_up else self.hidden_overlap
            return (base_x, base_y + y_offset)
        return (0, 0)

    # --- EVENT HANDLING ---

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update_ai_bot()
            self.draw()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

            elif event.type == pygame.VIDEORESIZE:
                global WINDOW_WIDTH, WINDOW_HEIGHT
                WINDOW_WIDTH, WINDOW_HEIGHT = event.size
                self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
                self.update_geometry()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.on_left_click(event.pos)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.dragging:
                    self.on_left_release(event.pos)

            elif event.type == pygame.MOUSEMOTION:
                pass

    def on_left_click(self, pos):
        # 1. Check UI Toolbar buttons
        if pos[1] <= 60:
            for btn in self.buttons:
                if btn['rect'].collidepoint(pos):
                    self.handle_button_click(btn['id'])
                    return
            return

        if self.animator.is_animating():
            return

        self.current_hint = None

        # 2. Check Stock click
        stock_rect = pygame.Rect(self.stock_pos[0], self.stock_pos[1], self.card_w, self.card_h)
        if stock_rect.collidepoint(pos):
            self.engine.draw_stock_cards()
            return

        # 3. Check Tableau click / drag
        for col_idx in range(6, -1, -1):
            col = self.engine.tableau[col_idx]
            if not col:
                # Click on empty tableau slot
                col_rect = pygame.Rect(self.tableau_pos[col_idx][0], self.tableau_pos[col_idx][1], self.card_w, self.card_h)
                if col_rect.collidepoint(pos) and self.engine.waste and self.engine.waste[-1].rank == 13:
                    self.engine.move_waste_to_tableau(col_idx)
                    return
            else:
                for card_idx in range(len(col) - 1, -1, -1):
                    card = col[card_idx]
                    card_pos = self.get_card_screen_pos(('tableau', col_idx, card_idx))
                    card_rect = pygame.Rect(card_pos[0], card_pos[1], self.card_w, self.card_h)
                    if card_rect.collidepoint(pos):
                        if card.face_up:
                            # Start Dragging stack
                            self.dragging = True
                            self.drag_source = ('tableau', col_idx, card_idx)
                            self.drag_cards = col[card_idx:]
                            self.drag_start_pos = card_pos
                            self.drag_offset_x = pos[0] - card_pos[0]
                            self.drag_offset_y = pos[1] - card_pos[1]
                        return

        # 4. Check Waste click / drag
        if self.engine.waste:
            waste_rect = pygame.Rect(self.waste_pos[0], self.waste_pos[1], self.card_w, self.card_h)
            if waste_rect.collidepoint(pos):
                card = self.engine.waste[-1]

                # Double-click auto foundation test
                if self.engine.can_move_to_foundation(card):
                    self.engine.move_waste_to_foundation()
                    return

                # Otherwise start dragging
                self.dragging = True
                self.drag_source = ('waste',)
                self.drag_cards = [card]
                self.drag_start_pos = self.waste_pos
                self.drag_offset_x = pos[0] - self.waste_pos[0]
                self.drag_offset_y = pos[1] - self.waste_pos[1]
                return

    def on_left_release(self, pos):
        if not self.dragging:
            return
        self.dragging = False
        source_type = self.drag_source[0]
        moving_card = self.drag_cards[0]

        moved = False

        # Check drop on Tableau
        for target_col in range(7):
            col_pos = self.tableau_pos[target_col]
            target_rect = pygame.Rect(col_pos[0] - 10, self.tableau_y - 10, self.card_w + 20, 500)
            if target_rect.collidepoint(pos):
                if source_type == 'tableau':
                    src_col = self.drag_source[1]
                    card_idx = self.drag_source[2]
                    moved = self.engine.move_tableau_to_tableau(src_col, card_idx, target_col)
                elif source_type == 'waste':
                    moved = self.engine.move_waste_to_tableau(target_col)
                if moved:
                    break

        # Check drop on Foundation (only for single card)
        if not moved and len(self.drag_cards) == 1:
            for suit_id, f_pos in self.foundation_pos.items():
                f_rect = pygame.Rect(f_pos[0], f_pos[1], self.card_w, self.card_h)
                if f_rect.collidepoint(pos):
                    if source_type == 'tableau':
                        src_col = self.drag_source[1]
                        moved = self.engine.move_tableau_to_foundation(src_col)
                    elif source_type == 'waste':
                        moved = self.engine.move_waste_to_foundation()
                    if moved:
                        break

        # If move failed, add snap-back animation
        if not moved:
            start_mouse_pos = (pos[0] - self.drag_offset_x, pos[1] - self.drag_offset_y)
            card_surf = self.renderer.get_card_surface(moving_card)
            self.animator.add_card_animation(card_surf, start_mouse_pos, self.drag_start_pos, duration=0.2)

        self.drag_cards = []
        self.drag_source = None

    def handle_button_click(self, btn_id):
        if btn_id == 'new':
            self.engine.new_game()
            self.ai_auto_play = False
            self.victory_celebrated = False
            self.current_hint = None
            btn = next(b for b in self.buttons if b['id'] == 'ai_bot')
            btn['text'] = 'AI Auto-Play'
        elif btn_id == 'undo':
            self.engine.undo()
            self.current_hint = None
        elif btn_id == 'hint':
            self.trigger_ai_hint()
        elif btn_id == 'ai_bot':
            self.ai_auto_play = not self.ai_auto_play
            btn = next(b for b in self.buttons if b['id'] == 'ai_bot')
            btn['text'] = 'Pause AI' if self.ai_auto_play else 'AI Auto-Play'
        elif btn_id == 'speed':
            if self.ai_speed_mult == 1.0:
                self.ai_speed_mult = 2.0
            elif self.ai_speed_mult == 2.0:
                self.ai_speed_mult = 4.0
            else:
                self.ai_speed_mult = 1.0
            btn = next(b for b in self.buttons if b['id'] == 'speed')
            btn['text'] = f'Speed: {int(self.ai_speed_mult)}x'

    def trigger_ai_hint(self):
        """Calculates AI solver recommendation and highlights source/dest."""
        move = self.engine.get_ai_best_move()
        if not move:
            self.current_hint = None
            return

        action = move[0]
        if action == 'draw_stock':
            self.current_hint = {'src': self.stock_pos, 'dest': self.waste_pos}
        elif action == 'tableau_to_foundation':
            src_col = move[1]
            src_pos = self.get_card_screen_pos(('tableau', src_col, len(self.engine.tableau[src_col]) - 1))
            dest_suit = self.engine.tableau[src_col][-1].suit
            dest_pos = self.foundation_pos[dest_suit]
            self.current_hint = {'src': src_pos, 'dest': dest_pos}
        elif action == 'waste_to_foundation':
            src_pos = self.waste_pos
            dest_suit = self.engine.waste[-1].suit
            dest_pos = self.foundation_pos[dest_suit]
            self.current_hint = {'src': src_pos, 'dest': dest_pos}
        elif action == 'tableau_to_tableau':
            src_col, card_idx, dest_col = move[1], move[2], move[3]
            src_pos = self.get_card_screen_pos(('tableau', src_col, card_idx))
            dest_card_idx = len(self.engine.tableau[dest_col])
            dest_pos = self.get_card_screen_pos(('tableau', dest_col, dest_card_idx))
            self.current_hint = {'src': src_pos, 'dest': dest_pos}
        elif action == 'waste_to_tableau':
            dest_col = move[1]
            src_pos = self.waste_pos
            dest_card_idx = len(self.engine.tableau[dest_col])
            dest_pos = self.get_card_screen_pos(('tableau', dest_col, dest_card_idx))
            self.current_hint = {'src': src_pos, 'dest': dest_pos}

    def update_ai_bot(self):
        """Executes AI solver turns automatically when Auto-Play is enabled."""
        if not self.ai_auto_play or self.animator.is_animating() or self.dragging:
            return

        if self.engine.is_won() or self.engine.is_stalemate():
            self.ai_auto_play = False
            btn = next(b for b in self.buttons if b['id'] == 'ai_bot')
            btn['text'] = 'AI Auto-Play'
            return

        now = time.time()
        delay = 0.4 / self.ai_speed_mult
        if now - self.last_ai_step_time >= delay:
            self.last_ai_step_time = now
            moved = self.engine.execute_ai_step()
            if not moved or self.engine.is_won() or self.engine.is_stalemate():
                self.ai_auto_play = False
                btn = next(b for b in self.buttons if b['id'] == 'ai_bot')
                btn['text'] = 'AI Auto-Play'

    # --- RENDERING ENGINE ---

    def draw(self):
        # 1. Background Felt Gradient
        self.screen.fill(FELT_GREEN)
        pygame.draw.rect(self.screen, FELT_DARK, (0, 0, WINDOW_WIDTH, 60))

        # 2. Render Toolbar Buttons
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            rect = btn['rect']
            is_hover = rect.collidepoint(mouse_pos)
            is_active = (btn['id'] == 'ai_bot' and self.ai_auto_play)
            bg = BUTTON_ACTIVE if is_active else (BUTTON_HOVER if is_hover else BUTTON_BG)

            pygame.draw.rect(self.screen, bg, rect, border_radius=6)
            pygame.draw.rect(self.screen, (212, 175, 55), rect, width=1, border_radius=6)  # Metallic Gold Border

            txt = self.font_toolbar.render(btn['text'], True, TEXT_GOLD if is_hover else TEXT_WHITE)
            txt_rect = txt.get_rect(center=rect.center)
            self.screen.blit(txt, txt_rect)

        # 3. Status HUD (Score, Moves, Victory, Stalemate)
        status_str = f"Score: {self.engine.score}   |   Moves: {self.engine.move_count}"
        if self.engine.is_won():
            status_str += "   |   GAME WON!"
        elif self.engine.is_stalemate():
            status_str += "   |   NO MORE MOVES!"
        elif self.ai_auto_play:
            status_str += "   |   AI Playing..."

        txt_status = self.font_status.render(status_str, True, (255, 223, 110))  # Royal Gold HUD
        self.screen.blit(txt_status, (600, 18))

        # 4. Draw Slots (Stock, Waste, Foundations, Tableau)
        # Stock Slot
        if not self.engine.stock:
            slot_surf = self.renderer.get_slot_surface("Draw")
            self.screen.blit(slot_surf, self.stock_pos)
        else:
            back_surf = self.renderer.get_card_back_surface()
            self.screen.blit(back_surf, self.stock_pos)

        # Waste Slot
        if not self.engine.waste:
            self.screen.blit(self.renderer.get_slot_surface(), self.waste_pos)
        else:
            top_waste = self.engine.waste[-1]
            if not (self.dragging and self.drag_source == ('waste',)):
                card_surf = self.renderer.get_card_surface(top_waste)
                self.screen.blit(card_surf, self.waste_pos)

        # Foundation Slots
        for suit_id, pos in self.foundation_pos.items():
            pile = self.engine.foundation[suit_id]
            symbol = Card.SUIT_SYMBOLS[suit_id]
            if not pile:
                self.screen.blit(self.renderer.get_slot_surface(symbol), pos)
            else:
                card_surf = self.renderer.get_card_surface(pile[-1])
                self.screen.blit(card_surf, pos)

        # Tableau Columns
        for col_idx in range(7):
            col = self.engine.tableau[col_idx]
            base_pos = self.tableau_pos[col_idx]
            if not col:
                self.screen.blit(self.renderer.get_slot_surface(), base_pos)
            else:
                for card_idx, card in enumerate(col):
                    # Skip rendering cards currently being dragged
                    if self.dragging and self.drag_source[0] == 'tableau' and self.drag_source[1] == col_idx and card_idx >= self.drag_source[2]:
                        continue
                    pos = self.get_card_screen_pos(('tableau', col_idx, card_idx))
                    card_surf = self.renderer.get_card_surface(card)
                    self.screen.blit(card_surf, pos)

        # 5. Render AI Hint Highlights
        if self.current_hint:
            self.renderer.draw_highlight(self.screen, self.current_hint['src'], color=HINT_GLOW, width=4)
            self.renderer.draw_highlight(self.screen, self.current_hint['dest'], color=CYAN_HIGHLIGHT, width=4)

        # 6. Render Active Card Dragging Stack
        if self.dragging and self.drag_cards:
            mouse_x, mouse_y = mouse_pos
            curr_x = mouse_x - self.drag_offset_x
            curr_y = mouse_y - self.drag_offset_y

            for idx, card in enumerate(self.drag_cards):
                card_surf = self.renderer.get_card_surface(card)
                self.screen.blit(card_surf, (curr_x, curr_y + idx * self.faceup_overlap))
                self.renderer.draw_highlight(self.screen, (curr_x, curr_y + idx * self.faceup_overlap), color=GOLD_HIGHLIGHT, width=3)

        # 7. Render Sliding Animations & Particles
        self.animator.update_and_draw(self.screen)

        # 8. Victory Celebration
        if self.engine.is_won():
            if not self.victory_celebrated:
                self.victory_celebrated = True
                card_surfs = [self.renderer.get_card_surface(c) for c in self.engine.foundation[1]]
                positions = [self.foundation_pos[1] for _ in range(len(card_surfs))]
                self.animator.start_victory_cascade(card_surfs, positions)

            win_txt = self.font_win.render("CONGRATULATIONS! YOU WON!", True, GOLD_HIGHLIGHT)
            win_rect = win_txt.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            pygame.draw.rect(self.screen, (0, 0, 0, 180), win_rect.inflate(40, 20), border_radius=12)
            self.screen.blit(win_txt, win_rect)

        pygame.display.flip()


if __name__ == '__main__':
    seed_arg = None
    if '--seed' in sys.argv:
        try:
            seed_idx = sys.argv.index('--seed')
            seed_arg = int(sys.argv[seed_idx + 1])
        except (IndexError, ValueError):
            seed_arg = None
    app = SolitaireGUIApp(seed=seed_arg)
    app.run()
