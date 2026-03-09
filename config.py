SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 900
MIN_WIDTH = 1100
MIN_HEIGHT = 720
FPS = 60

CARD_WIDTH = 90
CARD_HEIGHT = 130

CARD_SUITS = ["♠", "♣", "♦", "♥"]
CARD_RANKS = ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A", "2"]

SUIT_ORDER = {
    "♠": 1,
    "♣": 2,
    "♦": 3,
    "♥": 4,
}

RANK_ORDER = {
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
    "J": 11,
    "Q": 12,
    "K": 13,
    "A": 14,
    "2": 15,
}

PLAYER_NAME_POOL = [
    "Mia", "Ethan", "Zoe", "Lucas",
    "Ava", "Noah", "Chloe", "Liam",
    "Sophie", "Jack", "Ella", "Leo",
    "Nina", "Oscar", "Ruby", "Max",
]

DEFAULT_PANEL_WIDTH = 320
DEFAULT_PANEL_HEIGHT = 320
DEFAULT_PANEL_MARGIN = 20
MIN_PANEL_WIDTH = 240
MIN_PANEL_HEIGHT = 240
MAX_PANEL_WIDTH_RATIO = 0.42
MAX_PANEL_HEIGHT_RATIO = 0.78

BOARD_WIDTH_RATIO = 0.42
BOARD_WIDTH_MAX = 620
BOARD_HEIGHT_RATIO = 0.27
BOARD_SIDE_RESERVE = 180

DEAL_ANIMATION_DURATION = 0.06
DEAL_START_DELAY = 0.01
SCROLL_STEP = 28

COLORS = {
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
    "panel": (28, 34, 40),
    "panel_border": (210, 210, 210),
    "resize_handle": (140, 140, 150),
    "toolbar": (24, 28, 34),
    "toolbar_border": (70, 80, 92),
    "red": (200, 50, 50),
    "black": (30, 30, 30),
    "scroll_track": (55, 62, 70),
    "scroll_thumb": (140, 150, 165),
}
