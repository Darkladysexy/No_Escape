# -------- File: settings.py --------
import pygame

# --- Kích thước và FPS ---
WIDTH, HEIGHT = 800, 600
FPS = 60

# --- Màu sắc ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128, 180) # Màu xám gốc có alpha cho pause
PLAYER_COLOR = BLUE
BOT_COLOR = RED
PLAYER_GOAL_COLOR = PLAYER_COLOR
BOT_GOAL_COLOR = BOT_COLOR

# --- Cài đặt Mê cung ---
WALL_THICKNESS = 2
MAZE_MARGIN_X = 40
MAZE_MARGIN_Y = 40

# --- Cài đặt Level ---
LEVELS = {
    # Level: {cols, rows, time_1p, bot_delay_vs}
    1: {'cols': 10, 'rows': 10, 'time_1p': 30, 'bot_delay_vs': 18},
    2: {'cols': 15, 'rows': 15, 'time_1p': 45, 'bot_delay_vs': 15},
    3: {'cols': 20, 'rows': 20, 'time_1p': 60, 'bot_delay_vs': 12},
}
MAX_LEVEL = 3

# --- Fonts ---
FONT_NAME = 'arial' # Hoặc None để dùng font mặc định
FONT_SIZE_LARGE = 40
FONT_SIZE_BUTTON = 30
FONT_SIZE_INFO = 25
FONT_SIZE_PAUSE = 60

# --- Nút Pause ---
PAUSE_BUTTON_RECT = pygame.Rect(WIDTH - 90, 5, 30, 30)

# --- Màu sắc chủ đề Home Screen mới (Thêm vào đây) ---
DARK_GRAY_BG = (40, 40, 40)       # Màu nền tối (dự phòng nếu ảnh lỗi)
TITLE_RED = (180, 0, 0)          # Màu đỏ sẫm cho tiêu đề
BUTTON_TEXT_LIGHT = (220, 220, 220) # Màu chữ sáng cho nút
BUTTON_BG_DARK = (50, 50, 50, 220) # Màu nền xám tối, hơi trong suốt cho nút thường
EXIT_BUTTON_BG_DARK = (100, 0, 0, 220) # Màu nền đỏ tối, hơi trong suốt cho nút Exit
BUTTON_BORDER_LIGHT = (100, 100, 100) # Màu viền xám nhạt cho nút (tùy chọn)

# -------- Hết file: settings.py --------