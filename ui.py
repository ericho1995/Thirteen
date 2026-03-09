import pygame
from typing import List, Tuple, Optional
from cards import Card, Hand
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, MIN_WIDTH, MIN_HEIGHT,
    CARD_WIDTH, CARD_HEIGHT, COLORS
)


class UI:
    def __init__(self):
        pygame.init()
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption("Thirteen")
        self.clock = pygame.time.Clock()

        self.font_name = self.pick_font([
            "bahnschrift",
            "segoeui",
            "arial",
            "dejavusans",
        ])
        self.symbol_font_name = self.pick_font([
            "segoeuisymbol",
            "arialunicodems",
            "dejavusans",
            "freesans",
        ])

        self.font = pygame.font.Font(self.font_name, 24)
        self.small_font = pygame.font.Font(self.font_name, 18)
        self.big_font = pygame.font.Font(self.font_name, 38)
        self.title_font = pygame.font.Font(self.font_name, 30)
        self.score_title_font = pygame.font.Font(self.font_name, 20)

        self.card_rank_font = pygame.font.Font(self.font_name, 24)
        self.card_suit_font = pygame.font.Font(self.symbol_font_name, 26)
        self.card_center_font = pygame.font.Font(self.symbol_font_name, 34)

        self.toolbar_height = 54
        self.update_layout()

    def pick_font(self, candidates):
        for name in candidates:
            path = pygame.font.match_font(name)
            if path:
                return path
        return None

    def handle_resize(self, size: Tuple[int, int]):
        self.width = max(MIN_WIDTH, size[0])
        self.height = max(MIN_HEIGHT, size[1])
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        self.update_layout()

    def update_layout(self):
        self.hand_y = self.height - 170

        side_reserve = 220
        board_w = min(520, int(self.width * 0.34))
        board_h = int(self.height * 0.23)

        available_left = 40
        available_right = self.width - side_reserve - 40
        board_x = max(available_left, (available_right - board_w) // 2)

        self.play_area = pygame.Rect(
            board_x,
            int(self.height * 0.34),
            board_w,
            board_h
        )


        button_w = 130
        button_h = 48
        action_y = self.play_area.bottom + 26
        center_x = self.width // 2

        self.play_button = pygame.Rect(center_x - button_w - 10, action_y, button_w, button_h)
        self.pass_button = pygame.Rect(center_x + 10, action_y, button_w, button_h)
        self.new_game_button = pygame.Rect(self.width - 180, self.toolbar_height + 14, 150, 40)

        self.toolbar_rect = pygame.Rect(0, 0, self.width, self.toolbar_height)
        self.toolbar_hard_reset_button = pygame.Rect(16, 10, 140, 34)
        self.toolbar_toggle_log_button = pygame.Rect(170, 10, 120, 34)

    def draw_rounded_rect(self, color, rect, radius=16, width=0):
        pygame.draw.rect(self.screen, color, rect, width=width, border_radius=radius)

    def draw_background(self):
        self.screen.fill(COLORS["bg_bottom"])
        for y in range(self.height):
            blend = y / self.height
            r = int(COLORS["bg_top"][0] * (1 - blend) + COLORS["bg_bottom"][0] * blend)
            g = int(COLORS["bg_top"][1] * (1 - blend) + COLORS["bg_bottom"][1] * blend)
            b = int(COLORS["bg_top"][2] * (1 - blend) + COLORS["bg_bottom"][2] * blend)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.width, y))

    def suit_color(self, suit: str):
        return COLORS["red"] if suit in ["♥", "♦"] else COLORS["black"]

    def draw_card(self, card: Card, rect: pygame.Rect, selected: bool = False):
        shadow_rect = rect.move(4, 5)
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, COLORS["card_shadow"], shadow_surf.get_rect(), border_radius=12)
        self.screen.blit(shadow_surf, shadow_rect.topleft)

        face_color = COLORS["card_selected"] if selected else COLORS["card_face"]
        self.draw_rounded_rect(face_color, rect, radius=12)
        self.draw_rounded_rect(COLORS["card_border"], rect, radius=12, width=2)

        rank_text = self.card_rank_font.render(card.rank, True, self.suit_color(card.suit))
        suit_text = self.card_suit_font.render(card.suit, True, self.suit_color(card.suit))
        center_rank = self.card_rank_font.render(card.rank, True, self.suit_color(card.suit))
        center_suit = self.card_center_font.render(card.suit, True, self.suit_color(card.suit))

        self.screen.blit(rank_text, (rect.x + 8, rect.y + 6))
        self.screen.blit(suit_text, (rect.x + 10, rect.y + 30))

        gap = 4
        total_width = center_rank.get_width() + gap + center_suit.get_width()
        start_x = rect.centerx - total_width // 2

        line_height = max(center_rank.get_height(), center_suit.get_height())
        base_y = rect.centery - line_height // 2
        rank_y = base_y + (line_height - center_rank.get_height()) // 2
        suit_y = base_y + (line_height - center_suit.get_height()) // 2

        self.screen.blit(center_rank, (start_x, rank_y))
        self.screen.blit(center_suit, (start_x + center_rank.get_width() + gap, suit_y))

    def draw_card_back(self, rect: pygame.Rect):
        shadow_rect = rect.move(3, 4)
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, COLORS["card_shadow"], shadow_surf.get_rect(), border_radius=10)
        self.screen.blit(shadow_surf, shadow_rect.topleft)

        self.draw_rounded_rect((52, 76, 140), rect, radius=10)
        self.draw_rounded_rect((235, 235, 245), rect, radius=10, width=2)
        inner = rect.inflate(-14, -14)
        self.draw_rounded_rect((230, 230, 240), inner, radius=8, width=2)

    def draw_toolbar(self):
        pygame.draw.rect(self.screen, COLORS["toolbar"], self.toolbar_rect)
        pygame.draw.line(self.screen, COLORS["toolbar_border"], (0, self.toolbar_height - 1), (self.width, self.toolbar_height - 1), 2)
        title = self.title_font.render("Thirteen", True, COLORS["text"])
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 10))
        self.draw_button(self.toolbar_hard_reset_button, "Hard Reset", alt=True)
        self.draw_button(self.toolbar_toggle_log_button, "Toggle Log", alt=True)

    def draw_hand(self, hand: Hand, selected_indices: Optional[List[int]] = None):
        if selected_indices is None:
            selected_indices = []
        spacing = min(55, max(32, int((self.width - 160) / max(13, len(hand.cards) + 1))))
        total_width = ((len(hand.cards) - 1) * spacing) + CARD_WIDTH
        x_start = max(40, (self.width - total_width) // 2)

        for i, card in enumerate(hand.cards):
            y_offset = -24 if i in selected_indices else 0
            rect = pygame.Rect(x_start + i * spacing, self.hand_y + y_offset, CARD_WIDTH, CARD_HEIGHT)
            self.draw_card(card, rect, i in selected_indices)

    def draw_opponent_horizontal(self, hand: Hand, x_start: int, y: int):
        for i in range(len(hand.cards)):
            rect = pygame.Rect(x_start + i * 18, y, 55, 80)
            self.draw_card_back(rect)

    def draw_opponent_vertical(self, hand: Hand, x: int, y_start: int):
        for i in range(len(hand.cards)):
            rect = pygame.Rect(x, y_start + i * 18, 55, 80)
            self.draw_card_back(rect)

    def draw_player_label(self, name: str, card_count: int, x: int, y: int, active: bool = False, center: bool = False):
        color = COLORS["active_name"] if active else COLORS["text"]
        label = self.font.render(f"{name} ({card_count})", True, color)
        rect = label.get_rect(center=(x, y)) if center else label.get_rect(topleft=(x, y))
        self.screen.blit(label, rect)

    def draw_play_area(self, prev_combo: List[Card], active_animation=None):
        self.draw_rounded_rect(COLORS["table_zone"], self.play_area, radius=24)
        self.draw_rounded_rect(COLORS["table_outline"], self.play_area, radius=24, width=3)
        label = self.small_font.render("Current trick", True, COLORS["muted_text"])
        self.screen.blit(label, (self.play_area.x + 18, self.play_area.y + 14))

        if prev_combo and not active_animation:
            positions = self.get_board_card_positions(len(prev_combo))
            for i, card in enumerate(prev_combo):
                self.draw_card(card, positions[i])

    def draw_button(self, rect: pygame.Rect, label: str, alt: bool = False):
        color = COLORS["button_alt"] if alt else COLORS["button"]
        self.draw_rounded_rect(color, rect, radius=14)
        self.draw_rounded_rect((230, 230, 230), rect, radius=14, width=2)
        text = self.small_font.render(label, True, COLORS["button_text"])
        self.screen.blit(text, text.get_rect(center=rect.center))

    def history_panel_rect(self, history_visible: bool, history_width: int, history_height: int, history_pos: Tuple[int, int]):
        if not history_visible:
            return None
        return pygame.Rect(history_pos[0], history_pos[1], history_width, history_height)

    def history_header_rect(self, history_visible: bool, history_width: int, history_height: int, history_pos: Tuple[int, int]):
        panel = self.history_panel_rect(history_visible, history_width, history_height, history_pos)
        if panel is None:
            return None
        return pygame.Rect(panel.x, panel.y, panel.width, 42)

    def history_resize_handle_rect(self, history_visible: bool, history_width: int, history_height: int, history_pos: Tuple[int, int]):
        panel = self.history_panel_rect(history_visible, history_width, history_height, history_pos)
        if panel is None:
            return None
        return pygame.Rect(panel.right - 14, panel.bottom - 14, 12, 12)

    def standings_toggle_rect(self, history_width: int, history_height: int, history_pos: Tuple[int, int]):
        panel = pygame.Rect(history_pos[0], history_pos[1], history_width, history_height)
        return pygame.Rect(panel.x + 14, panel.y + 48, panel.width - 28, 30)

    def history_toggle_rect(self, history_width: int, history_height: int, history_pos: Tuple[int, int]):
        panel = pygame.Rect(history_pos[0], history_pos[1], history_width, history_height)
        return pygame.Rect(panel.x + 14, panel.y + 84, panel.width - 28, 30)

    def panel_content_rect(self, history_visible: bool, history_width: int, history_height: int, history_pos: Tuple[int, int]):
        panel = self.history_panel_rect(history_visible, history_width, history_height, history_pos)
        if panel is None:
            return None
        top = panel.y + 122
        return pygame.Rect(panel.x + 14, top, panel.width - 28, panel.bottom - top - 14)

    def get_sorted_standings(self, win_counts: dict):
        return sorted(win_counts.items(), key=lambda item: (-item[1], item[0]))

    def get_leader(self, win_counts: dict):
        if not win_counts:
            return None
        top_score = max(win_counts.values())
        if top_score <= 0:
            return None
        leaders = [name for name, score in win_counts.items() if score == top_score]
        if len(leaders) != 1:
            return None
        return leaders[0], top_score

    def wrap_text_lines(self, text: str, max_width: int):
        words = text.split(" ")
        lines = []
        current = ""

        for word in words:
            test = word if not current else f"{current} {word}"
            if self.small_font.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word

        if current:
            lines.append(current)

        return lines

    def split_text_for_symbols(self, text: str):
        suit_chars = {"♠", "♣", "♦", "♥"}
        parts = []
        current = ""
        current_is_symbol = None

        for ch in text:
            is_symbol = ch in suit_chars
            if current_is_symbol is None:
                current = ch
                current_is_symbol = is_symbol
            elif is_symbol == current_is_symbol:
                current += ch
            else:
                parts.append((current, current_is_symbol))
                current = ch
                current_is_symbol = is_symbol

        if current:
            parts.append((current, current_is_symbol))

        return parts

    def draw_mixed_font_text(self, text: str, x: int, y: int, color, line_height: int = 24):
        cursor_x = x
        for chunk, is_symbol in self.split_text_for_symbols(text):
            font = self.card_suit_font if is_symbol else self.small_font
            surface = font.render(chunk, True, color)
            draw_y = y + (line_height - surface.get_height()) // 2
            self.screen.blit(surface, (cursor_x, draw_y))
            cursor_x += surface.get_width()

    def draw_mixed_status_text(self, text: str, x: int, y: int, color, line_height: int = 24):
        cursor_x = x
        for chunk, is_symbol in self.split_text_for_symbols(text):
            font = self.card_suit_font if is_symbol else self.font
            if line_height <= 22:
                font = self.card_suit_font if is_symbol else self.small_font

            surface = font.render(chunk, True, color)
            draw_y = y + (line_height - surface.get_height()) // 2
            self.screen.blit(surface, (cursor_x, draw_y))
            cursor_x += surface.get_width()

    def compute_section_layout(self, panel_rect: pygame.Rect, show_standings: bool, show_history: bool):
        gap = 10
        sections = []
        if show_standings:
            sections.append("standings")
        if show_history:
            sections.append("history")

        if not sections:
            return {}

        available_height = panel_rect.height
        min_heights = {"standings": 140, "history": 120}
        total_min = sum(min_heights[s] for s in sections) + gap * (len(sections) - 1)

        rects = {}
        if len(sections) == 1:
            rects[sections[0]] = panel_rect.copy()
            return rects

        if available_height <= total_min:
            standings_h = min_heights["standings"]
            history_h = max(60, available_height - standings_h - gap)
        else:
            standings_h = max(min_heights["standings"], int(available_height * 0.42))
            history_h = available_height - standings_h - gap

        y = panel_rect.y
        if show_standings:
            rects["standings"] = pygame.Rect(panel_rect.x, y, panel_rect.width, standings_h)
            y += standings_h + gap
        if show_history:
            rects["history"] = pygame.Rect(panel_rect.x, y, panel_rect.width, panel_rect.bottom - y)

        return rects

    def is_history_body_hovered(
        self,
        pos: Tuple[int, int],
        history_log: List[str],
        win_counts: dict,
        standings_visible: bool,
        recent_plays_visible: bool,
        history_visible: bool,
        history_width: int,
        history_height: int,
        history_pos: Tuple[int, int]
    ):
        content = self.panel_content_rect(history_visible, history_width, history_height, history_pos)
        if content is None:
            return False

        section_rects = self.compute_section_layout(content, standings_visible, recent_plays_visible)
        history_rect = section_rects.get("history")
        return history_rect is not None and history_rect.collidepoint(pos)

    def max_history_scroll(
        self,
        history_log: List[str],
        win_counts: dict,
        standings_visible: bool,
        recent_plays_visible: bool,
        history_visible: bool,
        history_width: int,
        history_height: int,
        history_pos: Tuple[int, int]
    ):
        if not recent_plays_visible:
            return 0

        content = self.panel_content_rect(history_visible, history_width, history_height, history_pos)
        if content is None:
            return 0

        section_rects = self.compute_section_layout(content, standings_visible, recent_plays_visible)
        history_rect = section_rects.get("history")
        if history_rect is None:
            return 0

        left_padding = 12
        right_padding = 14
        text_width = history_rect.width - left_padding - right_padding - 8

        wrapped_lines = []
        for entry in history_log:
            wrapped_lines.extend(self.wrap_text_lines(entry, text_width))

        line_height = 24
        top_padding = 10
        bottom_padding = 10
        content_height = len(wrapped_lines) * line_height + top_padding + bottom_padding
        return max(0, content_height - history_rect.height)

    def draw_scrollbar(self, body_rect: pygame.Rect, content_height: int, scroll: int):
        if content_height <= body_rect.height:
            return

        track = pygame.Rect(body_rect.right - 8, body_rect.y, 8, body_rect.height)
        pygame.draw.rect(self.screen, COLORS["scroll_track"], track, border_radius=4)

        ratio = body_rect.height / content_height
        thumb_h = max(26, int(track.height * ratio))
        max_thumb_y = track.height - thumb_h
        thumb_y = track.y + int((scroll / max(1, content_height - body_rect.height)) * max_thumb_y)
        thumb = pygame.Rect(track.x, thumb_y, track.width, thumb_h)
        pygame.draw.rect(self.screen, COLORS["scroll_thumb"], thumb, border_radius=4)

    def draw_standings_section(self, rect: pygame.Rect, win_counts: dict):
        self.draw_rounded_rect((34, 40, 46), rect, radius=10)
        pygame.draw.rect(self.screen, COLORS["panel_border"], rect, 1, border_radius=10)

        title = self.score_title_font.render("Match Standings", True, COLORS["active_name"])
        self.screen.blit(title, (rect.x + 12, rect.y + 10))

        rows = self.get_sorted_standings(win_counts)
        leader = self.get_leader(win_counts)
        row_y = rect.y + 42

        if leader is None:
            leader_text = self.small_font.render("Leader: None yet", True, COLORS["muted_text"])
            self.screen.blit(leader_text, (rect.x + 12, row_y))
            row_y += 30
        else:
            leader_name, leader_score = leader
            leader_badge = pygame.Rect(rect.x + 12, row_y, rect.width - 24, 32)
            self.draw_rounded_rect((54, 68, 58), leader_badge, radius=8)
            self.draw_rounded_rect((120, 155, 120), leader_badge, radius=8, width=1)

            leader_text = self.small_font.render(f"Leader: {leader_name}", True, COLORS["text"])
            leader_score_text = self.small_font.render(str(leader_score), True, COLORS["active_name"])
            self.screen.blit(leader_text, (leader_badge.x + 10, leader_badge.y + 7))
            self.screen.blit(leader_score_text, (leader_badge.right - 12 - leader_score_text.get_width(), leader_badge.y + 7))
            row_y += 40

        for idx, (name, wins) in enumerate(rows, start=1):
            if row_y + 28 > rect.bottom - 8:
                break

            row_rect = pygame.Rect(rect.x + 12, row_y, rect.width - 24, 28)
            fill = (38, 44, 50) if idx % 2 else (33, 39, 45)
            self.draw_rounded_rect(fill, row_rect, radius=8)

            rank_text = self.small_font.render(f"{idx}.", True, COLORS["muted_text"])
            name_text = self.small_font.render(name, True, COLORS["text"])
            wins_text = self.small_font.render(str(wins), True, COLORS["active_name"])

            self.screen.blit(rank_text, (row_rect.x + 10, row_rect.y + 5))
            self.screen.blit(name_text, (row_rect.x + 34, row_rect.y + 5))
            self.screen.blit(wins_text, (row_rect.right - 12 - wins_text.get_width(), row_rect.y + 5))
            row_y += 32

    def draw_history_section(self, rect: pygame.Rect, history_log: List[str], history_scroll: int):
        self.draw_rounded_rect((34, 40, 46), rect, radius=10)
        pygame.draw.rect(self.screen, COLORS["panel_border"], rect, 1, border_radius=10)

        title = self.score_title_font.render("Recent Plays", True, COLORS["active_name"])
        self.screen.blit(title, (rect.x + 12, rect.y + 10))

        body = pygame.Rect(rect.x + 6, rect.y + 38, rect.width - 12, rect.height - 44)
        if body.height <= 20:
            return

        clip_prev = self.screen.get_clip()
        self.screen.set_clip(body)

        left_padding = 10
        right_padding = 12
        top_padding = 8
        bottom_padding = 8
        text_width = body.width - left_padding - right_padding - 8

        log_lines = []
        for entry in history_log:
            log_lines.extend(self.wrap_text_lines(entry, text_width))

        line_height = 24
        content_height = len(log_lines) * line_height + top_padding + bottom_padding
        draw_y = body.y + top_padding - history_scroll

        for line in log_lines:
            self.draw_mixed_font_text(line, body.x + left_padding, draw_y, COLORS["muted_text"], line_height)
            draw_y += line_height

        self.screen.set_clip(clip_prev)
        pygame.draw.rect(self.screen, COLORS["panel_border"], body, 1, border_radius=6)
        self.draw_scrollbar(body, content_height, history_scroll)

    def draw_history_panel(
        self,
        history_log: List[str],
        history_scroll: int,
        win_counts: dict,
        standings_visible: bool,
        recent_plays_visible: bool,
        history_visible: bool,
        history_width: int,
        history_height: int,
        history_pos: Tuple[int, int]
    ):
        if not history_visible:
            return

        panel = self.history_panel_rect(history_visible, history_width, history_height, history_pos)
        header = self.history_header_rect(history_visible, history_width, history_height, history_pos)
        handle = self.history_resize_handle_rect(history_visible, history_width, history_height, history_pos)
        content_rect = self.panel_content_rect(history_visible, history_width, history_height, history_pos)

        self.draw_rounded_rect(COLORS["panel"], panel, radius=18)
        self.draw_rounded_rect(COLORS["panel_border"], panel, radius=18, width=2)
        pygame.draw.rect(self.screen, (45, 52, 60), header, border_top_left_radius=18, border_top_right_radius=18)
        pygame.draw.rect(self.screen, COLORS["resize_handle"], handle, border_radius=3)

        title = self.font.render("Match Panel", True, COLORS["text"])
        self.screen.blit(title, (panel.x + 16, panel.y + 10))

        standings_toggle = self.standings_toggle_rect(history_width, history_height, history_pos)
        history_toggle = self.history_toggle_rect(history_width, history_height, history_pos)

        self.draw_rounded_rect((38, 44, 50), standings_toggle, radius=8)
        self.draw_rounded_rect((38, 44, 50), history_toggle, radius=8)

        standings_label = self.small_font.render(
            f"Standings [ON]" if standings_visible else "Standings [OFF]",
            True,
            COLORS["active_name"] if standings_visible else COLORS["muted_text"]
        )
        history_label = self.small_font.render(
            f"History [ON]" if recent_plays_visible else "History [OFF]",
            True,
            COLORS["active_name"] if recent_plays_visible else COLORS["muted_text"]
        )

        self.screen.blit(standings_label, (standings_toggle.x + 10, standings_toggle.y + 6))
        self.screen.blit(history_label, (history_toggle.x + 10, history_toggle.y + 6))

        if content_rect is None:
            return

        section_rects = self.compute_section_layout(content_rect, standings_visible, recent_plays_visible)

        if "standings" in section_rects:
            self.draw_standings_section(section_rects["standings"], win_counts)

        if "history" in section_rects:
            self.draw_history_section(section_rects["history"], history_log, history_scroll)

        if not section_rects:
            empty_text = self.small_font.render("Both sections are hidden", True, COLORS["muted_text"])
            self.screen.blit(empty_text, (content_rect.x + 10, content_rect.y + 10))

    def draw_active_animation(self, active_animation):
        if not active_animation:
            return

        start_x, start_y = active_animation["start_pos"]
        progress = active_animation["progress"]
        cards = active_animation["cards"]
        targets = active_animation["targets"]

        for i, card in enumerate(cards):
            target_rect = targets[i]
            x = start_x + (target_rect.x - start_x) * progress
            y = start_y + (target_rect.y - start_y) * progress
            rect = pygame.Rect(int(x), int(y), CARD_WIDTH, CARD_HEIGHT)
            self.draw_card(card, rect)

    def draw_ui(self, model: dict):
        hands = model["hands"]
        player_names = model["player_names"]
        current_player = model["current_player"]
        prev_combo = model["prev_combo"]
        selected = model["selected"]
        history_log = model["history_log"]
        history_scroll = model["history_scroll"]
        win_counts = model["win_counts"]
        history_visible = model["history_visible"]
        history_width = model["history_width"]
        history_height = model["history_height"]
        history_pos = model["history_pos"]
        message = model["message"]
        active_animation = model["active_animation"]
        game_over = model["game_over"]
        standings_visible = model["standings_visible"]
        recent_plays_visible = model["recent_plays_visible"]

        self.draw_background()
        self.draw_toolbar()

        top_hand = hands[2]
        top_x = (self.width - (len(top_hand.cards) * 18 + 55)) // 2
        self.draw_player_label(
            player_names[2],
            len(top_hand.cards),
            self.width // 2,
            self.toolbar_height + 18,
            current_player == 2,
            center=True
        )
        self.draw_opponent_horizontal(top_hand, top_x, self.toolbar_height + 54)

        self.draw_player_label(
            player_names[1],
            len(hands[1].cards),
            40,
            self.toolbar_height + 122,
            current_player == 1
        )
        self.draw_opponent_vertical(hands[1], 40, self.toolbar_height + 158)

        self.draw_player_label(
            player_names[3],
            len(hands[3].cards),
            self.width - 180,
            self.toolbar_height + 122,
            current_player == 3
        )
        self.draw_opponent_vertical(hands[3], self.width - 95, self.toolbar_height + 158)

        self.draw_hand(hands[0], selected)
        self.draw_player_label(
            player_names[0],
            len(hands[0].cards),
            self.width // 2,
            self.height - 18,
            current_player == 0,
            center=True
        )

        self.draw_play_area(prev_combo, active_animation)
        self.draw_active_animation(active_animation)

        self.draw_button(self.play_button, "Play")
        self.draw_button(self.pass_button, "Pass", alt=True)

        if game_over:
            self.draw_button(self.new_game_button, "New Game", alt=True)

        self.draw_history_panel(
            history_log,
            history_scroll,
            win_counts,
            standings_visible,
            recent_plays_visible,
            history_visible,
            history_width,
            history_height,
            history_pos
        )

        if message:
            self.draw_mixed_status_text(message, 40, self.height - 220, COLORS["message"], 28)

        self.draw_mixed_status_text("Select cards, then click Play", 40, self.height - 190, COLORS["muted_text"], 22)


        pygame.display.flip()

    def get_card_at_pos(self, hand: Hand, pos: Tuple[int, int]) -> Tuple[Optional[int], Optional[pygame.Rect]]:
        spacing = min(55, max(32, int((self.width - 160) / max(13, len(hand.cards) + 1))))
        total_width = ((len(hand.cards) - 1) * spacing) + CARD_WIDTH
        x_start = max(40, (self.width - total_width) // 2)

        for i in range(len(hand.cards) - 1, -1, -1):
            rect = pygame.Rect(x_start + i * spacing, self.hand_y, CARD_WIDTH, CARD_HEIGHT)
            lifted_rect = rect.move(0, -24)
            if lifted_rect.collidepoint(pos) or rect.collidepoint(pos):
                return i, rect

        return None, None

    def get_play_source_position(self, player_index: int):
        if player_index == 0:
            return (self.width // 2 - CARD_WIDTH // 2, self.hand_y - 18)
        if player_index == 1:
            return (92, self.height // 2 - 40)
        if player_index == 2:
            return (self.width // 2 - CARD_WIDTH // 2, self.toolbar_height + 120)
        return (self.width - 150, self.height // 2 - 40)

    def get_board_card_positions(self, count: int):
        spacing = min(72, max(54, int(self.play_area.width / max(4, count + 1))))
        total_width = ((count - 1) * spacing) + CARD_WIDTH
        start_x = self.play_area.centerx - total_width // 2
        y = self.play_area.centery - CARD_HEIGHT // 2 + 6
        return [
            pygame.Rect(start_x + i * spacing, y, CARD_WIDTH, CARD_HEIGHT)
            for i in range(count)
        ]

    def is_play_button_clicked(self, pos: Tuple[int, int]) -> bool:
        return self.play_button.collidepoint(pos)

    def is_pass_button_clicked(self, pos: Tuple[int, int]) -> bool:
        return self.pass_button.collidepoint(pos)

    def is_new_game_button_clicked(self, pos: Tuple[int, int]) -> bool:
        return self.new_game_button.collidepoint(pos)

    def is_toolbar_hard_reset_clicked(self, pos: Tuple[int, int]) -> bool:
        return self.toolbar_hard_reset_button.collidepoint(pos)

    def is_toolbar_toggle_log_clicked(self, pos: Tuple[int, int]) -> bool:
        return self.toolbar_toggle_log_button.collidepoint(pos)

    def is_history_header_clicked(self, pos: Tuple[int, int], history_visible: bool, history_width: int, history_height: int, history_pos: Tuple[int, int]) -> bool:
        header = self.history_header_rect(history_visible, history_width, history_height, history_pos)
        return header is not None and header.collidepoint(pos)

    def is_history_resize_handle_clicked(self, pos: Tuple[int, int], history_visible: bool, history_width: int, history_height: int, history_pos: Tuple[int, int]) -> bool:
        handle = self.history_resize_handle_rect(history_visible, history_width, history_height, history_pos)
        return handle is not None and handle.collidepoint(pos)

    def is_standings_toggle_clicked(self, pos: Tuple[int, int], history_width: int, history_height: int, history_pos: Tuple[int, int]) -> bool:
        return self.standings_toggle_rect(history_width, history_height, history_pos).collidepoint(pos)

    def is_recent_plays_toggle_clicked(
        self,
        pos: Tuple[int, int],
        history_log: List[str],
        win_counts: dict,
        standings_visible: bool,
        recent_plays_visible: bool,
        history_width: int,
        history_height: int,
        history_pos: Tuple[int, int]
    ) -> bool:
        return self.history_toggle_rect(history_width, history_height, history_pos).collidepoint(pos)

    def compute_history_size_from_mouse(self, mouse_pos: Tuple[int, int], history_pos: Tuple[int, int], current_w: int, current_h: int):
        new_w = mouse_pos[0] - history_pos[0]
        new_h = mouse_pos[1] - history_pos[1]
        return new_w, new_h

    def clamp_history_panel_position(self, x: int, y: int, width: int, height: int):
        x = max(20, min(self.width - width - 20, x))
        y = max(self.toolbar_height + 12, min(self.height - height - 20, y))
        return (x, y)
