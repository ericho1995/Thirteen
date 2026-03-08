"""Thirteen Game - Main Entry"""
import pygame
from cards import Deck, Hand
from game_logic import is_valid_play, AIPlayer
from ui import UI


class ThirteenGame:
    def __init__(self):
        self.deck = Deck()
        self.deck.shuffle()
        self.hands = [Hand(self.deck.deal(13)) for _ in range(4)]
        self.current_player = 0
        self.prev_combo = []
        self.selected = []
        self.ai_players = [AIPlayer() for _ in range(3)]
        self.ui = UI()
        self.message = "Click cards to select, then click play area"
        self.game_over = False
        self.winner = None

    def handle_mouse(self, pos):
        if self.game_over or self.current_player != 0:
            return

        index, _ = self.ui.get_card_at_pos(self.hands[0], pos, self.selected)
        if index is not None:
            if index in self.selected:
                self.selected.remove(index)
            else:
                self.selected.append(index)
            return

        if self.ui.play_area.collidepoint(pos) and self.selected:
            play_combo = [self.hands[0].cards[i] for i in self.selected]

            if is_valid_play(self.prev_combo, play_combo):
                self.prev_combo = sorted(play_combo, key=lambda c: c.value)

                for i in sorted(self.selected, reverse=True):
                    del self.hands[0].cards[i]

                self.selected = []
                self.message = "Played successfully"

                if len(self.hands[0].cards) == 0:
                    self.game_over = True
                    self.winner = "You"
                    self.message = "You win!"
                    return

                self.next_turn()
            else:
                self.message = "Invalid play"

    def next_turn(self):
        self.current_player = (self.current_player + 1) % 4

        while self.current_player != 0 and not self.game_over:
            ai_index = self.current_player - 1
            ai_hand = self.hands[self.current_player]
            ai_play = self.ai_players[ai_index].choose_play(ai_hand, self.prev_combo)

            if ai_play:
                self.prev_combo = sorted(ai_play, key=lambda c: c.value)

                for card in ai_play:
                    ai_hand.cards.remove(card)

                self.message = f"Player {self.current_player + 1} played"

                if len(ai_hand.cards) == 0:
                    self.game_over = True
                    self.winner = f"Player {self.current_player + 1}"
                    self.message = f"{self.winner} wins!"
                    return
            else:
                self.message = f"Player {self.current_player + 1} passed"

            self.current_player = (self.current_player + 1) % 4

    def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse(event.pos)

            self.ui.draw_ui(
                self.hands,
                self.current_player,
                self.prev_combo,
                self.selected,
                self.message
            )

            self.ui.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    game = ThirteenGame()
    game.run()
