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
        self.play_button = pygame.Rect(500, 530, 140, 50)
        self.pass_button = pygame.Rect(660, 530, 140, 50)
        self.restart_button = pygame.Rect(820, 530, 140, 50)


        self.colors = {
            "bg": (20, 40, 60),
            "card_face": (80, 120, 200),
            "card_selected": (255, 255, 100),
            "play_area": (0, 180, 0),
            "button": (70, 70, 70),
            "button_text": (255, 255, 255),
            "text": (255, 255, 255),
            "message": (255, 255, 0),
            "outline": (0, 0, 0),
        }

    def draw_card(self, card: Card, rect: pygame.Rect, selected: bool = False):
        color = self.colors["card_selected"] if selected else self.colors["card_face"]
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, self.colors["outline"], rect, 3)

        text = self.font.render(str(card), True, self.colors["text"])
        text_rect = text.get_rect(center=rect.center)
        self.screen.blit(text, text_rect)

    def draw_card_back(self, rect: pygame.Rect):
        pygame.draw.rect(self.screen, self.colors["card_face"], rect)
        pygame.draw.rect(self.screen, self.colors["outline"], rect, 2)

    def draw_hand(self, hand: Hand, selected_indices: Optional[List[int]] = None):
        if selected_indices is None:
            selected_indices = []

        x_start = 50
        spacing = 55

        for i, card in enumerate(hand.cards):
            y_offset = -20 if i in selected_indices else 0
            rect = pygame.Rect(x_start + i * spacing, HAND_Y + y_offset, CARD_WIDTH, CARD_HEIGHT)
            self.draw_card(card, rect, i in selected_indices)

    def draw_opponent_hand(self, hand: Hand, player_idx: int):
        if player_idx == 1:
            x_start, y, spacing = 50, 80, 20
        elif player_idx == 2:
            x_start, y, spacing = SCREEN_WIDTH - 400, 80, 20
        else:
            x_start, y, spacing = 500, 80, 20

        for i in range(len(hand.cards)):
            rect = pygame.Rect(x_start + i * spacing, y, 50, 70)
            self.draw_card_back(rect)

    def draw_play_area(self, prev_combo: List[Card]):
        pygame.draw.rect(self.screen, self.colors["play_area"], self.play_area)
        pygame.draw.rect(self.screen, self.colors["outline"], self.play_area, 4)

        label = self.font.render("Play Area", True, self.colors["text"])
        self.screen.blit(label, (self.play_area.x + 10, self.play_area.y + 10))

        if prev_combo:
            total_width = len(prev_combo) * 45
            start_x = self.play_area.centerx - total_width // 2
            for i, card in enumerate(prev_combo):
                rect = pygame.Rect(start_x + i * 45, self.play_area.centery - 40, 60, 90)
                self.draw_card(card, rect)

    def draw_button(self, rect: pygame.Rect, label: str):
        pygame.draw.rect(self.screen, self.colors["button"], rect)
        pygame.draw.rect(self.screen, self.colors["outline"], rect, 2)
        text = self.font.render(label, True, self.colors["button_text"])
        text_rect = text.get_rect(center=rect.center)
        self.screen.blit(text, text_rect)

    def is_restart_button_clicked(self, pos: Tuple[int, int]) -> bool:
        return self.restart_button.collidepoint(pos)


    def draw_ui(self, hands: List[Hand], current_player: int, prev_combo: List[Card], selected: List[int], message: str = ""):
        self.screen.fill(self.colors["bg"])

        self.draw_hand(hands[0], selected)

        for i in range(1, len(hands)):
            self.draw_opponent_hand(hands[i], i)

        self.draw_play_area(prev_combo)
        self.draw_button(self.play_button, "Play")
        self.draw_button(self.pass_button, "Pass")
        self.draw_button(self.restart_button, "Restart")

        status = self.big_font.render(f"Player {current_player + 1}'s Turn", True, self.colors["text"])
        self.screen.blit(status, (50, 30))

        counts = self.font.render(
            " | ".join([f"P{i+1}: {len(hand.cards)} cards" for i, hand in enumerate(hands)]),
            True,
            self.colors["text"],
        )
        self.screen.blit(counts, (50, 90))

        if message:
            msg_surf = self.font.render(message, True, self.colors["message"])
            self.screen.blit(msg_surf, (50, 120))

        pygame.display.flip()

    def get_card_at_pos(self, hand: Hand, pos: Tuple[int, int]) -> Tuple[Optional[int], Optional[pygame.Rect]]:
        x_start = 50
        spacing = 55

        for i in range(len(hand.cards) - 1, -1, -1):
            rect = pygame.Rect(x_start + i * spacing, HAND_Y, CARD_WIDTH, CARD_HEIGHT)
            if rect.collidepoint(pos):
                return i, rect

        return None, None

    def is_play_button_clicked(self, pos: Tuple[int, int]) -> bool:
        return self.play_button.collidepoint(pos)

    def is_pass_button_clicked(self, pos: Tuple[int, int]) -> bool:
        return self.pass_button.collidepoint(pos)
