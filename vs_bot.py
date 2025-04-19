# -------- File: vs_bot.py --------
import pygame
import settings
import utils
# from maze import Maze # Không cần

def handle_input_vs(event, game_data):
    """Xử lý input riêng cho chế độ VS Bot."""
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
             if settings.PAUSE_BUTTON_RECT.collidepoint(event.pos): new_game_state = 'paused_vs'
    return new_game_state

def update_vs(game_data):
    """Cập nhật logic cho chế độ VS Bot."""
    player_col, player_row = game_data['player_pos']
    bot_col, bot_row = game_data['bot_pos'] # Lấy vị trí bot
    vs_player_goal = game_data['vs_player_goal_pos']; bot_goal = game_data['bot_goal_pos']
    bot_path = game_data['bot_path']; bot_move_timer = game_data['bot_move_timer']; bot_delay = game_data['bot_delay']
    new_game_state = game_data['game_state']

    bot_move_timer += 1
    if bot_path and bot_move_timer >= bot_delay:
        bot_move_timer = 0
        current_bot_pos = (bot_col, bot_row)
        # --- Khối try-except ĐÚNG ---
        try:
            # Thụt vào đúng cách
            current_index_in_path = bot_path.index(current_bot_pos)
            # Kiểm tra xem có bước tiếp theo không
            if current_index_in_path + 1 < len(bot_path):
                # Lấy tọa độ bước tiếp theo
                next_col, next_row = bot_path[current_index_in_path + 1]
                # Cập nhật vị trí bot
                bot_col, bot_row = next_col, next_row # <<< Cập nhật biến cục bộ
                game_data['bot_pos'] = (bot_col, bot_row) # <<< Cập nhật game_data

        # Khối except phải thẳng hàng với try
        except ValueError:
            # Bot lệch đường -> tìm lại
            # print(f"Warning: Bot at {current_bot_pos} not found in path. Recalculating...")
            new_path = utils.find_path_bfs(game_data['maze'], current_bot_pos, bot_goal)
            game_data['bot_path'] = new_path if new_path else []
        # --- Kết thúc khối try-except ---

    game_data['bot_move_timer'] = bot_move_timer # Lưu lại timer

    # Kiểm tra thắng thua (dùng bot_col, bot_row đã được cập nhật)
    if (player_col, player_row) == vs_player_goal:
        new_game_state = 'player_wins_vs'
    elif (bot_col, bot_row) == bot_goal:
        new_game_state = 'bot_wins_vs'
    return new_game_state

def draw_vs(screen, maze_surface, game_data, fonts):
    """Vẽ màn hình cho chế độ VS Bot."""
    layout = game_data.get('layout')
    if not layout or not maze_surface: return
    cell_size, offset_x, offset_y = layout['cell_size'], layout['offset_x'], layout['offset_y']
    screen.fill(settings.WHITE); current_maze = game_data['maze']
    if current_maze: current_maze.draw(maze_surface, settings.BLACK, settings.WHITE, settings.WALL_THICKNESS); screen.blit(maze_surface, (offset_x, offset_y))
    vs_player_goal_col, vs_player_goal_row = game_data['vs_player_goal_pos']; bot_goal_col, bot_goal_row = game_data['bot_goal_pos']
    utils.draw_goal(screen, vs_player_goal_col, vs_player_goal_row, cell_size, offset_x, offset_y, settings.PLAYER_GOAL_COLOR); utils.draw_goal(screen, bot_goal_col, bot_goal_row, cell_size, offset_x, offset_y, settings.BOT_GOAL_COLOR)
    player_col, player_row = game_data['player_pos']; bot_col, bot_row = game_data['bot_pos']
    utils.draw_entity(screen, player_col, player_row, cell_size, offset_x, offset_y, settings.PLAYER_COLOR); utils.draw_entity(screen, bot_col, bot_row, cell_size, offset_x, offset_y, settings.BOT_COLOR)
    current_level = game_data.get('current_level', 0); level_text = f"LV{current_level}"; utils.draw_text(screen, level_text, fonts['info'], settings.BLACK, settings.WIDTH - 50, 10, center=False)
    utils.draw_pause_button(screen)

def handle_input_paused_vs(event, game_data, fonts):
    """Xử lý input cho màn hình Pause VS Bot."""
    new_game_state = game_data['game_state']
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        buttons = utils.draw_pause_menu(pygame.Surface((1,1), pygame.SRCALPHA), fonts)
        mouse_pos = event.pos
        if buttons['continue'].collidepoint(mouse_pos): new_game_state = 'vs_bot'
        elif buttons['replay'].collidepoint(mouse_pos): game_data['action'] = 'replay_vs'
        elif buttons['exit'].collidepoint(mouse_pos):
             # new_game_state = 'home' # <<< KHÔNG ĐỔI STATE Ở ĐÂY NỮA
             game_data['action'] = 'go_home' # <<< THAY BẰNG ACTION
    return new_game_state

def draw_paused_vs(screen, maze_surface, game_data, fonts):
    """Vẽ màn hình Pause VS Bot."""
    if game_data.get('layout') and maze_surface: draw_vs(screen, maze_surface, game_data, fonts)
    utils.draw_pause_menu(screen, fonts)

def handle_input_end_vs(event, game_data, fonts):
    """Xử lý input cho màn hình kết thúc VS Bot."""
    new_game_state = game_data['game_state']; current_level = game_data['current_level']; is_player_win = (new_game_state == 'player_wins_vs')
    if is_player_win: primary_button_text = "Next Level" if current_level < settings.MAX_LEVEL else "Chơi lại từ đầu"
    else: primary_button_text = "Replay"
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        buttons = utils.draw_end_menu(pygame.Surface((1,1)), "", (0,0,0), primary_button_text, fonts)
        mouse_pos = event.pos
        if buttons['primary'].collidepoint(mouse_pos):
             if is_player_win:
                  if current_level < settings.MAX_LEVEL: game_data['action'] = 'next_level_vs'
                  else: game_data['action'] = 'replay_all_vs'
             else: game_data['action'] = 'replay_vs'
        elif buttons['exit'].collidepoint(mouse_pos):
             # new_game_state = 'home' # <<< KHÔNG ĐỔI STATE Ở ĐÂY NỮA
             game_data['action'] = 'go_home' # <<< THAY BẰNG ACTION
    return new_game_state

def draw_player_wins_vs(screen, game_data, fonts):
    """Vẽ màn hình Player thắng VS Bot."""
    current_level = game_data['current_level']
    if current_level < settings.MAX_LEVEL: button_text = "Next Level"; message = f"Player Wins Level {current_level}!"
    else: button_text = "Chơi lại từ đầu"; message = "Player Wins! Hoàn Thành!"
    utils.draw_end_menu(screen, message, settings.PLAYER_COLOR, button_text, fonts)

def draw_bot_wins_vs(screen, game_data, fonts):
    """Vẽ màn hình Bot thắng VS Bot."""
    utils.draw_end_menu(screen, "Bot Wins!", settings.BOT_COLOR, "Replay", fonts)