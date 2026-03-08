"""Thirteen Game - UI Rendering & Input"""
import pygame
from typing import List, Tuple, Optional
from cards import Card, Hand

SCREEN_WIDTH, SCREEN_HEIGHT = 1400, 900
CARD_WIDTH, CARD_HEIGHT = 90, 130
HAND_Y = SCREEN_HEIGHT - 185


class UI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Thirteen")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("segoeui", 24)
        self.small_font = pygame.font.SysFont("segoeui", 18)
        self.big_font = pygame.font.SysFont("segoeui", 38, bold=True)

        self.play_area = pygame.Rect(430, 260, 540, 220)
        self.play_button = pygame.Rect(470, 530, 140, 52)
        self.pass_button = pygame.Rect(630, 530, 140, 52)
        self.restart_button = pygame.Rect(790, 530, 140, 52)

        self.colors = {
            "bg_top": (20, 70, 50),
            "bg_bottom": (12, 45, 32),
            "table_zone": (18, 88, 60),
            "table_outline": (8, 30, 22),

            "card_face": (248, 245, 239),
            "card_border": (40, 40, 40),
            "card_shadow": (0, 0, 0, 50),
            "card_selected": (255, 244, 196),

            "button": (42, 42, 48),
            "button_alt": (70, 70, 78),
            "button_text": (245, 245, 245),

            "text": (245, 245, 245),
            "muted_text": (210, 220, 215),
            "message": (255, 230, 120),
            "active_name": (255, 240, 150),

            "red": (200, 50, 50),
            "black": (30, 30, 30),
        }

    def draw_rounded_rect(self, color, rect, radius=16, width=0):
        pygame.draw.rect(self.screen, color, rect, width=width, border_radius=radius)

    def draw_background(self):
        self.screen.fill(self.colors["bg_bottom"])
        for y in range(SCREEN_HEIGHT):
            blend = y / SCREEN_HEIGHT
            r = int(self.colors["bg_top"][0] * (1 - blend) + self.colors["bg_bottom"][0] * blend)
            g = int(self.colors["bg_top"][1] * (1 - blend) + self.colors["bg_bottom"][1] * blend)
            b = int(self.colors["bg_top"][2] * (1 - blend) + self.colors["bg_bottom"][2] * blend)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))

    def suit_color(self, suit: str):
        return self.colors["red"] if suit in ["♥", "♦"] else self.colors["black"]

    def draw_card(self, card: Card, rect: pygame.Rect, selected: bool = False):
        shadow_rect = rect.move(4, 5)
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, self.colors["card_shadow"], shadow_surf.get_rect(), border_radius=12)
        self.screen.blit(shadow_surf, shadow_rect.topleft)

        face_color = self.colors["card_selected"] if selected else self.colors["card_face"]
        self.draw_rounded_rect(face_color, rect, radius=12)
        self.draw_rounded_rect(self.colors["card_border"], rect, radius=12, width=2)

        rank_text = self.font.render(card.rank, True, self.suit_color(card.suit))
        suit_text = self.font.render(card.suit, True, self.suit_color(card.suit))
        center_text = self.big_font.render(f"{card.rank}{card.suit}", True, self.suit_color(card.suit))

        self.screen.blit(rank_text, (rect.x + 8, rect.y + 6))
        self.screen.blit(suit_text, (rect.x + 8, rect.y + 30))
        self.screen.blit(center_text, center_text.get_rect(center=rect.center))

    def draw_card_back(self, rect: pygame.Rect):
        shadow_rect = rect.move(3, 4)
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, self.colors["card_shadow"], shadow_surf.get_rect(), border_radius=10)
        self.screen.blit(shadow_surf, shadow_rect.topleft)

        self.draw_rounded_rect((52, 76, 140), rect, radius=10)
        self.draw_rounded_rect((235, 235, 245), rect, radius=10, width=2)
        inner = rect.inflate(-14, -14)
        self.draw_rounded_rect((230, 230, 240), inner, radius=8, width=2)

    def draw_hand(self, hand: Hand, selected_indices: Optional[List[int]] = None):
        if selected_indices is None:
            selected_indices = []

        spacing = 55
        x_start = max(40, (SCREEN_WIDTH - ((len(hand.cards) - 1) * spacing + CARD_WIDTH)) // 2)

        for i, card in enumerate(hand.cards):
            y_offset = -24 if i in selected_indices else 0
            rect = pygame.Rect(x_start + i * spacing, HAND_Y + y_offset, CARD_WIDTH, CARD_HEIGHT)
            self.draw_card(card, rect, i in selected_indices)

    def draw_opponent_horizontal(self, hand: Hand, x_start: int, y: int):
        spacing = 18
        for i in range(len(hand.cards)):
            rect = pygame.Rect(x_start + i * spacing, y, 55, 80)
            self.draw_card_back(rect)

    def draw_opponent_vertical(self, hand: Hand, x: int, y_start: int):
        spacing = 18
        for i in range(len(hand.cards)):
            rect = pygame.Rect(x, y_start + i * spacing, 55, 80)
            self.draw_card_back(rect)

    def draw_player_label(self, name: str, card_count: int, x: int, y: int, active: bool = False, center: bool = False):
        color = self.colors["active_name"] if active else self.colors["text"]
        label = self.font.render(f"{name} ({card_count})", True, color)
        rect = label.get_rect(center=(x, y)) if center else label.get_rect(topleft=(x, y))
        self.screen.blit(label, rect)

    def draw_play_area(self, prev_combo: List[Card]):
        self.draw_rounded_rect(self.colors["table_zone"], self.play_area, radius=24)
        self.draw_rounded_rect(self.colors["table_outline"], self.play_area, radius=24, width=3)

        label = self.small_font.render("Current trick", True, self.colors["muted_text"])
        self.screen.blit(label, (self.play_area.x + 18, self.play_area.y + 14))

        if prev_combo:
            total_width = len(prev_combo) * 72
            start_x = self.play_area.centerx - total_width // 2
            for i, card in enumerate(prev_combo):
                rect = pygame.Rect(start_x + i * 72, self.play_area.centery - 55, 90, 130)
                self.draw_card(card, rect)

    def draw_button(self, rect: pygame.Rect, label: str, alt: bool = False):
        color = self.colors["button_alt"] if alt else self.colors["button"]
        self.draw_rounded_rect(color, rect, radius=14)
        self.draw_rounded_rect((230, 230, 230), rect, radius=14, width=2)

        text = self.font.render(label, True, self.colors["button_text"])
        self.screen.blit(text, text.get_rect(center=rect.center))

    def draw_ui(self, hands: List[Hand], player_names: List[str], current_player: int, prev_combo: List[Card], selected: List[int], message: str = ""):
        self.draw_background()

        title = self.big_font.render("Thirteen", True, self.colors["text"])
        self.screen.blit(title, (40, 22))

        # Top player
        top_hand = hands[2]
        top_x = (SCREEN_WIDTH - (len(top_hand.cards) * 18 + 55)) // 2
        self.draw_opponent_horizontal(top_hand, top_x, 40)
        self.draw_player_label(player_names[2], len(top_hand.cards), SCREEN_WIDTH // 2, 30, current_player == 2, center=True)

        # Left player
        self.draw_opponent_vertical(hands[1], 40, 180)
        self.draw_player_label(player_names[1], len(hands[1].cards), 40, 150, current_player == 1)

        # Right player
        self.draw_opponent_vertical(hands[3], SCREEN_WIDTH - 95, 180)
        self.draw_player_label(player_names[3], len(hands[3].cards), SCREEN_WIDTH - 180, 150, current_player == 3)

        # Bottom player
        self.draw_hand(hands[0], selected)
        self.draw_player_label(player_names[0], len(hands[0].cards), SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40, current_player == 0, center=True)

        self.draw_play_area(prev_combo)

        self.draw_button(self.play_button, "Play")
        self.draw_button(self.pass_button, "Pass", alt=True)
        self.draw_button(self.restart_button, "Restart", alt=True)

        if message:
            msg = self.font.render(message, True, self.colors["message"])
            self.screen.blit(msg, (40, SCREEN_HEIGHT - 230))

        hint = self.small_font.render("Select cards, then click Play", True, self.colors["muted_text"])
        self.screen.blit(hint, (40, SCREEN_HEIGHT - 200))

        pygame.display.flip()

    def get_card_at_pos(self, hand: Hand, pos: Tuple[int, int]) -> Tuple[Optional[int], Optional[pygame.Rect]]:
        spacing = 55
        x_start = max(40, (SCREEN_WIDTH - ((len(hand.cards) - 1) * spacing + CARD_WIDTH)) // 2)

        for i in range(len(hand.cards) - 1, -1, -1):
            rect = pygame.Rect(x_start + i * spacing, HAND_Y, CARD_WIDTH, CARD_HEIGHT)
            lifted_rect = rect.move(0, -24)
            if lifted_rect.collidepoint(pos) or rect.collidepoint(pos):
                return i, rect

        return None, None

    def is_play_button_clicked(self, pos: Tuple[int, int]) -> bool:
        return self.play_button.collidepoint(pos)

    def is_pass_button_clicked(self, pos: Tuple[int, int]) -> bool:
        return self.pass_button.collidepoint(pos)

    def is_restart_button_clicked(self, pos: Tuple[int, int]) -> bool:
        return self.restart_button.collidepoint(pos)
