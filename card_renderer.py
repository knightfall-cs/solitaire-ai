import pygame

# --- ROYAL & CLASSIC COLOR PALETTE ---
FELT_GREEN = (10, 62, 37)       # Deep Royal Emerald
FELT_DARK = (6, 38, 22)         # Dark Emerald Shadow
FELT_LIGHT = (18, 90, 54)       # Vibrant Felt Highlight

WHITE = (255, 255, 255)
BLACK = (30, 30, 30)
RED_SUIT = (215, 38, 56)        # Original Vibrant Crimson
BLACK_SUIT = (33, 37, 41)       # Original Charcoal Black
CARD_BG = (252, 252, 252)       # Original Crisp Card White
CARD_BORDER = (180, 190, 200)    # Original Clean Card Border

SLOT_OUTLINE = (180, 142, 40)   # Antiqued Gold Outline
SLOT_BG = (8, 48, 28)           # Dark Velvet Slot

GOLD_HIGHLIGHT = (255, 215, 0)  # Pure Royal Gold
GOLD_ACCENT = (218, 165, 32)    # Golden Rod
CYAN_HIGHLIGHT = (0, 225, 255)
HINT_GLOW = (255, 140, 0)

TOOLBAR_BG = (5, 28, 16)        # Dark Velvet Top Bar
BUTTON_BG = (24, 84, 48)        # Emerald Button
BUTTON_HOVER = (36, 116, 68)    # Hover Emerald
BUTTON_ACTIVE = (128, 0, 32)     # Royal Burgundy Active
TEXT_GOLD = (255, 223, 110)     # Shimmering Gold Text
TEXT_WHITE = (245, 245, 240)

ROYAL_FONT_FAMILY = "Georgia, Times New Roman, DejaVu Serif, Liberation Serif, URW Bookman, serif"
ORIGINAL_CARD_FONT = "DejaVu Sans, Segoe UI Symbol, Arial, sans-serif"


class CardRenderer:
    """
    Dynamic Vector-Style Pygame Card and Slot Renderer.
    Renders crisp cards with the original clean front face style and Royal UI controls.
    """

    def __init__(self, card_width=110, card_height=154):
        self.width = card_width
        self.height = card_height
        self.border_radius = 10

        # Initialize Pygame fonts - Original clean sans-serif for card faces
        pygame.font.init()
        self.font_rank = pygame.font.SysFont(ORIGINAL_CARD_FONT, int(self.height * 0.22), bold=True)
        self.font_suit_small = pygame.font.SysFont(ORIGINAL_CARD_FONT, int(self.height * 0.18), bold=True)
        self.font_suit_center = pygame.font.SysFont(ORIGINAL_CARD_FONT, int(self.height * 0.48), bold=True)
        self.font_slot = pygame.font.SysFont(ORIGINAL_CARD_FONT, int(self.height * 0.35), bold=True)

        # Cache rendered card surfaces to optimize performance
        self._cache = {}

    def get_card_surface(self, card):
        """Returns or creates a cached Pygame surface for a card."""
        if not card.face_up:
            return self.get_card_back_surface()

        key = (card.rank, card.suit)
        if key in self._cache:
            return self._cache[key]

        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Drop shadow & card body
        rect = pygame.Rect(0, 0, self.width, self.height)
        pygame.draw.rect(surf, (0, 0, 0, 50), rect.move(3, 4), border_radius=self.border_radius)
        pygame.draw.rect(surf, CARD_BG, rect, border_radius=self.border_radius)
        pygame.draw.rect(surf, CARD_BORDER, rect, width=2, border_radius=self.border_radius)

        color = RED_SUIT if card.is_red else BLACK_SUIT

        # Top-left rank & suit
        rank_txt = self.font_rank.render(card.rank_str, True, color)
        suit_small = self.font_suit_small.render(card.suit_symbol, True, color)
        suit_small = self.font_suit_small.render(card.suit_symbol, True, color)

        surf.blit(rank_txt, (10, 8))
        surf.blit(suit_small, (12, 8 + rank_txt.get_height() - 4))

        # Bottom-right rank & suit (rotated 180)
        br_surf = pygame.Surface((rank_txt.get_width() + 15, rank_txt.get_height() + suit_small.get_height() + 5), pygame.SRCALPHA)
        br_surf.blit(rank_txt, (0, 0))
        br_surf.blit(suit_small, (2, rank_txt.get_height() - 4))
        rotated_br = pygame.transform.rotate(br_surf, 180)
        surf.blit(rotated_br, (self.width - rotated_br.get_width() - 8, self.height - rotated_br.get_height() - 8))

        # Center suit symbol
        suit_center = self.font_suit_center.render(card.suit_symbol, True, color)
        center_rect = suit_center.get_rect(center=(self.width // 2, self.height // 2 + 5))
        surf.blit(suit_center, center_rect)

        self._cache[key] = surf
        return surf

    def get_card_back_surface(self):
        """Renders the back pattern of a card."""
        key = 'BACK'
        if key in self._cache:
            return self._cache[key]

        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        rect = pygame.Rect(0, 0, self.width, self.height)

        # Shadow & Base
        pygame.draw.rect(surf, (0, 0, 0, 40), rect.move(2, 3), border_radius=self.border_radius)
        pygame.draw.rect(surf, (20, 50, 110), rect, border_radius=self.border_radius)
        pygame.draw.rect(surf, CARD_BORDER, rect, width=2, border_radius=self.border_radius)

        # Inner gold border
        inner_rect = rect.inflate(-12, -12)
        pygame.draw.rect(surf, GOLD_HIGHLIGHT, inner_rect, width=2, border_radius=self.border_radius - 2)

        # Crosshatch pattern
        pattern_surf = pygame.Surface((inner_rect.width, inner_rect.height), pygame.SRCALPHA)
        for x in range(-inner_rect.width, inner_rect.width * 2, 12):
            pygame.draw.line(pattern_surf, (40, 80, 160, 150), (x, 0), (x + inner_rect.height, inner_rect.height), 2)
            pygame.draw.line(pattern_surf, (40, 80, 160, 150), (x, inner_rect.height), (x + inner_rect.height, 0), 2)

        surf.blit(pattern_surf, (6, 6))
        self._cache[key] = surf
        return surf

    def get_slot_surface(self, watermark_symbol=""):
        """Renders empty card slot outline with faint watermark."""
        key = f"SLOT_{watermark_symbol}"
        if key in self._cache:
            return self._cache[key]

        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        rect = pygame.Rect(0, 0, self.width, self.height)

        pygame.draw.rect(surf, SLOT_BG, rect, border_radius=self.border_radius)
        pygame.draw.rect(surf, SLOT_OUTLINE, rect, width=2, border_radius=self.border_radius)

        if watermark_symbol:
            txt = self.font_slot.render(watermark_symbol, True, (40, 120, 75))
            txt_rect = txt.get_rect(center=(self.width // 2, self.height // 2))
            surf.blit(txt, txt_rect)

        self._cache[key] = surf
        return surf

    def draw_highlight(self, surface, pos, color=GOLD_HIGHLIGHT, width=4):
        """Draws glowing selection/hint outline around card position."""
        rect = pygame.Rect(pos[0], pos[1], self.width, self.height)
        pygame.draw.rect(surface, color, rect, width=width, border_radius=self.border_radius + 2)
