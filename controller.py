import random
import pygame
from ai import AIPlayer
from cards import Deck, Hand
from config import (
    PLAYER_NAME_POOL,
    MIN_WIDTH,
    MIN_HEIGHT,
    MIN_PANEL_WIDTH,
    MIN_PANEL_HEIGHT,
    MAX_PANEL_WIDTH_RATIO,
    MAX_PANEL_HEIGHT_RATIO,
    DEAL_ANIMATION_DURATION,
    DEAL_START_DELAY,
    SCROLL_STEP,
)
from rules import is_valid_play, display_sort_key
from state import GameState


class GameController:
    def __init__(self, ui):
        self.ui = ui
        self.ai_players = [AIPlayer("expert") for _ in range(3)]
        self.state = GameState()
        self._init_players()
        self.state.panel.pos = self.ui.default_history_panel_position(
            self.ui.width,
            self.ui.height,
            self.state.panel.width,
            self.state.panel.height
        )
        self.prepare_new_hand(full_reset=True)

    def _init_players(self):
        pool = PLAYER_NAME_POOL[:]
        random.shuffle(pool)
        self.state.player_names = ["You", pool[0], pool[1], pool[2]]
        self.state.scoreboard.ensure_players(self.state.player_names)

    def update(self, dt: float):
        if self.state.deal.in_progress:
            self.update_deal_animation(dt)
            return
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

    def update_deal_animation(self, dt: float):
        deal = self.state.deal
        if not deal.in_progress:
            return

        if deal.animated_card:
            deal.animated_card["elapsed"] += dt
            progress = min(1.0, deal.animated_card["elapsed"] / deal.animated_card["duration"])
            deal.animated_card["progress"] = 1 - (1 - progress) * (1 - progress)

            if progress >= 1.0:
                self.finish_single_deal_step()
            return

        deal.deal_timer += dt
        if deal.deal_timer >= DEAL_START_DELAY:
            self.start_next_deal_step()

    def start_next_deal_step(self):
        deal = self.state.deal
        if not deal.temp_deck:
            self.finish_dealing_phase()
            return

        player_index = deal.deal_index % 4
        card = deal.temp_deck.pop(0)
        target_rect = self.ui.get_deal_target_rect(player_index, len(self.state.hands[player_index].cards))

        deal.animated_card = {
            "card": card,
            "player_index": player_index,
            "target_rect": target_rect,
            "start_pos": self.ui.get_deck_position(),
            "elapsed": 0.0,
            "duration": DEAL_ANIMATION_DURATION,
            "progress": 0.0,
        }

    def finish_single_deal_step(self):
        deal = self.state.deal
        anim = deal.animated_card
        if not anim:
            return

        player_index = anim["player_index"]
        card = anim["card"]
        self.state.hands[player_index].cards.append(card)
        deal.deal_index += 1
        deal.animated_card = None
        deal.deal_timer = 0.0

        if len(self.state.hands[player_index].cards) == 13:
            self.state.hands[player_index].sort_for_display()

        if all(len(hand.cards) == 13 for hand in self.state.hands):
            self.finish_dealing_phase()

    def finish_dealing_phase(self):
        self.sort_all_hands()
        self.state.deal.in_progress = False
        self.state.deal.ready_to_deal = False
        self.state.deal.dealing_started = True
        self.state.deal.temp_deck = []
        self.state.deal.animated_card = None
        self.begin_hand_after_deal()

    def begin_hand_after_deal(self):
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
            lead_name = self.state.player_names[self.state.current_player]
            self.state.message = f"{lead_name} leads as previous winner."
            self.add_history(f"New hand: {lead_name} leads")
        else:
            self.state.current_player = self.find_three_of_spades_owner()
            self.state.last_player_to_play = self.state.current_player
            self.state.must_open_with_three_spades = True
            lead_name = self.state.player_names[self.state.current_player]
            if self.state.current_player == 0:
                self.state.message = "You start with 3♠."
            else:
                self.state.message = f"{lead_name} starts with 3♠."
            self.add_history(f"New hand: {lead_name} must open with 3♠")

        if self.state.current_player != 0:
            self.run_ai_turns_until_player()

    def prepare_new_hand(self, full_reset=False):
        if full_reset and not self.state.player_names:
            self._init_players()

        self.state.hands = [Hand([]) for _ in range(4)]
        self.state.prev_combo = []
        self.state.selected = []
        self.state.passed_players = set()
        self.state.last_player_to_play = 0
        self.state.game_over = False
        self.state.winner = None
        self.state.active_animation = None
        self.state.must_open_with_three_spades = False

        deck = Deck()
        deck.shuffle()

        self.state.deal.in_progress = False
        self.state.deal.ready_to_deal = True
        self.state.deal.dealing_started = False
        self.state.deal.temp_deck = deck.cards[:]
        self.state.deal.deal_index = 0
        self.state.deal.deal_timer = 0.0
        self.state.deal.animated_card = None

        self.state.message = "Click Deal to start"

    def start_dealing(self):
        if not self.state.deal.ready_to_deal or self.state.deal.in_progress:
            return
        self.state.deal.in_progress = True
        self.state.deal.deal_timer = 0.0
        self.state.message = "Dealing cards..."

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
        self.state.active_animation = {
            "player_index": player_index,
            "cards": sorted(combo, key=display_sort_key),
            "start_pos": self.ui.get_play_source_position(player_index),
            "targets": self.ui.get_board_card_positions(len(combo)),
            "elapsed": 0.0,
            "duration": 0.22,
            "progress": 0.0,
        }

    def format_cards(self, cards):
        return " ".join(str(card) for card in sorted(cards, key=display_sort_key))

    def add_history(self, text):
        self.state.history.add(text)
        self.clamp_panel_scrolls()

    def clamp_panel_scrolls(self):
        panel = self.state.panel
        max_history_scroll = self.ui.max_history_scroll(
            self.state.history.entries,
            self.state.scoreboard.as_dict(),
            panel.show_standings,
            panel.show_history,
            panel.visible,
            panel.width,
            panel.height,
            panel.pos
        )
        panel.history_scroll = max(0, min(panel.history_scroll, max_history_scroll))

        max_standings_scroll = self.ui.max_standings_scroll(
            self.state.scoreboard.as_dict(),
            panel.show_standings,
            panel.show_history,
            panel.visible,
            panel.width,
            panel.height,
            panel.pos
        )
        panel.standings_scroll = max(0, min(panel.standings_scroll, max_standings_scroll))

    def active_players(self):
        return [i for i in range(4) if len(self.state.hands[i].cards) > 0]

    def find_three_of_spades_owner(self):
        for i, hand in enumerate(self.state.hands):
            if hand.contains_three_of_spades():
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
        return any(card.is_three_of_spades() for card in combo)

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
        self.state.scoreboard.reset()
        self.state.history.clear()
        self.state.previous_winner = None
        self.state.panel.history_scroll = 0
        self.state.panel.standings_scroll = 0

    def hard_restart(self):
        self.reset_scores_and_history()
        self.prepare_new_hand(full_reset=False)
        self.state.message = "Hard reset complete. Click Deal"

    def handle_play(self):
        if self.state.deal.ready_to_deal or self.state.deal.in_progress:
            return
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
        if self.state.deal.ready_to_deal or self.state.deal.in_progress:
            return
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

            self.commit_player_pass(self.state.current_player)
            if self.state.current_player == 0:
                return

    def handle_panel_scroll(self, delta, mouse_pos=None):
        panel = self.state.panel
        if not panel.visible:
            return

        if mouse_pos is None:
            mouse_pos = pygame.mouse.get_pos()

        if self.ui.is_standings_body_hovered(
            mouse_pos,
            self.state.scoreboard.as_dict(),
            panel.show_standings,
            panel.show_history,
            panel.visible,
            panel.width,
            panel.height,
            panel.pos
        ):
            max_scroll = self.ui.max_standings_scroll(
                self.state.scoreboard.as_dict(),
                panel.show_standings,
                panel.show_history,
                panel.visible,
                panel.width,
                panel.height,
                panel.pos
            )
            panel.standings_scroll = max(0, min(panel.standings_scroll - delta * SCROLL_STEP, max_scroll))
            return

        if self.ui.is_history_body_hovered(
            mouse_pos,
            self.state.history.entries,
            self.state.scoreboard.as_dict(),
            panel.show_standings,
            panel.show_history,
            panel.visible,
            panel.width,
            panel.height,
            panel.pos
        ):
            max_scroll = self.ui.max_history_scroll(
                self.state.history.entries,
                self.state.scoreboard.as_dict(),
                panel.show_standings,
                panel.show_history,
                panel.visible,
                panel.width,
                panel.height,
                panel.pos
            )
            panel.history_scroll = max(0, min(panel.history_scroll - delta * SCROLL_STEP, max_scroll))

    def handle_mouse(self, pos):
        panel = self.state.panel

        if self.state.deal.ready_to_deal and self.ui.is_deal_button_clicked(pos):
            self.start_dealing()
            return

        if panel.visible:
            body, content_height, track, thumb = self.ui.standings_scrollbar_rects(
                self.state.scoreboard.as_dict(),
                panel.standings_scroll,
                panel.show_standings,
                panel.show_history,
                panel.visible,
                panel.width,
                panel.height,
                panel.pos
            )
            if track and thumb:
                if thumb.collidepoint(pos):
                    panel.dragging_standings_scrollbar = True
                    panel.scrollbar_drag_offset_y = pos[1] - thumb.y
                    return
                if track.collidepoint(pos):
                    panel.standings_scroll = self.ui.scroll_from_track_click(pos[1], body, content_height)
                    self.clamp_panel_scrolls()
                    return

            body, content_height, track, thumb = self.ui.history_scrollbar_rects(
                self.state.history.entries,
                panel.history_scroll,
                self.state.scoreboard.as_dict(),
                panel.show_standings,
                panel.show_history,
                panel.visible,
                panel.width,
                panel.height,
                panel.pos
            )
            if track and thumb:
                if thumb.collidepoint(pos):
                    panel.dragging_history_scrollbar = True
                    panel.scrollbar_drag_offset_y = pos[1] - thumb.y
                    return
                if track.collidepoint(pos):
                    panel.history_scroll = self.ui.scroll_from_track_click(pos[1], body, content_height)
                    self.clamp_panel_scrolls()
                    return

        if panel.visible and self.ui.is_standings_toggle_clicked(pos, panel.width, panel.height, panel.pos):
            panel.show_standings = not panel.show_standings
            self.clamp_panel_scrolls()
            return

        if panel.visible and self.ui.is_recent_plays_toggle_clicked(
            pos,
            self.state.history.entries,
            self.state.scoreboard.as_dict(),
            panel.show_standings,
            panel.show_history,
            panel.width,
            panel.height,
            panel.pos
        ):
            panel.show_history = not panel.show_history
            self.clamp_panel_scrolls()
            return

        if self.ui.is_toolbar_hard_reset_clicked(pos):
            self.hard_restart()
            return

        if self.ui.is_toolbar_toggle_log_clicked(pos):
            panel.visible = not panel.visible
            self.clamp_panel_scrolls()
            return

        if self.state.game_over and self.ui.is_new_game_button_clicked(pos):
            self.prepare_new_hand(full_reset=False)
            return

        if panel.visible and self.ui.is_history_resize_handle_clicked(
            pos, panel.visible, panel.width, panel.height, panel.pos
        ):
            panel.dragging_resize = True
            return

        if panel.visible and self.ui.is_history_header_clicked(
            pos, panel.visible, panel.width, panel.height, panel.pos
        ):
            panel_x, panel_y = panel.pos
            panel.dragging_panel = True
            panel.drag_offset = (pos[0] - panel_x, pos[1] - panel_y)
            return

        if self.state.deal.ready_to_deal or self.state.deal.in_progress:
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
        self.state.panel.pos = self.ui.clamp_history_panel_position(
            self.state.panel.pos[0],
            self.state.panel.pos[1],
            self.state.panel.width,
            self.state.panel.height
        )
        self.clamp_panel_scrolls()

    def handle_event(self, event):
        panel = self.state.panel

        if event.type == pygame.VIDEORESIZE:
            self.handle_resize(event.size)

        elif event.type == pygame.MOUSEWHEEL:
            self.handle_panel_scroll(event.y)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.handle_mouse(event.pos)
            elif event.button == 4:
                self.handle_panel_scroll(1, event.pos)
            elif event.button == 5:
                self.handle_panel_scroll(-1, event.pos)

            elif event.type == pygame.MOUSEBUTTONUP:
                panel.dragging_resize = False
                panel.dragging_panel = False
                panel.dragging_history_scrollbar = False
                panel.dragging_standings_scrollbar = False

            elif event.type == pygame.MOUSEMOTION:
                if panel.dragging_standings_scrollbar and panel.visible:
                    body, content_height, track, thumb = self.ui.standings_scrollbar_rects(
                        self.state.scoreboard.as_dict(),
                        panel.standings_scroll,
                        panel.show_standings,
                        panel.show_history,
                        panel.visible,
                        panel.width,
                        panel.height,
                        panel.pos
                    )
                    if track and thumb:
                        panel.standings_scroll = self.ui.scroll_from_thumb_drag(
                            event.pos[1],
                            track,
                            thumb,
                            content_height,
                            body.height,
                            panel.scrollbar_drag_offset_y
                        )
                        self.clamp_panel_scrolls()

                elif panel.dragging_history_scrollbar and panel.visible:
                    body, content_height, track, thumb = self.ui.history_scrollbar_rects(
                        self.state.history.entries,
                        panel.history_scroll,
                        self.state.scoreboard.as_dict(),
                        panel.show_standings,
                        panel.show_history,
                        panel.visible,
                        panel.width,
                        panel.height,
                        panel.pos
                    )
                    if track and thumb:
                        panel.history_scroll = self.ui.scroll_from_thumb_drag(
                            event.pos[1],
                            track,
                            thumb,
                            content_height,
                            body.height,
                            panel.scrollbar_drag_offset_y
                        )
                        self.clamp_panel_scrolls()

                elif panel.dragging_resize and panel.visible:
                    new_width, new_height = self.ui.compute_history_size_from_mouse(
                        event.pos,
                        panel.pos,
                        panel.width,
                        panel.height
                    )
                    panel.width = max(MIN_PANEL_WIDTH, min(int(self.ui.width * MAX_PANEL_WIDTH_RATIO), new_width))
                    panel.height = max(MIN_PANEL_HEIGHT, min(int(self.ui.height * MAX_PANEL_HEIGHT_RATIO), new_height))
                    self.clamp_panel_scrolls()

                elif panel.dragging_panel and panel.visible:
                    offset_x, offset_y = panel.drag_offset
                    new_x = event.pos[0] - offset_x
                    new_y = event.pos[1] - offset_y
                    panel.pos = self.ui.clamp_history_panel_position(new_x, new_y, panel.width, panel.height)


    def view_model(self):
        panel = self.state.panel
        return {
            "hands": self.state.hands,
            "player_names": self.state.player_names,
            "current_player": self.state.current_player,
            "prev_combo": self.state.prev_combo,
            "selected": self.state.selected,
            "history_log": self.state.history.entries,
            "history_scroll": panel.history_scroll,
            "standings_scroll": panel.standings_scroll,
            "win_counts": self.state.scoreboard.as_dict(),
            "history_visible": panel.visible,
            "history_width": panel.width,
            "history_height": panel.height,
            "history_pos": panel.pos,
            "message": self.state.message,
            "active_animation": self.state.active_animation,
            "game_over": self.state.game_over,
            "standings_visible": panel.show_standings,
            "recent_plays_visible": panel.show_history,
            "deal_ready": self.state.deal.ready_to_deal,
            "deal_in_progress": self.state.deal.in_progress,
            "deal_animation": self.state.deal.animated_card,
        }
