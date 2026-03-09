"""Thirteen Game - Main Entry"""
import pygame
import random
from cards import Deck, Hand
from game_logic import is_valid_play, AIPlayer, display_sort_key
from ui import UI


class ThirteenGame:
    def __init__(self):
        self.ui = UI()
        self.previous_winner = None
        self.must_open_with_three_spades = False
        self.history_visible = True
        self.history_width = 300
        self.dragging_history_resize = False
        self.reset_game(full_reset=True)

    def format_cards(self, cards):
        return " ".join(str(card) for card in sorted(cards, key=display_sort_key))

    def add_history(self, text):
        self.history_log.append(text)
        self.history_log = self.history_log[-30:]

    def find_three_of_spades_owner(self):
        for i, hand in enumerate(self.hands):
            for card in hand.cards:
                if card.rank == "3" and card.suit == "♠":
                    return i
        return 0

    def sort_all_hands_for_display(self):
        for hand in self.hands:
            hand.cards.sort(key=display_sort_key)

    def reset_game(self, full_reset=False):
        if full_reset or not hasattr(self, "player_names"):
            name_pool = [
                "Mia", "Ethan", "Zoe", "Lucas", "Ava", "Noah",
                "Chloe", "Liam", "Sophie", "Jack", "Ella", "Leo",
                "Nina", "Oscar", "Ruby", "Max"
            ]
            random.shuffle(name_pool)
            self.player_names = ["You", name_pool[0], name_pool[1], name_pool[2]]
            self.win_counts = {name: 0 for name in self.player_names}

        self.deck = Deck()
        self.deck.shuffle()
        self.hands = [Hand(self.deck.deal(13)) for _ in range(4)]
        self.sort_all_hands_for_display()

        self.prev_combo = []
        self.selected = []
        self.history_log = []
        self.ai_players = [AIPlayer() for _ in range(3)]
        self.game_over = False
        self.winner = None
        self.passed_players = set()

        if self.previous_winner is not None:
            self.current_player = self.previous_winner
            self.last_player_to_play = self.previous_winner
            self.must_open_with_three_spades = False
            self.message = f"{self.player_names[self.current_player]} leads as previous winner."
            self.add_history(f"New hand: {self.player_names[self.current_player]} leads")
        else:
            self.current_player = self.find_three_of_spades_owner()
            self.last_player_to_play = self.current_player
            self.must_open_with_three_spades = True
            self.message = f"{self.player_names[self.current_player]} starts with 3♠."
            self.add_history(f"New hand: {self.player_names[self.current_player]} must open with 3♠")

    def start_new_hand(self):
        self.reset_game(full_reset=False)
        if self.current_player != 0 and not self.game_over:
            self.run_ai_turns_until_player()

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

    def combo_contains_three_spades(self, combo):
        return any(card.rank == "3" and card.suit == "♠" for card in combo)

    def register_win(self, player_index):
        self.game_over = True
        self.previous_winner = player_index
        self.winner = self.player_names[player_index]
        self.win_counts[self.winner] += 1
        self.message = f"{self.winner} wins!"
        self.add_history(f"{self.winner} wins the hand")

    def handle_mouse(self, pos):
        if self.ui.is_history_toggle_clicked(pos):
            self.history_visible = not self.history_visible
            return

        if self.ui.is_history_resize_handle_clicked(pos, self.history_visible, self.history_width):
            self.dragging_history_resize = True
            return

        if self.ui.is_restart_button_clicked(pos):
            self.start_new_hand()
            return

        if self.game_over or self.current_player != 0:
            return

        index, _ = self.ui.get_card_at_pos(self.hands[0], pos)
        if index is not None:
            if index in self.selected:
                self.selected.remove(index)
            else:
                self.selected.append(index)
            self.selected.sort()
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

        if self.must_open_with_three_spades and not self.combo_contains_three_spades(play_combo):
            self.message = "Opening play must include 3♠"
            return

        if not is_valid_play(self.prev_combo, play_combo):
            self.message = "Invalid play"
            return

        self.prev_combo = sorted(play_combo, key=display_sort_key)
        self.hands[0].remove_cards(self.selected)
        self.hands[0].cards.sort(key=display_sort_key)
        self.selected = []
        self.passed_players.discard(0)
        self.last_player_to_play = 0
        self.must_open_with_three_spades = False
        self.message = "You played"
        self.add_history(f"{self.player_names[0]} played {self.format_cards(play_combo)}")

        if len(self.hands[0].cards) == 0:
            self.register_win(0)
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
        self.add_history(f"{self.player_names[0]} passed")

        if self.trick_should_reset():
            self.reset_trick()
            self.message = f"Trick cleared. {self.player_names[self.current_player]} leads."
            self.add_history(f"Trick cleared. {self.player_names[self.current_player]} leads")
            if self.current_player != 0:
                self.run_ai_turns_until_player()
            return

        self.current_player = self.next_eligible_player(0)
        self.run_ai_turns_until_player()

    def run_ai_turns_until_player(self):
        while not self.game_over and self.current_player != 0:
            ai_index = self.current_player - 1
            ai_hand = self.hands[self.current_player]

            ai_play = self.ai_players[ai_index].choose_play(
                ai_hand,
                self.prev_combo,
                must_contain_three_spades=self.must_open_with_three_spades
            )

            if ai_play:
                self.prev_combo = sorted(ai_play, key=display_sort_key)
                ai_hand.remove_card_objects(ai_play)
                ai_hand.cards.sort(key=display_sort_key)
                self.passed_players.discard(self.current_player)
                self.last_player_to_play = self.current_player
                self.must_open_with_three_spades = False
                self.message = f"{self.player_names[self.current_player]} played"
                self.add_history(f"{self.player_names[self.current_player]} played {self.format_cards(ai_play)}")

                if len(ai_hand.cards) == 0:
                    self.register_win(self.current_player)
                    return

                if self.trick_should_reset():
                    self.reset_trick()
                    self.message = f"Trick cleared. {self.player_names[self.current_player]} leads."
                    self.add_history(f"Trick cleared. {self.player_names[self.current_player]} leads")
                    if self.current_player == 0:
                        return
                else:
                    self.current_player = self.next_eligible_player(self.current_player)
            else:
                self.passed_players.add(self.current_player)
                self.message = f"{self.player_names[self.current_player]} passed"
                self.add_history(f"{self.player_names[self.current_player]} passed")

                if self.trick_should_reset():
                    self.reset_trick()
                    self.message = f"Trick cleared. {self.player_names[self.current_player]} leads."
                    self.add_history(f"Trick cleared. {self.player_names[self.current_player]} leads")
                    if self.current_player == 0:
                        return
                else:
                    self.current_player = self.next_eligible_player(self.current_player)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.handle_mouse(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging_history_resize = False
        elif event.type == pygame.MOUSEMOTION and self.dragging_history_resize and self.history_visible:
            self.history_width = max(220, min(420, self.ui.compute_history_width_from_mouse(event.pos[0])))

    def run(self):
        if self.current_player != 0:
            self.run_ai_turns_until_player()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self.handle_event(event)

            self.ui.draw_ui(
                self.hands,
                self.player_names,
                self.current_player,
                self.prev_combo,
                self.selected,
                self.history_log,
                self.win_counts,
                self.history_visible,
                self.history_width,
                self.message
            )
            self.ui.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    game = ThirteenGame()
    game.run()
