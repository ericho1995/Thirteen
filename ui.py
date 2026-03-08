"""Thirteen Game - UI Rendering & Input"""
import pygame
from typing import List, Tuple, Optional
from cards import Card, Hand

SCREEN_WIDTH, SCREEN_HEIGHT = 1400, 900
CARD_WIDTH, CARD_HEIGHT = 70, 100
HAND_Y = SCREEN_HEIGHT - 150


class UI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Thirteen Card Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 28)
        self.big_font = pygame.font.Font(None, 48)
        self.play_area = pygame.Rect(500, 300, 400, 200)
        self.colors = {
            "bg": (20, 40, 60),
            "card_back": (80, 120, 200),
            "card_selected": (255, 255, 100),
            "play_valid": (0, 180, 0),
        }

    def draw_card(self, card: Card, rect: pygame.Rect, selected: bool = False):
        color = self.colors["card_selected"] if selected else self.colors["card_back"]
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, (0, 0, 0), rect, 3)
        text = self.font.render(str(card), True, (255, 255, 255))
        text_rect = text.get_rect(center=rect.center)
        self.screen.blit(text, text_rect)

    def draw_hand(self, hand: Hand, player_idx: int, selected_indices: List[int] = None):
        if selected_indices is None:
            selected_indices = []

        if player_idx == 0:
            x_start = 50
            y = HAND_Y
            spacing = 55
        else:
            x_start = 50 if player_idx % 2 == 0 else SCREEN_WIDTH - 400
            y = 80 + (player_idx * 60)
            spacing = 20

        for i, card in enumerate(hand.cards):
            rect = pygame.Rect(x_start + i * spacing, y, CARD_WIDTH, CARD_HEIGHT)
            self.draw_card(card, rect, i in selected_indices)

    def draw_opponent_hand(self, hand: Hand, player_idx: int):
        x_start = 50 if player_idx % 2 == 0 else SCREEN_WIDTH - 400
        y = 80 + (player_idx * 60)

        for i in range(len(hand.cards)):
            rect = pygame.Rect(x_start + i * 20, y, 50, 70)
            pygame.draw.rect(self.screen, self.colors["card_back"], rect)
            pygame.draw.rect(self.screen, (0, 0, 0), rect, 2)

    def draw_play_area(self, prev_combo: List[Card]):
        pygame.draw.rect(self.screen, self.colors["play_valid"], self.play_area)
        pygame.draw.rect(self.screen, (0, 0, 0), self.play_area, 4)

        if prev_combo:
            start_x = self.play_area.centerx - (len(prev_combo) * 35)
            for i, card in enumerate(prev_combo):
                rect = pygame.Rect(start_x + i * 45, self.play_area.centery - 45, 60, 90)
                self.draw_card(card, rect)

    def draw_ui(self, hands: List[Hand], current_player: int, prev_combo: List[Card], selected: List[int], message: str = ""):
        self.screen.fill(self.colors["bg"])

        self.draw_hand(hands[0], 0, selected)

        for i in range(1, len(hands)):
            self.draw_opponent_hand(hands[i], i)

        self.draw_play_area(prev_combo)

        status = self.big_font.render(f"Player {current_player + 1}'s Turn", True, (255, 255, 255))
        self.screen.blit(status, (50, 30))

        if message:
            msg_surf = self.font.render(message, True, (255, 255, 0))
            self.screen.blit(msg_surf, (50, 85))

        pygame.display.flip()

    def get_card_at_pos(self, hand: Hand, pos: Tuple[int, int], selected: List[int]) -> Tuple[Optional[int], Optional[pygame.Rect]]:
        x_start = 50
        spacing = 55

        for i in range(len(hand.cards)):
            rect = pygame.Rect(x_start + i * spacing, HAND_Y, CARD_WIDTH, CARD_HEIGHT)
            if rect.collidepoint(pos):
                return i, rect
        return None, None
