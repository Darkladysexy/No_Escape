# -------- File: utils.py --------
import pygame
from collections import deque
import settings # Đảm bảo import settings

# --- Hàm Tính toán Layout ---
def calculate_maze_layout(cols, rows):
    """Tính toán kích thước ô, offset và kích thước surface dựa trên số cột/hàng."""
    if cols <= 0 or rows <= 0:
        print(f"Lỗi: Số cột ({cols}) hoặc hàng ({rows}) không hợp lệ.")
        return 50, 20, 20, 500, 500 # Ví dụ giá trị mặc định

    cell_width = (settings.WIDTH - settings.MAZE_MARGIN_X) // cols
    cell_height = (settings.HEIGHT - settings.MAZE_MARGIN_Y) // rows
    cell_size = min(cell_width, cell_height)
    if cell_size <= 0: cell_size = 1

    offset_x = (settings.WIDTH - cols * cell_size) // 2
    offset_y = (settings.HEIGHT - rows * cell_size) // 2
    surface_width = cols * cell_size + settings.WALL_THICKNESS
    surface_height = rows * cell_size + settings.WALL_THICKNESS
    return cell_size, offset_x, offset_y, surface_width, surface_height

# --- Hàm Vẽ ---
def draw_text(surface, text, text_font, color, x, y, center=True):
    """Vẽ chữ lên bề mặt với xử lý lỗi font."""
    try:
        if not isinstance(text_font, pygame.font.Font):
             raise ValueError("text_font không phải là đối tượng pygame.font.Font hợp lệ")
        text_surface = text_font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if center: text_rect.center = (x, y)
        else: text_rect.topleft = (x, y)
        surface.blit(text_surface, text_rect)
    except Exception as e:
        print(f"Lỗi vẽ text '{text}' với font {text_font}: {e}")
        try:
             default_font = pygame.font.Font(None, 30)
             fallback_color = settings.WHITE if color != settings.BLACK else settings.BLACK
             text_surface = default_font.render(text, True, fallback_color)
             text_rect = text_surface.get_rect()
             if center: text_rect.center = (x, y)
             else: text_rect.topleft = (x, y)
             surface.blit(text_surface, text_rect)
        except Exception as e_fallback:
             print(f"Lỗi nghiêm trọng khi vẽ text fallback: {e_fallback}")


def draw_entity(surface, col, row, cell_size, offset_x, offset_y, color):
    """Vẽ thực thể tại ô lưới, dùng layout được truyền vào."""
    if cell_size <= 0: return
    center_x = offset_x + col * cell_size + cell_size // 2
    center_y = offset_y + row * cell_size + cell_size // 2
    radius = max(1, cell_size // 3)
    pygame.draw.circle(surface, color, (center_x, center_y), radius)

def draw_goal(surface, col, row, cell_size, offset_x, offset_y, color):
    """Vẽ ô đích tại ô lưới, dùng layout được truyền vào."""
    if cell_size <= 0: return
    rect_size = max(1, cell_size // 2)
    rect_x = offset_x + col * cell_size + (cell_size - rect_size) // 2
    rect_y = offset_y + row * cell_size + (cell_size - rect_size) // 2
    rect = pygame.Rect(rect_x, rect_y, rect_size, rect_size)
    pygame.draw.rect(surface, color, rect)

def draw_pause_button(surface):
    """Vẽ nút pause."""
    pause_bg_color = (100, 100, 100, 180)
    try:
        s = pygame.Surface((settings.PAUSE_BUTTON_RECT.width, settings.PAUSE_BUTTON_RECT.height), pygame.SRCALPHA)
        s.fill(pause_bg_color)
        surface.blit(s, settings.PAUSE_BUTTON_RECT.topleft)
    except Exception as e:
        print(f"Lỗi vẽ nền nút pause: {e}")
        pygame.draw.rect(surface, (100, 100, 100), settings.PAUSE_BUTTON_RECT)

    pygame.draw.rect(surface, settings.WHITE, settings.PAUSE_BUTTON_RECT, 1)

    line_width = 3
    gap = settings.PAUSE_BUTTON_RECT.width // 4
    line_height = settings.PAUSE_BUTTON_RECT.height - 10
    line_y_top = settings.PAUSE_BUTTON_RECT.centery - line_height // 2
    line_y_bottom = line_y_top + line_height
    line_x1 = settings.PAUSE_BUTTON_RECT.centerx - gap // 2
    line_x2 = settings.PAUSE_BUTTON_RECT.centerx + gap // 2

    pygame.draw.line(surface, settings.WHITE, (line_x1, line_y_top), (line_x1, line_y_bottom), line_width)
    pygame.draw.line(surface, settings.WHITE, (line_x2, line_y_top), (line_x2, line_y_bottom), line_width)

def draw_pause_menu(surface, fonts):
    """Vẽ lớp phủ và menu khi pause theo theme mới."""
    overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
    overlay.fill(settings.BUTTON_BG_DARK)
    surface.blit(overlay, (0, 0))

    # Sử dụng font 'pause_title' hoặc 'pause' nếu có, fallback về 'large' -> 'button' -> mặc định
    title_font = fonts.get('pause_title', fonts.get('pause', fonts.get('large', fonts.get('button'))))
    if not title_font: title_font = pygame.font.Font(None, settings.FONT_SIZE_PAUSE)
    draw_text(surface, "Paused", title_font, settings.TITLE_RED, settings.WIDTH // 2, settings.HEIGHT // 4)

    button_width = 220
    button_height = 55
    button_x = settings.WIDTH // 2 - button_width // 2
    continue_button_rect = pygame.Rect(button_x, settings.HEIGHT // 2 - 60, button_width, button_height)
    replay_button_rect = pygame.Rect(button_x, settings.HEIGHT // 2 + 25, button_width, button_height)
    exit_button_rect = pygame.Rect(button_x, settings.HEIGHT // 2 + 110, button_width, button_height)

    try:
        s_continue = pygame.Surface((continue_button_rect.width, continue_button_rect.height), pygame.SRCALPHA)
        s_continue.fill(settings.BUTTON_BG_DARK)
        surface.blit(s_continue, continue_button_rect.topleft)
        pygame.draw.rect(surface, settings.BUTTON_BORDER_LIGHT, continue_button_rect, 2)

        s_replay = pygame.Surface((replay_button_rect.width, replay_button_rect.height), pygame.SRCALPHA)
        s_replay.fill(settings.BUTTON_BG_DARK)
        surface.blit(s_replay, replay_button_rect.topleft)
        pygame.draw.rect(surface, settings.BUTTON_BORDER_LIGHT, replay_button_rect, 2)

        s_exit = pygame.Surface((exit_button_rect.width, exit_button_rect.height), pygame.SRCALPHA)
        s_exit.fill(settings.EXIT_BUTTON_BG_DARK)
        surface.blit(s_exit, exit_button_rect.topleft)
        pygame.draw.rect(surface, settings.BUTTON_BORDER_LIGHT, exit_button_rect, 2)
    except Exception as e_draw:
        print(f"Lỗi vẽ nền/viền nút pause: {e_draw}")

    button_font = fonts.get('button')
    if not button_font: button_font = pygame.font.Font(None, settings.FONT_SIZE_BUTTON)
    draw_text(surface, 'Continue', button_font, settings.BUTTON_TEXT_LIGHT, continue_button_rect.centerx, continue_button_rect.centery)
    draw_text(surface, 'Replay', button_font, settings.BUTTON_TEXT_LIGHT, replay_button_rect.centerx, replay_button_rect.centery)
    draw_text(surface, 'Exit', button_font, settings.BUTTON_TEXT_LIGHT, exit_button_rect.centerx, exit_button_rect.centery)

    return {'continue': continue_button_rect, 'replay': replay_button_rect, 'exit': exit_button_rect}


def draw_end_menu(surface, message, message_color, primary_button_text, fonts):
    """Vẽ màn hình kết thúc với theme mới."""
    surface.fill(settings.DARK_GRAY_BG)

    title_font = fonts.get('large', fonts.get('button'))
    if not title_font: title_font = pygame.font.Font(None, settings.FONT_SIZE_LARGE)
    draw_text(surface, message, title_font, message_color, settings.WIDTH // 2, settings.HEIGHT // 3)

    button_width = 220
    button_height = 55
    button_x = settings.WIDTH // 2 - button_width // 2
    primary_button_rect = pygame.Rect(button_x, settings.HEIGHT // 2 + 20, button_width, button_height)
    exit_button_rect = pygame.Rect(button_x, settings.HEIGHT // 2 + 100, button_width, button_height)

    try:
        s_primary = pygame.Surface((primary_button_rect.width, primary_button_rect.height), pygame.SRCALPHA)
        s_primary.fill(settings.BUTTON_BG_DARK)
        surface.blit(s_primary, primary_button_rect.topleft)
        pygame.draw.rect(surface, settings.BUTTON_BORDER_LIGHT, primary_button_rect, 2)

        s_exit = pygame.Surface((exit_button_rect.width, exit_button_rect.height), pygame.SRCALPHA)
        s_exit.fill(settings.EXIT_BUTTON_BG_DARK)
        surface.blit(s_exit, exit_button_rect.topleft)
        pygame.draw.rect(surface, settings.BUTTON_BORDER_LIGHT, exit_button_rect, 2)
    except Exception as e_draw:
        print(f"Lỗi vẽ nền/viền nút end: {e_draw}")

    button_font = fonts.get('button')
    if not button_font: button_font = pygame.font.Font(None, settings.FONT_SIZE_BUTTON)
    draw_text(surface, primary_button_text, button_font, settings.BUTTON_TEXT_LIGHT, primary_button_rect.centerx, primary_button_rect.centery)
    draw_text(surface, 'Exit', button_font, settings.BUTTON_TEXT_LIGHT, exit_button_rect.centerx, exit_button_rect.centery)

    return {'primary': primary_button_rect, 'exit': exit_button_rect}


# --- Hàm Tìm đường ---
def find_path_bfs(maze, start_coords, goal_coords):
    """Tìm đường đi ngắn nhất từ start_coords đến goal_coords bằng BFS, kiểm tra tường 2 chiều."""
    if not maze:
        print("Lỗi BFS: Đối tượng maze không hợp lệ.")
        return None
    cols, rows = maze.cols, maze.rows
    start_col, start_row = start_coords
    goal_col, goal_row = goal_coords

    if not (0 <= start_col < cols and 0 <= start_row < rows and
            0 <= goal_col < cols and 0 <= goal_row < rows):
        print(f"Warning: Tọa độ không hợp lệ trong BFS: start={start_coords}, goal={goal_coords}, maze_dims=({cols},{rows})")
        return None
    if start_coords == goal_coords: return [start_coords]

    queue = deque([(start_col, start_row, [])]) # path là list các tọa độ (col, row)
    visited = set([(start_col, start_row)])

    while queue:
        curr_col, curr_row, path = queue.popleft()

        if curr_col == goal_col and curr_row == goal_row:
            full_path = path + [(curr_col, curr_row)]
            return full_path

        current_cell = maze.get_cell(curr_col, curr_row)
        if not current_cell: continue

        moves = [
            (0, -1, 'top', 'bottom'), # Lên
            (0, 1, 'bottom', 'top'),   # Xuống
            (-1, 0, 'left', 'right'),  # Trái
            (1, 0, 'right', 'left')   # Phải
        ]

        for dx, dy, current_wall, neighbor_wall in moves:
            next_col, next_row = curr_col + dx, curr_row + dy

            if 0 <= next_col < cols and 0 <= next_row < rows and (next_col, next_row) not in visited:
                if not current_cell.walls[current_wall]:
                    neighbor_cell = maze.get_cell(next_col, next_row)
                    if neighbor_cell and not neighbor_cell.walls[neighbor_wall]:
                        visited.add((next_col, next_row))
                        new_path = path + [(curr_col, curr_row)]
                        queue.append((next_col, next_row, new_path))

    print(f"Warning: BFS không tìm thấy đường từ {start_coords} đến {goal_coords}")
    return None

# -------- Hết file: utils.py --------