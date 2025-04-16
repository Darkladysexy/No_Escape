# -------- File: one_player.py --------
import pygame
import settings
import utils
from maze import Maze # Cần để khởi tạo lại maze khi replay

# Biến cục bộ cho module này (hoặc truyền qua game_data)
# Ví dụ: pause_start_time_1p = 0 # Nên quản lý ở file chính tốt hơn

def handle_input_1p(event, game_data):
    """Xử lý input riêng cho chế độ 1 Player."""
    player_col, player_row = game_data['player_pos']
    current_maze = game_data['maze']
    new_game_state = game_data['game_state'] # Trạng thái hiện tại

    if event.type == pygame.KEYDOWN:
        old_player_col, old_player_row = player_col, player_row
        moved = False
        current_cell = current_maze.get_cell(player_col, player_row) if current_maze else None
        if not current_cell: return player_col, player_row, new_game_state # Không làm gì nếu không có ô

        # Kiểm tra tường ô hiện tại
        if event.key == pygame.K_UP or event.key == pygame.K_w:
            if not current_cell.walls['top']: player_row -= 1; moved = True
        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
            if not current_cell.walls['bottom']: player_row += 1; moved = True
        elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
            if not current_cell.walls['left']: player_col -= 1; moved = True
        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
            if not current_cell.walls['right']: player_col += 1; moved = True

        # Giữ trong biên
        player_col = max(0, min(player_col, settings.MAZE_COLS - 1))
        player_row = max(0, min(player_row, settings.MAZE_ROWS - 1))

        # Kiểm tra có vào được ô mới không
        if moved:
            next_cell = current_maze.get_cell(player_col, player_row)
            can_enter = False
            if next_cell:
                if player_row < old_player_row and not next_cell.walls['bottom']: can_enter=True
                elif player_row > old_player_row and not next_cell.walls['top']: can_enter=True
                elif player_col < old_player_col and not next_cell.walls['right']: can_enter=True
                elif player_col > old_player_col and not next_cell.walls['left']: can_enter=True
                elif player_col == old_player_col and player_row == old_player_row: can_enter=True
            if not can_enter: player_col, player_row = old_player_col, old_player_row

    elif event.type == pygame.MOUSEBUTTONDOWN:
         if event.button == 1:
             # Kiểm tra click nút pause
             if settings.PAUSE_BUTTON_RECT.collidepoint(event.pos):
                 game_data['pause_start_time'] = pygame.time.get_ticks() # Lưu thời điểm pause
                 new_game_state = 'paused_1p'

    # Trả về vị trí mới và trạng thái mới (có thể không đổi)
    game_data['player_pos'] = (player_col, player_row)
    return new_game_state


def update_1p(game_data):
    """Cập nhật logic cho chế độ 1 Player (timer, win/lose)."""
    player_col, player_row = game_data['player_pos']
    goal_col, goal_row = game_data['1p_goal_pos']
    start_time = game_data['start_time']
    new_game_state = game_data['game_state'] # Trạng thái hiện tại

    # Tính thời gian
    current_ticks = pygame.time.get_ticks()
    elapsed_time = (current_ticks - start_time) / 1000
    remaining_time = max(0, settings.TIME_LIMIT_1P - elapsed_time)
    game_data['remaining_time'] = remaining_time # Cập nhật thời gian còn lại

    # Kiểm tra thắng/thua
    if player_col == goal_col and player_row == goal_row:
        new_game_state = 'win_1p'
    elif remaining_time <= 0:
        new_game_state = 'lose_1p'

    return new_game_state


def draw_1p(screen, maze_surface, game_data, fonts):
    """Vẽ màn hình cho chế độ 1 Player."""
    screen.fill(settings.WHITE)
    # Vẽ mê cung
    current_maze = game_data['maze']
    if current_maze:
        current_maze.draw(maze_surface, settings.BLACK, settings.WHITE, settings.WALL_THICKNESS)
        screen.blit(maze_surface, (settings.MAZE_OFFSET_X, settings.MAZE_OFFSET_Y))
    # Vẽ đích và người chơi
    goal_col, goal_row = game_data['1p_goal_pos']
    player_col, player_row = game_data['player_pos']
    utils.draw_goal(screen, goal_col, goal_row, settings.YELLOW)
    utils.draw_entity(screen, player_col, player_row, settings.BLUE)
    # Vẽ thông tin
    remaining_time = game_data.get('remaining_time', settings.TIME_LIMIT_1P)
    minutes = int(remaining_time // 60)
    seconds = int(remaining_time % 60)
    timer_text = f"Time: {minutes:01}:{seconds:02}"
    utils.draw_text(screen, timer_text, fonts['info'], settings.BLACK, 10, 10, center=False)
    utils.draw_text(screen, "LV1", fonts['info'], settings.BLACK, settings.WIDTH - 50, 10, center=False)
    # Vẽ nút Pause
    utils.draw_pause_button(screen)


def handle_input_paused_1p(event, game_data):
    """Xử lý input cho màn hình Pause 1 Player."""
    new_game_state = game_data['game_state']
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        # Lấy rect các nút từ hàm vẽ (hơi bất tiện, có thể tối ưu)
        # Tạm thời định nghĩa lại ở đây để xử lý click
        continue_button = pygame.Rect(settings.WIDTH // 2 - 100, settings.HEIGHT // 2 - 50, 200, 50)
        replay_button = pygame.Rect(settings.WIDTH // 2 - 100, settings.HEIGHT // 2 + 20, 200, 50)
        exit_button = pygame.Rect(settings.WIDTH // 2 - 100, settings.HEIGHT // 2 + 90, 200, 50)

        if continue_button.collidepoint(event.pos):
            pause_duration = pygame.time.get_ticks() - game_data['pause_start_time']
            game_data['start_time'] += pause_duration # Bù giờ
            new_game_state = '1_player'
        elif replay_button.collidepoint(event.pos):
             # Reset game data for 1P replay
             game_data['maze'] = Maze(settings.MAZE_COLS, settings.MAZE_ROWS, settings.CELL_SIZE)
             game_data['player_pos'] = game_data['maze'].entry_pos
             game_data['1p_goal_pos'] = game_data['maze'].exit_pos
             game_data['start_time'] = pygame.time.get_ticks()
             game_data['remaining_time'] = settings.TIME_LIMIT_1P
             new_game_state = '1_player'
        elif exit_button.collidepoint(event.pos):
             new_game_state = 'home'
    return new_game_state

def draw_paused_1p(screen, maze_surface, game_data, fonts):
    """Vẽ màn hình Pause 1 Player."""
    # Vẽ lại màn hình game ở dưới
    draw_1p(screen, maze_surface, game_data, fonts)
    # Vẽ lớp phủ và menu
    utils.draw_pause_menu(screen, fonts) # Hàm này vẽ và trả về rect, nhưng ta ko dùng ở đây

def handle_input_end_1p(event, game_data):
    """Xử lý input cho màn hình Win/Lose 1 Player."""
    new_game_state = game_data['game_state']
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        replay_button = pygame.Rect(settings.WIDTH // 2 - 100, settings.HEIGHT // 2 + 20, 200, 50)
        exit_button = pygame.Rect(settings.WIDTH // 2 - 100, settings.HEIGHT // 2 + 90, 200, 50)

        if replay_button.collidepoint(event.pos):
             # Reset game data for 1P replay
             game_data['maze'] = Maze(settings.MAZE_COLS, settings.MAZE_ROWS, settings.CELL_SIZE)
             game_data['player_pos'] = game_data['maze'].entry_pos
             game_data['1p_goal_pos'] = game_data['maze'].exit_pos
             game_data['start_time'] = pygame.time.get_ticks()
             game_data['remaining_time'] = settings.TIME_LIMIT_1P
             new_game_state = '1_player'
        elif exit_button.collidepoint(event.pos):
             new_game_state = 'home'
    return new_game_state

def draw_win_1p(screen, game_data, fonts):
    """Vẽ màn hình Win 1 Player."""
    utils.draw_end_menu(screen, "You Win!", settings.GREEN, fonts)

def draw_lose_1p(screen, game_data, fonts):
    """Vẽ màn hình Lose 1 Player."""
    utils.draw_end_menu(screen, "Game Over", settings.RED, fonts)