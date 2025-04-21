# -------- File: one_player.py --------
import pygame
import settings
import utils
# from maze import Maze # Không cần import trực tiếp

def handle_input_1p(event, game_data):
    """Xử lý input riêng cho chế độ 1 Player (chỉ di chuyển)."""
    # Việc chuyển sang Pause đã được xử lý ở vòng lặp chính (noescape.py)
    player_col, player_row = game_data['player_pos']
    current_maze = game_data.get('maze')
    new_game_state = game_data['game_state'] # Giữ state hiện tại

    if not current_maze: return new_game_state # Không có maze thì không làm gì

    if event.type == pygame.KEYDOWN:
        old_player_col, old_player_row = player_col, player_row
        moved = False
        current_cell = current_maze.get_cell(player_col, player_row)
        if not current_cell: return new_game_state # Không lấy được ô hiện tại

        cols, rows = current_maze.cols, current_maze.rows

        # Xác định di chuyển dựa trên phím bấm và tường ô hiện tại
        target_col, target_row = player_col, player_row
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
                if target_row < old_player_row and not target_cell.walls['bottom']: can_enter=True # Đi lên -> check tường dưới ô đích
                elif target_row > old_player_row and not target_cell.walls['top']: can_enter=True # Đi xuống -> check tường trên ô đích
                elif target_col < old_player_col and not target_cell.walls['right']: can_enter=True # Đi trái -> check tường phải ô đích
                elif target_col > old_player_col and not target_cell.walls['left']: can_enter=True # Đi phải -> check tường trái ô đích

            if can_enter:
                # Chỉ cập nhật vị trí nếu có thể đi vào ô đích
                game_data['player_pos'] = (target_col, target_row)
            # else: vị trí không đổi

    # Không xử lý MOUSEBUTTONDOWN ở đây nữa, đã chuyển sang noescape.py
    return new_game_state # Luôn trả về state hiện tại, không thay đổi state ở đây


def update_1p(game_data):
    """Cập nhật logic cho chế độ 1 Player (timer, win/lose)."""
    player_col, player_row = game_data['player_pos']
    goal_col, goal_row = game_data.get('1p_goal_pos', (-1, -1)) # Lấy vị trí đích
    start_time = game_data.get('start_time', 0)
    time_limit = game_data.get('time_limit', 60) # Thời gian giới hạn mặc định
    pause_start_time = game_data.get('pause_start_time', 0) # Thời điểm bắt đầu pause

    new_game_state = game_data['game_state']

    # Nếu đang không pause thì mới tính thời gian
    if pause_start_time == 0:
        current_ticks = pygame.time.get_ticks()
        elapsed_time = (current_ticks - start_time) / 1000
        remaining_time = max(0, time_limit - elapsed_time)
        game_data['remaining_time'] = remaining_time
    else:
        # Nếu đang pause, giữ nguyên thời gian còn lại
        remaining_time = game_data.get('remaining_time', time_limit)

    # Kiểm tra thắng/thua
    if player_col == goal_col and player_row == goal_row:
        new_game_state = 'win_1p'
    elif remaining_time <= 0 and pause_start_time == 0: # Chỉ thua khi hết giờ và không đang pause
        new_game_state = 'lose_1p'

    # Không cần cập nhật game_data['game_state'] ở đây, trả về state mới
    return new_game_state


def draw_1p(screen, maze_surface, game_data, fonts):
    """Vẽ màn hình cho chế độ 1 Player."""
    layout = game_data.get('layout')
    if not layout or not maze_surface: return # Không có layout hoặc surface thì không vẽ

    cell_size, offset_x, offset_y = layout['cell_size'], layout['offset_x'], layout['offset_y']
    screen.fill(settings.WHITE) # Nền trắng cho màn hình game

    # Vẽ mê cung (đã được vẽ sẵn trên maze_surface)
    screen.blit(maze_surface, (offset_x, offset_y))

    # Vẽ đích và người chơi
    goal_col, goal_row = game_data.get('1p_goal_pos', (-1, -1))
    player_col, player_row = game_data['player_pos']
    utils.draw_goal(screen, goal_col, goal_row, cell_size, offset_x, offset_y, settings.YELLOW)
    utils.draw_entity(screen, player_col, player_row, cell_size, offset_x, offset_y, settings.PLAYER_COLOR)

    # Vẽ thông tin (Thời gian, Level)
    remaining_time = game_data.get('remaining_time', 0)
    minutes = int(remaining_time // 60)
    seconds = int(remaining_time % 60)
    timer_text = f"Time: {minutes:02}:{seconds:02}" # Format 2 chữ số
    current_level = game_data.get('current_level', 0)
    level_text = f"LV {current_level}"

    info_font = fonts.get('info') # Lấy font info
    if not info_font: info_font = pygame.font.Font(None, settings.FONT_SIZE_INFO  ) # Font mặc định

    utils.draw_text(screen, timer_text, info_font, settings.BLACK, 10, 10, center=False)
    utils.draw_text(screen, level_text, info_font, settings.BLACK, settings.WIDTH - 60, 10, center=False) # Dịch trái chút

    # Vẽ nút pause
    utils.draw_pause_button(screen)


def handle_input_paused_1p(event, game_data, fonts):
    """Xử lý input cho màn hình Pause 1 Player."""
    new_game_state = game_data['game_state'] # Giữ state hiện tại trừ khi nút được nhấn
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        # Lấy rect của các nút từ hàm vẽ (để kiểm tra va chạm)
        dummy_surface = pygame.Surface((1,1), pygame.SRCALPHA) # Dùng SRCALPHA vì menu pause có alpha
        buttons = utils.draw_pause_menu(dummy_surface, fonts)
        mouse_pos = event.pos

        if buttons['continue'].collidepoint(mouse_pos):
            if 'pause_start_time' in game_data and game_data['pause_start_time'] > 0:
                 # Tính thời gian đã pause để bù vào start_time khi tiếp tục
                 pause_duration = pygame.time.get_ticks() - game_data['pause_start_time']
                 game_data['start_time'] += pause_duration
                 game_data['pause_start_time'] = 0 # Reset thời gian bắt đầu pause = 0 để update timer chạy lại
            new_game_state = '1_player'
        elif buttons['replay'].collidepoint(mouse_pos):
             game_data['action'] = 'replay_1p' # Báo hiệu replay
             # Không cần đổi state ở đây, vòng lặp chính sẽ xử lý action
        elif buttons['exit'].collidepoint(mouse_pos):
             game_data['action'] = 'go_home' # Báo hiệu về home
             # Không cần đổi state ở đây

    return new_game_state # Trả về state hiện tại (pause) hoặc state mới nếu bấm Continue


def draw_paused_1p(screen, maze_surface, game_data, fonts):
    """Vẽ màn hình Pause 1 Player."""
    # Vẽ lại màn hình game phía dưới một cách hơi mờ đi (tùy chọn)
    if game_data.get('layout') and maze_surface:
        # Tạo một surface tạm để vẽ game rồi làm mờ
        temp_surface = screen.copy() # Sao chép màn hình hiện tại
        draw_1p(temp_surface, maze_surface, game_data, fonts) # Vẽ game lên surface tạm
        temp_surface.set_alpha(100) # Làm mờ (0-255)
        screen.blit(temp_surface, (0,0)) # Vẽ lại lên màn hình chính
    else:
        # Nếu không có game state để vẽ, tô nền tối
        screen.fill(settings.DARK_GRAY_BG)

    # Vẽ menu pause lên trên (menu này đã có lớp phủ riêng)
    utils.draw_pause_menu(screen, fonts)


def handle_input_end_1p(event, game_data, fonts):
    """Xử lý input cho màn hình Win/Lose 1 Player."""
    new_game_state = game_data['game_state']
    current_level = game_data.get('current_level', 1)
    is_win = (new_game_state == 'win_1p')

    primary_button_text = "Next Level" if is_win and current_level < settings.MAX_LEVEL else "Replay All" if is_win else "Replay"

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        # Lấy rect của nút từ hàm vẽ để kiểm tra va chạm
        dummy_surface = pygame.Surface((1,1)) # Surface tạm, không cần alpha
        # Xác định màu chữ cho thông báo dựa trên thắng/thua
        message_color = settings.BUTTON_TEXT_LIGHT if is_win else settings.TITLE_RED
        # Gọi draw_end_menu chỉ để lấy rect, không cần message thực tế
        buttons = utils.draw_end_menu(dummy_surface, "", message_color, primary_button_text, fonts)
        mouse_pos = event.pos

        if buttons['primary'].collidepoint(mouse_pos):
             if is_win:
                  if current_level < settings.MAX_LEVEL:
                      game_data['action'] = 'next_level_1p'
                  else: # Thắng level cuối
                      game_data['action'] = 'replay_all_1p' # Chơi lại từ đầu
             else: # Lose
                  game_data['action'] = 'replay_1p' # Chơi lại level hiện tại
             # State sẽ được cập nhật bởi vòng lặp chính dựa trên action
        elif buttons['exit'].collidepoint(mouse_pos):
             game_data['action'] = 'go_home'
             # State sẽ được cập nhật bởi vòng lặp chính dựa trên action

    return new_game_state # Giữ state win/lose cho đến khi action được xử lý


def draw_win_1p(screen, game_data, fonts):
    """Vẽ màn hình Win 1 Player theo theme mới."""
    current_level = game_data.get('current_level', 1)
    if current_level < settings.MAX_LEVEL:
        button_text = "Next Level"
        message = f"Level {current_level} Complete!"
    else:
        button_text = "Replay All" # Đổi thành Replay All khi thắng level cuối
        message = "YOU WIN!!!"
    # Sử dụng màu chữ sáng (BUTTON_TEXT_LIGHT) cho thông báo thắng
    utils.draw_end_menu(screen, message, settings.BUTTON_TEXT_LIGHT, button_text, fonts)


def draw_lose_1p(screen, game_data, fonts):
    """Vẽ màn hình Lose 1 Player theo theme mới."""
    # Sử dụng màu chữ đỏ (TITLE_RED) cho thông báo thua
    utils.draw_end_menu(screen, "GAME OVER", settings.TITLE_RED, "Replay", fonts)

# -------- Hết file: one_player.py --------