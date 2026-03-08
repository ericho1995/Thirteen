"""Thirteen Game - Main Entry"""
import pygame
import random
from cards import Deck, Hand
from game_logic import is_valid_play, AIPlayer
from ui import UI


class ThirteenGame:
    def __init__(self):
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
        name_pool = [
            "Mia", "Ethan", "Zoe", "Lucas", "Ava", "Noah",
            "Chloe", "Liam", "Sophie", "Jack", "Ella", "Leo",
            "Nina", "Oscar", "Ruby", "Max"
        ]
        random.shuffle(name_pool)
        self.player_names = ["You"] + name_pool[:3]


    def active_players(self):
        return [i for i in range(4) if len(self.hands[i].cards) > 0]

    def next_active_player(self, start_player):
        active = self.active_players()
        if len(active) <= 1:
            return start_player

        player = (start_player + 1) % 4
        while len(self.hands[player].cards) == 0:
            player = (player + 1) % 4
        return player

    def next_eligible_player(self, start_player):
        eligible = [
            i for i in range(4)
            if len(self.hands[i].cards) > 0 and i not in self.passed_players
        ]

        if not eligible:
            return self.last_player_to_play

        player = (start_player + 1) % 4
        while True:
            if len(self.hands[player].cards) > 0 and player not in self.passed_players:
                return player
            player = (player + 1) % 4

    def trick_should_reset(self):
        active = self.active_players()
        non_last_active = [p for p in active if p != self.last_player_to_play]
        return all(p in self.passed_players for p in non_last_active)

    def reset_trick(self):
        self.prev_combo = []
        self.passed_players = set()

        if len(self.hands[self.last_player_to_play].cards) > 0:
            self.current_player = self.last_player_to_play
        else:
            self.current_player = self.next_active_player(self.last_player_to_play)

    def handle_mouse(self, pos):
        if self.ui.is_restart_button_clicked(pos):
            self.reset_game()
            return

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
        self.passed_players.discard(0)
        self.last_player_to_play = 0
        self.message = "You played"

        if len(self.hands[0].cards) == 0:
            self.game_over = True
            self.winner = "You"
            self.message = "You win!"
            return

        if self.trick_should_reset():
            self.reset_trick()
            self.message = f"Trick cleared. Player {self.current_player + 1} leads."
            if self.current_player != 0:
                self.run_ai_turns_until_player()
            return

        self.current_player = self.next_eligible_player(0)
        self.run_ai_turns_until_player()

    def handle_pass(self):
        if not self.prev_combo:
            self.message = "You cannot pass on a fresh trick"
            return

        self.passed_players.add(0)
        self.selected = []
        self.message = "You passed"

        if self.trick_should_reset():
            self.reset_trick()
            self.message = f"Trick cleared. Player {self.current_player + 1} leads."
            if self.current_player != 0:
                self.run_ai_turns_until_player()
            return

        self.current_player = self.next_eligible_player(0)
        self.run_ai_turns_until_player()

    def run_ai_turns_until_player(self):
        while not self.game_over and self.current_player != 0:
            ai_index = self.current_player - 1
            ai_hand = self.hands[self.current_player]
            ai_play = self.ai_players[ai_index].choose_play(ai_hand, self.prev_combo)

            if ai_play:
                self.prev_combo = sorted(ai_play, key=lambda c: c.value)
                ai_hand.remove_card_objects(ai_play)
                self.passed_players.discard(self.current_player)
                self.last_player_to_play = self.current_player
                self.message = f"Player {self.current_player + 1} played"

                if len(ai_hand.cards) == 0:
                    remaining = self.active_players()
                    if len(remaining) <= 1:
                        self.game_over = True
                        self.winner = f"Player {self.current_player + 1}"
                        self.message = f"{self.winner} wins!"
                        return

                if self.trick_should_reset():
                    self.reset_trick()
                    self.message = f"Trick cleared. Player {self.current_player + 1} leads."
                    if self.current_player == 0:
                        return
                else:
                    self.current_player = self.next_eligible_player(self.current_player)

            else:
                self.passed_players.add(self.current_player)
                self.message = f"Player {self.current_player + 1} passed"

                if self.trick_should_reset():
                    self.reset_trick()
                    self.message = f"Trick cleared. Player {self.current_player + 1} leads."
                    if self.current_player == 0:
                        return
                else:
                    self.current_player = self.next_eligible_player(self.current_player)

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
                self.player_names,
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
