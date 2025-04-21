# -------- File: vs_bot.py --------
import pygame
import settings
import utils
# from maze import Maze # Không cần

def handle_input_vs(event, game_data):
    """Xử lý input riêng cho chế độ VS Bot (chỉ di chuyển)."""
    # Chuyển sang Pause đã xử lý ở noescape.py
    player_col, player_row = game_data['player_pos']
    current_maze = game_data.get('maze')
    new_game_state = game_data['game_state'] # Giữ state hiện tại

    if not current_maze: return new_game_state

    if event.type == pygame.KEYDOWN:
        old_player_col, old_player_row = player_col, player_row
        moved = False
        current_cell = current_maze.get_cell(player_col, player_row)
        if not current_cell: return new_game_state

        cols, rows = current_maze.cols, current_maze.rows
        target_col, target_row = player_col, player_row

        # Xác định di chuyển dựa trên phím bấm và tường ô hiện tại
        if event.key == pygame.K_UP or event.key == pygame.K_w:
            if not current_cell.walls['top'] and player_row > 0:
                target_row -= 1; moved = True
        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
            if not current_cell.walls['bottom'] and player_row < rows - 1:
                target_row += 1; moved = True
        elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
            if not current_cell.walls['left'] and player_col > 0:
                target_col -= 1; moved = True
        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
            if not current_cell.walls['right'] and player_col < cols - 1:
                target_col += 1; moved = True

        # Nếu có ý định di chuyển, kiểm tra tường của ô đích
        if moved:
            target_cell = current_maze.get_cell(target_col, target_row)
            can_enter = False
            if target_cell:
                # Kiểm tra tường tương ứng của ô đích
                if target_row < old_player_row and not target_cell.walls['bottom']: can_enter=True
                elif target_row > old_player_row and not target_cell.walls['top']: can_enter=True
                elif target_col < old_player_col and not target_cell.walls['right']: can_enter=True
                elif target_col > old_player_col and not target_cell.walls['left']: can_enter=True

            if can_enter:
                game_data['player_pos'] = (target_col, target_row)
            # else: vị trí không đổi

    # Không xử lý MOUSEBUTTONDOWN ở đây
    return new_game_state


def update_vs(game_data):
    """Cập nhật logic cho chế độ VS Bot (Bot di chuyển, win/lose)."""
    player_col, player_row = game_data['player_pos']
    bot_col, bot_row = game_data['bot_pos'] # Lấy vị trí bot
    vs_player_goal = game_data.get('vs_player_goal_pos', (-1, -1)) # Đích của Player
    bot_goal = game_data.get('bot_goal_pos', (-1, -1))          # Đích của Bot
    bot_path = game_data.get('bot_path', [])
    bot_move_timer = game_data.get('bot_move_timer', 0)
    bot_delay = game_data.get('bot_delay', 15) # Độ trễ di chuyển của bot
    current_maze = game_data.get('maze')
    new_game_state = game_data['game_state']

    # --- Bot Movement Logic ---
    bot_move_timer += 1
    if bot_path and bot_move_timer >= bot_delay:
        bot_move_timer = 0 # Reset timer
        current_bot_pos = (bot_col, bot_row)

        try:
            # Tìm index của vị trí hiện tại trong path
            current_index_in_path = bot_path.index(current_bot_pos)

            # Kiểm tra xem có bước tiếp theo không
            if current_index_in_path + 1 < len(bot_path):
                # Lấy tọa độ bước tiếp theo
                next_col, next_row = bot_path[current_index_in_path + 1]
                # Cập nhật vị trí bot trong game_data
                game_data['bot_pos'] = (next_col, next_row)
                # Cập nhật biến cục bộ để kiểm tra thắng thua ngay trong frame này
                bot_col, bot_row = next_col, next_row
            # else: Bot đã ở cuối path (đích) hoặc path chỉ có 1 điểm

        except ValueError:
            # Bot không có trên đường đi dự tính (có thể do lỗi hoặc thay đổi mê cung?)
            # Cố gắng tìm lại đường đi từ vị trí hiện tại của bot
            print(f"Warning: Bot tại {current_bot_pos} không tìm thấy trong path. Tính toán lại...")
            if current_maze:
                new_path = utils.find_path_bfs(current_maze, current_bot_pos, bot_goal)
                game_data['bot_path'] = new_path if new_path else []
                # print(f"New path: {game_data['bot_path']}") # Debug
            else:
                 game_data['bot_path'] = [] # Không có maze thì không tìm được path

    game_data['bot_move_timer'] = bot_move_timer # Lưu lại timer

    # --- Kiểm tra Thắng Thua ---
    # Sử dụng bot_col, bot_row đã được cập nhật (nếu bot di chuyển)
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
    screen.fill(settings.WHITE) # Nền trắng cho game

    # Vẽ mê cung
    screen.blit(maze_surface, (offset_x, offset_y))

    # Vẽ đích của Player và Bot
    vs_player_goal_col, vs_player_goal_row = game_data.get('vs_player_goal_pos', (-1,-1))
    bot_goal_col, bot_goal_row = game_data.get('bot_goal_pos', (-1,-1))
    # Player goal (đích của player) màu của bot, Bot goal màu của player
    utils.draw_goal(screen, vs_player_goal_col, vs_player_goal_row, cell_size, offset_x, offset_y, settings.BOT_GOAL_COLOR)
    utils.draw_goal(screen, bot_goal_col, bot_goal_row, cell_size, offset_x, offset_y, settings.PLAYER_GOAL_COLOR)

    # Vẽ Player và Bot
    player_col, player_row = game_data['player_pos']
    bot_col, bot_row = game_data['bot_pos']
    utils.draw_entity(screen, player_col, player_row, cell_size, offset_x, offset_y, settings.PLAYER_COLOR)
    utils.draw_entity(screen, bot_col, bot_row, cell_size, offset_x, offset_y, settings.BOT_COLOR)

    # Vẽ thông tin Level
    current_level = game_data.get('current_level', 0)
    level_text = f"LV {current_level}"
    info_font = fonts.get('info') # Lấy font info
    if not info_font: info_font = pygame.font.Font(None, settings.FONT_SIZE_INFO) # Font mặc định
    utils.draw_text(screen, level_text, info_font, settings.BLACK, settings.WIDTH - 60, 10, center=False)

    # Vẽ nút pause
    utils.draw_pause_button(screen)


def handle_input_paused_vs(event, game_data, fonts):
    """Xử lý input cho màn hình Pause VS Bot."""
    new_game_state = game_data['game_state'] # Giữ state hiện tại trừ khi nút được nhấn
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        # Lấy rect của các nút từ hàm vẽ
        dummy_surface = pygame.Surface((1,1), pygame.SRCALPHA)
        buttons = utils.draw_pause_menu(dummy_surface, fonts)
        mouse_pos = event.pos

        if buttons['continue'].collidepoint(mouse_pos):
            new_game_state = 'vs_bot' # Quay lại game
        elif buttons['replay'].collidepoint(mouse_pos):
            game_data['action'] = 'replay_vs' # Báo hiệu replay
            # Không cần đổi state
        elif buttons['exit'].collidepoint(mouse_pos):
             game_data['action'] = 'go_home' # Báo hiệu về home
             # Không cần đổi state

    return new_game_state


def draw_paused_vs(screen, maze_surface, game_data, fonts):
    """Vẽ màn hình Pause VS Bot."""
    # Vẽ lại màn hình game phía dưới hơi mờ
    if game_data.get('layout') and maze_surface:
        temp_surface = screen.copy()
        draw_vs(temp_surface, maze_surface, game_data, fonts) # Vẽ game lên surface tạm
        temp_surface.set_alpha(100) # Làm mờ
        screen.blit(temp_surface, (0,0))
    else:
        screen.fill(settings.DARK_GRAY_BG)

    # Vẽ menu pause lên trên
    utils.draw_pause_menu(screen, fonts)


def handle_input_end_vs(event, game_data, fonts):
    """Xử lý input cho màn hình kết thúc VS Bot."""
    new_game_state = game_data['game_state']
    current_level = game_data.get('current_level', 1)
    is_player_win = (new_game_state == 'player_wins_vs')

    primary_button_text = "Next Level" if is_player_win and current_level < settings.MAX_LEVEL else "Replay All" if is_player_win else "Replay"

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        # Lấy rect của nút từ hàm vẽ
        dummy_surface = pygame.Surface((1,1))
        # Xác định màu chữ thông báo
        message_color = settings.BUTTON_TEXT_LIGHT if is_player_win else settings.TITLE_RED
        buttons = utils.draw_end_menu(dummy_surface, "", message_color, primary_button_text, fonts)
        mouse_pos = event.pos

        if buttons['primary'].collidepoint(mouse_pos):
             if is_player_win:
                  if current_level < settings.MAX_LEVEL:
                      game_data['action'] = 'next_level_vs'
                  else:
                      game_data['action'] = 'replay_all_vs' # Thắng level cuối -> chơi lại từ đầu
             else: # Bot Wins
                  game_data['action'] = 'replay_vs' # Chơi lại level hiện tại
        elif buttons['exit'].collidepoint(mouse_pos):
             game_data['action'] = 'go_home'

    return new_game_state # Giữ state win/lose cho đến khi action được xử lý


def draw_player_wins_vs(screen, game_data, fonts):
    """Vẽ màn hình Player thắng VS Bot theo theme mới."""
    current_level = game_data.get('current_level', 1)
    if current_level < settings.MAX_LEVEL:
        button_text = "Next Level"
        message = f"YOU WIN Level {current_level}!"
    else:
        button_text = "Replay All"
        message = "YOU DEFEATED THE BOT!"
    # Màu chữ sáng (BUTTON_TEXT_LIGHT) cho thông báo thắng
    utils.draw_end_menu(screen, message, settings.BUTTON_TEXT_LIGHT, button_text, fonts)


def draw_bot_wins_vs(screen, game_data, fonts):
    """Vẽ màn hình Bot thắng VS Bot theo theme mới."""
    # Màu chữ đỏ (TITLE_RED) cho thông báo thua
    utils.draw_end_menu(screen, "BOT WINS!", settings.TITLE_RED, "Replay", fonts)

# -------- Hết file: vs_bot.py --------