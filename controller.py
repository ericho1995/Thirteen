import random
import pygame
from cards import Deck, Hand
from ai import AIPlayer
from rules import is_valid_play, display_sort_key
from state import GameState
from config import PLAYER_NAME_POOL, MIN_WIDTH, MIN_HEIGHT


class GameController:
    def __init__(self, ui):
        self.ui = ui
        self.ai_players = [AIPlayer("expert") for _ in range(3)]
        self.state = GameState()
        self._init_players()
        self.place_history_panel_bottom_right()
        self.start_new_hand(full_reset=True)


    def _init_players(self):
        pool = PLAYER_NAME_POOL[:]
        random.shuffle(pool)
        self.state.player_names = ["You", pool[0], pool[1], pool[2]]
        self.state.scoreboard.ensure_players(self.state.player_names)

    def update(self, dt: float):
        self.update_animation(dt)

    def update_animation(self, dt: float):
        anim = self.state.active_animation
        if not anim:
            return

        anim["elapsed"] += dt
        progress = min(1.0, anim["elapsed"] / anim["duration"])
        eased = 1 - (1 - progress) * (1 - progress)
        anim["progress"] = eased

        if progress >= 1.0:
            self.finish_animation()

    def finish_animation(self):
        anim = self.state.active_animation
        if not anim:
            return

        combo = anim["cards"]
        player_index = anim["player_index"]

        self.state.prev_combo = sorted(combo, key=display_sort_key)
        self.state.passed_players.discard(player_index)
        self.state.last_player_to_play = player_index
        self.state.must_open_with_three_spades = False
        self.state.message = f"{self.state.player_names[player_index]} played"
        self.add_history(f"{self.state.player_names[player_index]} played {self.format_cards(combo)}")

        if len(self.state.hands[player_index].cards) == 0:
            self.register_win(player_index)
            self.state.active_animation = None
            return

        self.state.active_animation = None

        if self.trick_should_reset():
            self.reset_trick()
            self.state.message = f"Trick cleared. {self.state.player_names[self.state.current_player]} leads."
            self.add_history(f"Trick cleared. {self.state.player_names[self.state.current_player]} leads")
        else:
            self.state.current_player = self.next_eligible_player(player_index)

        if not self.state.game_over and self.state.current_player != 0:
            self.run_ai_turns_until_player()

    def start_play_animation(self, player_index, combo):
        start_pos = self.ui.get_play_source_position(player_index)
        target_positions = self.ui.get_board_card_positions(len(combo))
        self.state.active_animation = {
            "player_index": player_index,
            "cards": sorted(combo, key=display_sort_key),
            "start_pos": start_pos,
            "targets": target_positions,
            "elapsed": 0.0,
            "duration": 0.22,
            "progress": 0.0,
        }

    def format_cards(self, cards):
        return " ".join(str(card) for card in sorted(cards, key=display_sort_key))

    def add_history(self, text):
        self.state.history.add(text)
        self.clamp_history_scroll()

    def clamp_history_scroll(self):
        max_scroll = self.ui.max_history_scroll(
            self.state.history.entries,
            self.state.scoreboard.as_dict(),
            self.state.standings_visible,
            self.state.recent_plays_visible,
            self.state.history_visible,
            self.state.history_width,
            self.state.history_height,
            self.state.history_pos
        )
        self.state.history_scroll = max(0, min(self.state.history_scroll, max_scroll))

    def active_players(self):
        return [i for i in range(4) if len(self.state.hands[i].cards) > 0]

    def find_three_of_spades_owner(self):
        for i, hand in enumerate(self.state.hands):
            for card in hand.cards:
                if card.rank == "3" and card.suit == "♠":
                    return i
        return 0

    def next_active_player(self, start_player):
        active = self.active_players()
        if len(active) <= 1:
            return start_player

        player = (start_player + 1) % 4
        while len(self.state.hands[player].cards) == 0:
            player = (player + 1) % 4
        return player

    def next_eligible_player(self, start_player):
        eligible = [
            i for i in range(4)
            if len(self.state.hands[i].cards) > 0 and i not in self.state.passed_players
        ]
        if not eligible:
            return self.state.last_player_to_play

        player = (start_player + 1) % 4
        while True:
            if len(self.state.hands[player].cards) > 0 and player not in self.state.passed_players:
                return player
            player = (player + 1) % 4

    def trick_should_reset(self):
        active = self.active_players()
        non_last_active = [p for p in active if p != self.state.last_player_to_play]
        return all(p in self.state.passed_players for p in non_last_active)

    def reset_trick(self):
        self.state.prev_combo = []
        self.state.passed_players = set()

        if len(self.state.hands[self.state.last_player_to_play].cards) > 0:
            self.state.current_player = self.state.last_player_to_play
        else:
            self.state.current_player = self.next_active_player(self.state.last_player_to_play)

    def combo_contains_three_spades(self, combo):
        return any(card.rank == "3" and card.suit == "♠" for card in combo)

    def register_win(self, player_index):
        winner_name = self.state.player_names[player_index]
        self.state.game_over = True
        self.state.previous_winner = player_index
        self.state.winner = winner_name
        self.state.scoreboard.record_win(winner_name)
        self.state.message = f"{winner_name} wins!"
        self.add_history(f"{winner_name} wins the hand")

    def sort_all_hands(self):
        for hand in self.state.hands:
            hand.sort_for_display()

    def reset_scores_and_history(self):
        self.state.scoreboard.wins = {name: 0 for name in self.state.player_names}
        self.state.history.clear()
        self.state.previous_winner = None
        self.state.history_scroll = 0

    def start_new_hand(self, full_reset=False):
        if full_reset and not self.state.player_names:
            self._init_players()

        deck = Deck()
        deck.shuffle()
        self.state.hands = [Hand(deck.deal(13)) for _ in range(4)]
        self.sort_all_hands()

        self.state.prev_combo = []
        self.state.selected = []
        self.state.passed_players = set()
        self.state.last_player_to_play = 0
        self.state.game_over = False
        self.state.winner = None
        self.state.active_animation = None

        if self.state.previous_winner is not None:
            self.state.current_player = self.state.previous_winner
            self.state.last_player_to_play = self.state.previous_winner
            self.state.must_open_with_three_spades = False
            self.state.message = f"{self.state.player_names[self.state.current_player]} leads as previous winner."
            self.add_history(f"New hand: {self.state.player_names[self.state.current_player]} leads")
        else:
            self.state.current_player = self.find_three_of_spades_owner()
            self.state.last_player_to_play = self.state.current_player
            self.state.must_open_with_three_spades = True
            self.state.message = f"{self.state.player_names[self.state.current_player]} starts with 3♠."
            self.add_history(f"New hand: {self.state.player_names[self.state.current_player]} must open with 3♠")

        if self.state.current_player != 0:
            self.run_ai_turns_until_player()

    def hard_restart(self):
        self.reset_scores_and_history()
        self.start_new_hand(full_reset=False)
        self.state.message = "Hard reset complete"

    def handle_play(self):
        if self.state.active_animation or self.state.game_over:
            return

        if not self.state.selected:
            self.state.message = "No cards selected"
            return

        play_combo = [self.state.hands[0].cards[i] for i in self.state.selected]

        if self.state.must_open_with_three_spades and not self.combo_contains_three_spades(play_combo):
            self.state.message = "Opening play must include 3♠"
            return

        if not is_valid_play(self.state.prev_combo, play_combo):
            self.state.message = "Invalid play"
            return

        self.state.hands[0].remove_cards(self.state.selected)
        self.state.selected = []
        self.start_play_animation(0, play_combo)

    def commit_player_pass(self, player_index):
        self.state.passed_players.add(player_index)
        self.state.message = f"{self.state.player_names[player_index]} passed"
        self.add_history(f"{self.state.player_names[player_index]} passed")

        if self.trick_should_reset():
            self.reset_trick()
            self.state.message = f"Trick cleared. {self.state.player_names[self.state.current_player]} leads."
            self.add_history(f"Trick cleared. {self.state.player_names[self.state.current_player]} leads")
            return

        self.state.current_player = self.next_eligible_player(player_index)

    def handle_pass(self):
        if self.state.active_animation or self.state.game_over:
            return

        if not self.state.prev_combo:
            self.state.message = "You cannot pass on a fresh trick"
            return

        self.state.selected = []
        self.commit_player_pass(0)

        if not self.state.game_over and self.state.current_player != 0:
            self.run_ai_turns_until_player()

    def run_ai_turns_until_player(self):
        while not self.state.game_over and self.state.current_player != 0 and not self.state.active_animation:
            ai_index = self.state.current_player - 1
            ai_hand = self.state.hands[self.state.current_player]

            ai_play = self.ai_players[ai_index].choose_play(
                ai_hand,
                self.state.prev_combo,
                must_contain_three_spades=self.state.must_open_with_three_spades
            )

            if ai_play:
                ai_hand.remove_card_objects(ai_play)
                self.start_play_animation(self.state.current_player, ai_play)
                return
            else:
                self.commit_player_pass(self.state.current_player)
                if self.state.current_player == 0:
                    return

    def handle_history_scroll(self, delta, mouse_pos=None):
        if not self.state.history_visible:
            return

        if mouse_pos is None:
            mouse_pos = pygame.mouse.get_pos()

        if not self.ui.is_history_body_hovered(
            mouse_pos,
            self.state.history.entries,
            self.state.scoreboard.as_dict(),
            self.state.standings_visible,
            self.state.recent_plays_visible,
            self.state.history_visible,
            self.state.history_width,
            self.state.history_height,
            self.state.history_pos
        ):
            return

        max_scroll = self.ui.max_history_scroll(
            self.state.history.entries,
            self.state.scoreboard.as_dict(),
            self.state.standings_visible,
            self.state.recent_plays_visible,
            self.state.history_visible,
            self.state.history_width,
            self.state.history_height,
            self.state.history_pos
        )

        self.state.history_scroll = max(
            0,
            min(self.state.history_scroll - delta * 28, max_scroll)
        )

    def handle_mouse(self, pos):
        if self.state.history_visible and self.ui.is_standings_toggle_clicked(
            pos, self.state.history_width, self.state.history_height, self.state.history_pos
        ):
            self.state.standings_visible = not self.state.standings_visible
            self.clamp_history_scroll()
            return

        if self.state.history_visible and self.ui.is_recent_plays_toggle_clicked(
            pos,
            self.state.history.entries,
            self.state.scoreboard.as_dict(),
            self.state.standings_visible,
            self.state.recent_plays_visible,
            self.state.history_width,
            self.state.history_height,
            self.state.history_pos
        ):
            self.state.recent_plays_visible = not self.state.recent_plays_visible
            self.clamp_history_scroll()
            return

        if self.ui.is_toolbar_hard_reset_clicked(pos):
            self.hard_restart()
            return

        if self.ui.is_toolbar_toggle_log_clicked(pos):
            self.state.history_visible = not self.state.history_visible
            return

        if self.state.game_over and self.ui.is_new_game_button_clicked(pos):
            self.start_new_hand(full_reset=False)
            return

        if self.state.history_visible and self.ui.is_history_resize_handle_clicked(
            pos,
            self.state.history_visible,
            self.state.history_width,
            self.state.history_height,
            self.state.history_pos
        ):
            self.state.dragging_history_resize = True
            return

        if self.state.history_visible and self.ui.is_history_header_clicked(
            pos,
            self.state.history_visible,
            self.state.history_width,
            self.state.history_height,
            self.state.history_pos
        ):
            panel_x, panel_y = self.state.history_pos
            self.state.dragging_history_panel = True
            self.state.history_drag_offset = (pos[0] - panel_x, pos[1] - panel_y)
            return

        if self.state.active_animation:
            return

        if self.state.game_over or self.state.current_player != 0:
            return

        index, _ = self.ui.get_card_at_pos(self.state.hands[0], pos)
        if index is not None:
            if index in self.state.selected:
                self.state.selected.remove(index)
            else:
                self.state.selected.append(index)
            self.state.selected.sort()
            return

        if self.ui.is_play_button_clicked(pos):
            self.handle_play()
            return

        if self.ui.is_pass_button_clicked(pos):
            self.handle_pass()
            return

    def handle_resize(self, size):
        width = max(MIN_WIDTH, size[0])
        height = max(MIN_HEIGHT, size[1])
        self.ui.handle_resize((width, height))
        self.state.history_pos = self.ui.clamp_history_panel_position(
            self.state.history_pos[0],
            self.state.history_pos[1],
            self.state.history_width,
            self.state.history_height
        )
        self.clamp_history_scroll()

    def handle_event(self, event):
        if event.type == pygame.VIDEORESIZE:
            self.handle_resize(event.size)

        elif event.type == pygame.MOUSEWHEEL:
            self.handle_history_scroll(event.y)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.handle_mouse(event.pos)
            elif event.button == 4:
                self.handle_history_scroll(1, event.pos)
            elif event.button == 5:
                self.handle_history_scroll(-1, event.pos)

        elif event.type == pygame.MOUSEBUTTONUP:
            self.state.dragging_history_resize = False
            self.state.dragging_history_panel = False

        elif event.type == pygame.MOUSEMOTION:
            if self.state.dragging_history_resize and self.state.history_visible:
                new_width, new_height = self.ui.compute_history_size_from_mouse(
                    event.pos,
                    self.state.history_pos,
                    self.state.history_width,
                    self.state.history_height
                )
                self.state.history_width = max(240, min(int(self.ui.width * 0.42), new_width))
                self.state.history_height = max(240, min(int(self.ui.height * 0.72), new_height))
                self.clamp_history_scroll()

            elif self.state.dragging_history_panel and self.state.history_visible:
                offset_x, offset_y = self.state.history_drag_offset
                new_x = event.pos[0] - offset_x
                new_y = event.pos[1] - offset_y
                self.state.history_pos = self.ui.clamp_history_panel_position(
                    new_x, new_y, self.state.history_width, self.state.history_height
                )

    def place_history_panel_bottom_right(self):
        margin = 20
        x = self.ui.width - self.state.history_width - margin
        y = self.ui.height - self.state.history_height - margin
        self.state.history_pos = self.ui.clamp_history_panel_position(
            x,
            y,
            self.state.history_width,
            self.state.history_height
        )


    def view_model(self):
        return {
            "hands": self.state.hands,
            "player_names": self.state.player_names,
            "current_player": self.state.current_player,
            "prev_combo": self.state.prev_combo,
            "selected": self.state.selected,
            "history_log": self.state.history.entries,
            "history_scroll": self.state.history_scroll,
            "win_counts": self.state.scoreboard.as_dict(),
            "history_visible": self.state.history_visible,
            "history_width": self.state.history_width,
            "history_height": self.state.history_height,
            "history_pos": self.state.history_pos,
            "message": self.state.message,
            "active_animation": self.state.active_animation,
            "game_over": self.state.game_over,
            "standings_visible": self.state.standings_visible,
            "recent_plays_visible": self.state.recent_plays_visible,
        }
