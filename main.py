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
        self.message = "Select cards, then click Play. Click Pass to pass."
        self.game_over = False
        self.winner = None
        self.passed_players = set()
        self.last_player_to_play = 0
        self.ui = UI()
        self.reset_game()

    def reset_game(self):
        self.deck = Deck()
        self.deck.shuffle()
        self.hands = [Hand(self.deck.deal(13)) for _ in range(4)]
        self.current_player = 0
        self.prev_combo = []
        self.selected = []
        self.ai_players = [AIPlayer() for _ in range(3)]
        self.message = "Select cards, then click Play. Click Pass to pass."
        self.game_over = False
        self.winner = None
        self.passed_players = set()
        self.last_player_to_play = 0

    def handle_mouse(self, pos):
        if self.game_over or self.current_player != 0:
            return

        index, _ = self.ui.get_card_at_pos(self.hands[0], pos)
        if index is not None:
            if index in self.selected:
                self.selected.remove(index)
            else:
                self.selected.append(index)
            return

        if self.ui.is_play_button_clicked(pos):
            self.handle_play()
            return

        if self.ui.is_pass_button_clicked(pos):
            self.handle_pass()
            return
        
        if self.ui.is_restart_button_clicked(pos):
            self.reset_game()
            return

        if self.game_over or self.current_player != 0:
            return

    def handle_play(self):
        if not self.selected:
            self.message = "No cards selected"
            return

        play_combo = [self.hands[0].cards[i] for i in self.selected]

        if not is_valid_play(self.prev_combo, play_combo):
            self.message = "Invalid play"
            return

        self.prev_combo = sorted(play_combo, key=lambda c: c.value)
        self.hands[0].remove_cards(self.selected)
        self.selected = []
        self.passed_players = set()
        self.last_player_to_play = 0
        self.message = "You played"

        if len(self.hands[0].cards) == 0:
            self.game_over = True
            self.winner = "You"
            self.message = "You win!"
            return

        self.next_turn()

    def handle_pass(self):
        if not self.prev_combo:
            self.message = "You cannot pass on a fresh trick"
            return

        self.passed_players.add(0)
        self.selected = []
        self.message = "You passed"
        self.next_turn()

    def reset_trick_if_needed(self):
        active_players = [i for i in range(4) if len(self.hands[i].cards) > 0]
        if len(self.passed_players) >= len(active_players) - 1:
            self.prev_combo = []
            self.passed_players = set()
            self.current_player = self.last_player_to_play
            self.message = f"Trick cleared. Player {self.current_player + 1} leads."

    def next_turn(self):
        while not self.game_over:
            self.current_player = (self.current_player + 1) % 4

            if len(self.hands[self.current_player].cards) == 0:
                continue

            self.reset_trick_if_needed()

            if self.current_player == 0:
                return

            ai_index = self.current_player - 1
            ai_hand = self.hands[self.current_player]
            ai_play = self.ai_players[ai_index].choose_play(ai_hand, self.prev_combo)

            if ai_play:
                self.prev_combo = sorted(ai_play, key=lambda c: c.value)
                ai_hand.remove_card_objects(ai_play)
                self.passed_players = set()
                self.last_player_to_play = self.current_player
                self.message = f"Player {self.current_player + 1} played"

                if len(ai_hand.cards) == 0:
                    self.game_over = True
                    self.winner = f"Player {self.current_player + 1}"
                    self.message = f"{self.winner} wins!"
                    return
            else:
                self.passed_players.add(self.current_player)
                self.message = f"Player {self.current_player + 1} passed"

            active_players = [i for i in range(4) if len(self.hands[i].cards) > 0]
            if len(self.passed_players) >= len(active_players) - 1:
                self.prev_combo = []
                self.passed_players = set()
                self.current_player = self.last_player_to_play

                if self.current_player == 0:
                    self.message = "Trick cleared. Your lead."
                    return
                else:
                    self.message = f"Trick cleared. Player {self.current_player + 1} leads."

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
