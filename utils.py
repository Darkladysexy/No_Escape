# -------- File: utils.py --------
import pygame
from collections import deque
import settings

# --- Hàm Tính toán Layout ---
def calculate_maze_layout(cols, rows):
    """Tính toán kích thước ô, offset và kích thước surface dựa trên số cột/hàng."""
    cell_width = (settings.WIDTH - settings.MAZE_MARGIN_X) // cols
    cell_height = (settings.HEIGHT - settings.MAZE_MARGIN_Y) // rows
    cell_size = min(cell_width, cell_height)
    offset_x = (settings.WIDTH - cols * cell_size) // 2
    offset_y = (settings.HEIGHT - rows * cell_size) // 2
    surface_width = cols * cell_size + settings.WALL_THICKNESS
    surface_height = rows * cell_size + settings.WALL_THICKNESS
    return cell_size, offset_x, offset_y, surface_width, surface_height

# --- Hàm Vẽ ---
def draw_text(surface, text, text_font, color, x, y, center=True):
    """Vẽ chữ lên bề mặt."""
    text_surface = text_font.render(text, True, color); text_rect = text_surface.get_rect()
    if center: text_rect.center = (x, y)
    else: text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

def draw_entity(surface, col, row, cell_size, offset_x, offset_y, color):
    """Vẽ thực thể tại ô lưới, dùng layout được truyền vào."""
    center_x = offset_x + col * cell_size + cell_size // 2
    center_y = offset_y + row * cell_size + cell_size // 2
    radius = cell_size // 3
    pygame.draw.circle(surface, color, (center_x, center_y), radius)

def draw_goal(surface, col, row, cell_size, offset_x, offset_y, color):
    """Vẽ ô đích tại ô lưới, dùng layout được truyền vào."""
    rect_x = offset_x + col * cell_size + cell_size // 4
    rect_y = offset_y + row * cell_size + cell_size // 4
    rect = pygame.Rect(rect_x, rect_y, cell_size // 2, cell_size // 2)
    pygame.draw.rect(surface, color, rect)

def draw_pause_button(surface):
    """Vẽ nút pause."""
    pygame.draw.rect(surface, settings.GRAY[:3], settings.PAUSE_BUTTON_RECT)
    line_x1 = settings.PAUSE_BUTTON_RECT.centerx - settings.PAUSE_BUTTON_RECT.width // 6; line_x2 = settings.PAUSE_BUTTON_RECT.centerx + settings.PAUSE_BUTTON_RECT.width // 6
    line_y_top = settings.PAUSE_BUTTON_RECT.top + 5; line_y_bottom = settings.PAUSE_BUTTON_RECT.bottom - 5
    pygame.draw.line(surface, settings.WHITE, (line_x1, line_y_top), (line_x1, line_y_bottom), 3); pygame.draw.line(surface, settings.WHITE, (line_x2, line_y_top), (line_x2, line_y_bottom), 3)

def draw_pause_menu(surface, fonts):
    """Vẽ lớp phủ và menu khi pause."""
    overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA); overlay.fill(settings.GRAY); surface.blit(overlay, (0, 0))
    draw_text(surface, "Paused", fonts['pause'], settings.WHITE, settings.WIDTH // 2, settings.HEIGHT // 4)
    continue_button = pygame.Rect(settings.WIDTH // 2 - 100, settings.HEIGHT // 2 - 50, 200, 50); replay_button = pygame.Rect(settings.WIDTH // 2 - 100, settings.HEIGHT // 2 + 20, 200, 50); exit_button = pygame.Rect(settings.WIDTH // 2 - 100, settings.HEIGHT // 2 + 90, 200, 50)
    pygame.draw.rect(surface, settings.GREEN, continue_button); pygame.draw.rect(surface, settings.BLUE, replay_button); pygame.draw.rect(surface, settings.RED, exit_button)
    draw_text(surface, 'Continue', fonts['button'], settings.BLACK, continue_button.centerx, continue_button.centery); draw_text(surface, 'Replay', fonts['button'], settings.BLACK, replay_button.centerx, replay_button.centery); draw_text(surface, 'Exit', fonts['button'], settings.BLACK, exit_button.centerx, exit_button.centery)
    return {'continue': continue_button, 'replay': replay_button, 'exit': exit_button}

def draw_end_menu(surface, message, message_color, primary_button_text, fonts):
    """Vẽ màn hình kết thúc với nút chính và nút Exit."""
    surface.fill(settings.WHITE)
    draw_text(surface, message, fonts['large'], message_color, settings.WIDTH // 2, settings.HEIGHT // 3)
    primary_button = pygame.Rect(settings.WIDTH // 2 - 100, settings.HEIGHT // 2 + 20, 200, 50)
    exit_button = pygame.Rect(settings.WIDTH // 2 - 100, settings.HEIGHT // 2 + 90, 200, 50)
    pygame.draw.rect(surface, settings.GREEN, primary_button)
    pygame.draw.rect(surface, settings.RED, exit_button)
    draw_text(surface, primary_button_text, fonts['button'], settings.BLACK, primary_button.centerx, primary_button.centery); draw_text(surface, 'Exit', fonts['button'], settings.BLACK, exit_button.centerx, exit_button.centery)
    return {'primary': primary_button, 'exit': exit_button}


# --- Hàm Tìm đường ---
def find_path_bfs(maze, start_coords, goal_coords):
    """Tìm đường đi ngắn nhất từ start_coords đến goal_coords bằng BFS."""
    cols, rows = maze.cols, maze.rows; start_col, start_row = start_coords; goal_col, goal_row = goal_coords
    if not (0 <= start_col < cols and 0 <= start_row < rows and 0 <= goal_col < cols and 0 <= goal_row < rows): return None
    if start_coords == goal_coords: return [start_coords]
    queue = deque([(start_col, start_row, [])]); visited = set([(start_col, start_row)])
    while queue:
        curr_col, curr_row, path = queue.popleft()
        if curr_col == goal_col and curr_row == goal_row: return path + [(curr_col, curr_row)]
        current_cell = maze.get_cell(curr_col, curr_row);
        if not current_cell: continue
        possible_moves = []; neighbor_coords = (curr_col, curr_row - 1);
        if not current_cell.walls['top'] and curr_row > 0 and neighbor_coords not in visited: possible_moves.append(neighbor_coords)
        neighbor_coords = (curr_col, curr_row + 1);
        if not current_cell.walls['bottom'] and curr_row < rows - 1 and neighbor_coords not in visited: possible_moves.append(neighbor_coords)
        neighbor_coords = (curr_col - 1, curr_row);
        if not current_cell.walls['left'] and curr_col > 0 and neighbor_coords not in visited: possible_moves.append(neighbor_coords)
        neighbor_coords = (curr_col + 1, curr_row);
        if not current_cell.walls['right'] and curr_col < cols - 1 and neighbor_coords not in visited: possible_moves.append(neighbor_coords)
        for next_col, next_row in possible_moves: visited.add((next_col, next_row)); new_path = path + [(curr_col, curr_row)]; queue.append((next_col, next_row, new_path))
    return None