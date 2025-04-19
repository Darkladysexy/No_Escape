# -------- File: one_player.py --------
import pygame
import settings
import utils
# from maze import Maze # Không cần import trực tiếp

def handle_input_1p(event, game_data):
    """Xử lý input riêng cho chế độ 1 Player."""
    player_col, player_row = game_data['player_pos']; current_maze = game_data['maze']; new_game_state = game_data['game_state']
    if event.type == pygame.KEYDOWN:
        old_player_col, old_player_row = player_col, player_row; moved = False
        current_cell = current_maze.get_cell(player_col, player_row) if current_maze else None
        if not current_cell: return new_game_state
        cols, rows = current_maze.cols, current_maze.rows
        if event.key == pygame.K_UP or event.key == pygame.K_w:
            if not current_cell.walls['top']: player_row -= 1; moved = True
        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
            if not current_cell.walls['bottom']: player_row += 1; moved = True
        elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
            if not current_cell.walls['left']: player_col -= 1; moved = True
        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
            if not current_cell.walls['right']: player_col += 1; moved = True
        player_col = max(0, min(player_col, cols - 1)); player_row = max(0, min(player_row, rows - 1))
        if moved:
            next_cell = current_maze.get_cell(player_col, player_row); can_enter = False
            if next_cell:
                if player_row < old_player_row and not next_cell.walls['bottom']: can_enter=True
                elif player_row > old_player_row and not next_cell.walls['top']: can_enter=True
                elif player_col < old_player_col and not next_cell.walls['right']: can_enter=True
                elif player_col > old_player_col and not next_cell.walls['left']: can_enter=True
                elif player_col == old_player_col and player_row == old_player_row: can_enter=True
            if not can_enter: player_col, player_row = old_player_col, old_player_row
        game_data['player_pos'] = (player_col, player_row)
    elif event.type == pygame.MOUSEBUTTONDOWN:
         if event.button == 1:
             if settings.PAUSE_BUTTON_RECT.collidepoint(event.pos): game_data['pause_start_time'] = pygame.time.get_ticks(); new_game_state = 'paused_1p'
    return new_game_state

def update_1p(game_data):
    """Cập nhật logic cho chế độ 1 Player (timer, win/lose)."""
    player_col, player_row = game_data['player_pos']; goal_col, goal_row = game_data['1p_goal_pos']; start_time = game_data['start_time']; time_limit = game_data['time_limit']
    new_game_state = game_data['game_state']; current_ticks = pygame.time.get_ticks(); elapsed_time = (current_ticks - start_time) / 1000; remaining_time = max(0, time_limit - elapsed_time)
    game_data['remaining_time'] = remaining_time
    if player_col == goal_col and player_row == goal_row: new_game_state = 'win_1p'
    elif remaining_time <= 0: new_game_state = 'lose_1p'
    return new_game_state

def draw_1p(screen, maze_surface, game_data, fonts):
    """Vẽ màn hình cho chế độ 1 Player."""
    layout = game_data.get('layout');
    if not layout or not maze_surface: return
    cell_size, offset_x, offset_y = layout['cell_size'], layout['offset_x'], layout['offset_y']
    screen.fill(settings.WHITE); current_maze = game_data['maze']
    if current_maze: current_maze.draw(maze_surface, settings.BLACK, settings.WHITE, settings.WALL_THICKNESS); screen.blit(maze_surface, (offset_x, offset_y))
    goal_col, goal_row = game_data['1p_goal_pos']; player_col, player_row = game_data['player_pos']
    utils.draw_goal(screen, goal_col, goal_row, cell_size, offset_x, offset_y, settings.YELLOW); utils.draw_entity(screen, player_col, player_row, cell_size, offset_x, offset_y, settings.BLUE)
    remaining_time = game_data.get('remaining_time', 0); minutes = int(remaining_time // 60); seconds = int(remaining_time % 60); timer_text = f"Time: {minutes:01}:{seconds:02}"
    current_level = game_data.get('current_level', 0); level_text = f"LV{current_level}"
    utils.draw_text(screen, timer_text, fonts['info'], settings.BLACK, 10, 10, center=False); utils.draw_text(screen, level_text, fonts['info'], settings.BLACK, settings.WIDTH - 50, 10, center=False)
    utils.draw_pause_button(screen)

def handle_input_paused_1p(event, game_data, fonts):
    """Xử lý input cho màn hình Pause 1 Player."""
    new_game_state = game_data['game_state'] # Giữ state hiện tại trừ khi nút được nhấn
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        buttons = utils.draw_pause_menu(pygame.Surface((1,1), pygame.SRCALPHA), fonts)
        mouse_pos = event.pos
        if buttons['continue'].collidepoint(mouse_pos):
            pause_duration = pygame.time.get_ticks() - game_data['pause_start_time']; game_data['start_time'] += pause_duration; new_game_state = '1_player'
        elif buttons['replay'].collidepoint(mouse_pos):
             game_data['action'] = 'replay_1p' # Báo hiệu replay
        elif buttons['exit'].collidepoint(mouse_pos):
             game_data['action'] = 'go_home' # <<< SỬA: Đặt action về home
    return new_game_state # Trả về state hiện tại (pause), chờ action xử lý

def draw_paused_1p(screen, maze_surface, game_data, fonts):
    """Vẽ màn hình Pause 1 Player."""
    if game_data.get('layout') and maze_surface: draw_1p(screen, maze_surface, game_data, fonts)
    utils.draw_pause_menu(screen, fonts)

def handle_input_end_1p(event, game_data, fonts):
    """Xử lý input cho màn hình Win/Lose 1 Player."""
    new_game_state = game_data['game_state']; current_level = game_data['current_level']; is_win = (new_game_state == 'win_1p')
    primary_button_text = "Next Level" if is_win and current_level < settings.MAX_LEVEL else "Chơi lại từ đầu" if is_win else "Replay"
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        buttons = utils.draw_end_menu(pygame.Surface((1,1)), "", (0,0,0), primary_button_text, fonts)
        mouse_pos = event.pos
        if buttons['primary'].collidepoint(mouse_pos):
             if is_win:
                  if current_level < settings.MAX_LEVEL: game_data['action'] = 'next_level_1p'
                  else: game_data['action'] = 'replay_all_1p'
             else: game_data['action'] = 'replay_1p'
        elif buttons['exit'].collidepoint(mouse_pos):
             game_data['action'] = 'go_home' # <<< SỬA: Đặt action về home
    return new_game_state # Trả về state hiện tại (win/lose), chờ action xử lý

def draw_win_1p(screen, game_data, fonts):
    """Vẽ màn hình Win 1 Player."""
    current_level = game_data['current_level']
    if current_level < settings.MAX_LEVEL: button_text = "Next Level"; message = f"Level {current_level} Complete!"
    else: button_text = "Chơi lại từ đầu"; message = "You Win! Hoàn Thành!"
    utils.draw_end_menu(screen, message, settings.GREEN, button_text, fonts)

def draw_lose_1p(screen, game_data, fonts):
    """Vẽ màn hình Lose 1 Player."""
    utils.draw_end_menu(screen, "Game Over", settings.RED, "Replay", fonts)