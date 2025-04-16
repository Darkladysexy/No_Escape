# -------- File: vs_bot.py --------
import pygame
import settings
import utils
from maze import Maze # Cần để khởi tạo lại maze khi replay

def handle_input_vs(event, game_data):
    """Xử lý input riêng cho chế độ VS Bot (chủ yếu là player)."""
    player_col, player_row = game_data['player_pos']
    current_maze = game_data['maze']
    new_game_state = game_data['game_state']

    if event.type == pygame.KEYDOWN:
        # Logic di chuyển player giống hệt 1P
        old_player_col, old_player_row = player_col, player_row
        moved = False
        current_cell = current_maze.get_cell(player_col, player_row) if current_maze else None
        if not current_cell: return player_col, player_row, new_game_state

        if event.key == pygame.K_UP or event.key == pygame.K_w:
            if not current_cell.walls['top']: player_row -= 1; moved = True
        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
            if not current_cell.walls['bottom']: player_row += 1; moved = True
        elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
            if not current_cell.walls['left']: player_col -= 1; moved = True
        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
            if not current_cell.walls['right']: player_col += 1; moved = True

        player_col = max(0, min(player_col, settings.MAZE_COLS - 1))
        player_row = max(0, min(player_row, settings.MAZE_ROWS - 1))

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
                 new_game_state = 'paused_vs' # Chuyển sang pause VS

    game_data['player_pos'] = (player_col, player_row)
    return new_game_state


def update_vs(game_data):
    """Cập nhật logic cho chế độ VS Bot (di chuyển bot, win/lose)."""
    player_col, player_row = game_data['player_pos']
    bot_col, bot_row = game_data['bot_pos']
    vs_player_goal = game_data['vs_player_goal_pos']
    bot_goal = game_data['bot_goal_pos']
    bot_path = game_data['bot_path']
    bot_move_timer = game_data['bot_move_timer']
    new_game_state = game_data['game_state']

    # Di chuyển Bot
    bot_move_timer += 1
    if bot_path and bot_move_timer >= settings.BOT_MOVE_DELAY:
        bot_move_timer = 0 # Reset timer
        current_bot_pos = (bot_col, bot_row)
        try:
            current_index_in_path = bot_path.index(current_bot_pos)
            if current_index_in_path + 1 < len(bot_path):
                bot_col, bot_row = bot_path[current_index_in_path + 1]
                game_data['bot_pos'] = (bot_col, bot_row) # Cập nhật vị trí bot
        except ValueError: # Bot lệch đường -> tìm lại
             new_path = utils.find_path_bfs(game_data['maze'], current_bot_pos, bot_goal)
             game_data['bot_path'] = new_path if new_path else [] # Cập nhật path mới

    game_data['bot_move_timer'] = bot_move_timer # Lưu lại timer

    # Kiểm tra thắng thua
    if (player_col, player_row) == vs_player_goal:
        new_game_state = 'player_wins_vs'
    elif (bot_col, bot_row) == bot_goal:
        new_game_state = 'bot_wins_vs'

    return new_game_state


def draw_vs(screen, maze_surface, game_data, fonts):
    """Vẽ màn hình cho chế độ VS Bot."""
    screen.fill(settings.WHITE)
    # Vẽ mê cung
    current_maze = game_data['maze']
    if current_maze:
        current_maze.draw(maze_surface, settings.BLACK, settings.WHITE, settings.WALL_THICKNESS)
        screen.blit(maze_surface, (settings.MAZE_OFFSET_X, settings.MAZE_OFFSET_Y))
    # Vẽ các đích
    vs_player_goal_col, vs_player_goal_row = game_data['vs_player_goal_pos']
    bot_goal_col, bot_goal_row = game_data['bot_goal_pos']
    utils.draw_goal(screen, vs_player_goal_col, vs_player_goal_row, settings.PLAYER_GOAL_COLOR)
    utils.draw_goal(screen, bot_goal_col, bot_goal_row, settings.BOT_GOAL_COLOR)
    # Vẽ player và bot
    player_col, player_row = game_data['player_pos']
    bot_col, bot_row = game_data['bot_pos']
    utils.draw_entity(screen, player_col, player_row, settings.PLAYER_COLOR)
    utils.draw_entity(screen, bot_col, bot_row, settings.BOT_COLOR)
    # Vẽ thông tin
    utils.draw_text(screen, "LV1", fonts['info'], settings.BLACK, settings.WIDTH - 50, 10, center=False)
    # Vẽ nút Pause
    utils.draw_pause_button(screen)


def handle_input_paused_vs(event, game_data):
    """Xử lý input cho màn hình Pause VS Bot."""
    new_game_state = game_data['game_state']
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        # Lấy rect nút từ hàm vẽ hoặc định nghĩa lại
        continue_button = pygame.Rect(settings.WIDTH // 2 - 100, settings.HEIGHT // 2 - 50, 200, 50)
        replay_button = pygame.Rect(settings.WIDTH // 2 - 100, settings.HEIGHT // 2 + 20, 200, 50)
        exit_button = pygame.Rect(settings.WIDTH // 2 - 100, settings.HEIGHT // 2 + 90, 200, 50)

        if continue_button.collidepoint(event.pos):
            new_game_state = 'vs_bot' # Tiếp tục chơi
        elif replay_button.collidepoint(event.pos):
             # Reset game data for VS Bot replay
             game_data['maze'] = Maze(settings.MAZE_COLS, settings.MAZE_ROWS, settings.CELL_SIZE)
             game_data['player_pos'] = game_data['maze'].entry_pos
             game_data['bot_pos'] = game_data['maze'].exit_pos
             game_data['vs_player_goal_pos'] = game_data['bot_pos']
             game_data['bot_goal_pos'] = game_data['player_pos']
             game_data['bot_path'] = utils.find_path_bfs(game_data['maze'], game_data['bot_pos'], game_data['bot_goal_pos'])
             game_data['bot_move_timer'] = 0
             if game_data['bot_path'] is None: new_game_state = 'home' # Lỗi -> về home
             else: new_game_state = 'vs_bot'
        elif exit_button.collidepoint(event.pos):
             new_game_state = 'home'
    return new_game_state

def draw_paused_vs(screen, maze_surface, game_data, fonts):
    """Vẽ màn hình Pause VS Bot."""
    # Vẽ lại màn hình game ở dưới
    draw_vs(screen, maze_surface, game_data, fonts)
    # Vẽ lớp phủ và menu
    utils.draw_pause_menu(screen, fonts)

def handle_input_end_vs(event, game_data):
    """Xử lý input cho màn hình kết thúc VS Bot."""
    new_game_state = game_data['game_state']
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        replay_button = pygame.Rect(settings.WIDTH // 2 - 100, settings.HEIGHT // 2 + 20, 200, 50)
        exit_button = pygame.Rect(settings.WIDTH // 2 - 100, settings.HEIGHT // 2 + 90, 200, 50)
        # Cả Replay và Exit đều về Home
        if replay_button.collidepoint(event.pos): new_game_state = 'home'
        elif exit_button.collidepoint(event.pos): new_game_state = 'home'
    return new_game_state

def draw_player_wins_vs(screen, game_data, fonts):
    """Vẽ màn hình Player thắng VS Bot."""
    utils.draw_end_menu(screen, "Player Wins!", settings.PLAYER_COLOR, fonts)

def draw_bot_wins_vs(screen, game_data, fonts):
    """Vẽ màn hình Bot thắng VS Bot."""
    utils.draw_end_menu(screen, "Bot Wins!", settings.BOT_COLOR, fonts)