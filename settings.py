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
YELLOW = (255, 255, 0) # Màu đích 1P
GRAY = (128, 128, 128, 180) # Màu lớp phủ Pause
# Màu cho VS Bot
PLAYER_COLOR = BLUE
BOT_COLOR = RED
PLAYER_GOAL_COLOR = BOT_COLOR
BOT_GOAL_COLOR = PLAYER_COLOR

# --- Cài đặt Mê cung ---
MAZE_COLS, MAZE_ROWS = 32, 32
WALL_THICKNESS = 2

# Tính toán kích thước ô và offset (đặt ở đây để dễ truy cập)
# Tính CELL_SIZE dựa trên kích thước màn hình và số ô, để lại lề
_CELL_WIDTH = (WIDTH - 40) // MAZE_COLS
_CELL_HEIGHT = (HEIGHT - 40) // MAZE_ROWS
CELL_SIZE = min(_CELL_WIDTH, _CELL_HEIGHT)
# Tính offset để căn giữa
MAZE_OFFSET_X = (WIDTH - MAZE_COLS * CELL_SIZE) // 2
MAZE_OFFSET_Y = (HEIGHT - MAZE_ROWS * CELL_SIZE) // 2
# Kích thước thực tế của surface vẽ mê cung
MAZE_SURFACE_WIDTH = MAZE_COLS * CELL_SIZE + WALL_THICKNESS
MAZE_SURFACE_HEIGHT = MAZE_ROWS * CELL_SIZE + WALL_THICKNESS

# --- Cài đặt Game ---
TIME_LIMIT_1P = 60 # Giây
BOT_MOVE_DELAY = 15 # Frames

# --- Fonts ---
# Có thể định nghĩa tên font ở đây và tải trong file chính hoặc utils
FONT_NAME = 'arial' # Hoặc None để dùng font mặc định
FONT_SIZE_LARGE = 40
FONT_SIZE_BUTTON = 30
FONT_SIZE_INFO = 25 # Timer, Level
FONT_SIZE_PAUSE = 60

# --- Nút Pause ---
PAUSE_BUTTON_RECT = pygame.Rect(WIDTH - 90, 5, 30, 30)