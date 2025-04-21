# -------- File: noescape.py --------
import pygame
import sys
import settings
import utils
from maze import Maze
import one_player
import vs_bot

# --- Hàm Khởi tạo Level 1 Player ---
def start_level_1p(level, game_data):
    if level not in settings.LEVELS: print(f"Lỗi: Level {level} không tồn tại!"); return None, False
    level_info = settings.LEVELS[level]; cols, rows = level_info['cols'], level_info['rows']; time_limit = level_info['time_1p']
    cell_size, offset_x, offset_y, surf_w, surf_h = utils.calculate_maze_layout(cols, rows)
    game_data['current_level'] = level; game_data['maze'] = Maze(cols, rows, cell_size); game_data['player_pos'] = game_data['maze'].entry_pos
    game_data['1p_goal_pos'] = game_data['maze'].exit_pos; game_data['start_time'] = pygame.time.get_ticks(); game_data['time_limit'] = time_limit; game_data['remaining_time'] = time_limit
    game_data['layout'] = {'cell_size': cell_size, 'offset_x': offset_x, 'offset_y': offset_y, 'surf_w': surf_w, 'surf_h': surf_h}
    new_maze_surface = pygame.Surface((surf_w, surf_h)); print(f"Bắt đầu 1P Level {level}")
    new_maze_surface = pygame.Surface((surf_w, surf_h))
    game_data['maze'].draw(new_maze_surface, wall_color=(255, 255, 255), background_color=(0, 0, 0), wall_thickness=2)

    return new_maze_surface, True

# --- Hàm Khởi tạo Level VS Bot ---
def start_level_vs(level, game_data):
     if level not in settings.LEVELS: print(f"Lỗi: Level {level} không tồn tại!"); return None, False
     level_info = settings.LEVELS[level]; cols, rows = level_info['cols'], level_info['rows']; bot_delay = level_info['bot_delay_vs']
     cell_size, offset_x, offset_y, surf_w, surf_h = utils.calculate_maze_layout(cols, rows)
     game_data['current_level'] = level; game_data['maze'] = Maze(cols, rows, cell_size); game_data['player_pos'] = game_data['maze'].entry_pos
     game_data['bot_pos'] = game_data['maze'].exit_pos; game_data['vs_player_goal_pos'] = game_data['bot_pos']; game_data['bot_goal_pos'] = game_data['player_pos']
     game_data['bot_move_timer'] = 0; game_data['bot_delay'] = bot_delay
     game_data['layout'] = {'cell_size': cell_size, 'offset_x': offset_x, 'offset_y': offset_y, 'surf_w': surf_w, 'surf_h': surf_h}
     game_data['bot_path'] = utils.find_path_bfs(game_data['maze'], game_data['bot_pos'], game_data['bot_goal_pos'])
     if game_data['bot_path'] is None: print(f"Lỗi VS Bot Level {level}: Không tìm đường!"); return None, False
     new_maze_surface = pygame.Surface((surf_w, surf_h)); print(f"Bắt đầu VS Bot Level {level}")
     new_maze_surface = pygame.Surface((surf_w, surf_h))
     game_data['maze'].draw(new_maze_surface, wall_color=(255, 255, 255), background_color=(0, 0, 0), wall_thickness=2)

     return new_maze_surface, True

def run_game():
    pygame.init(); screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT)); pygame.display.set_caption("No Escape Maze Game"); clock = pygame.time.Clock()
    try: fonts = { 'large': pygame.font.SysFont(settings.FONT_NAME, settings.FONT_SIZE_LARGE, bold=True), 'button': pygame.font.SysFont(settings.FONT_NAME, settings.FONT_SIZE_BUTTON), 'info': pygame.font.SysFont(settings.FONT_NAME, settings.FONT_SIZE_INFO), 'pause': pygame.font.SysFont(settings.FONT_NAME, settings.FONT_SIZE_PAUSE, bold=True) }
    except: fonts = { 'large': pygame.font.Font(None, settings.FONT_SIZE_LARGE),'button': pygame.font.Font(None, settings.FONT_SIZE_BUTTON), 'info': pygame.font.Font(None, settings.FONT_SIZE_INFO), 'pause': pygame.font.Font(None, settings.FONT_SIZE_PAUSE)}
    maze_surface = None
    game_data = { 'game_state': 'home', 'maze': None, 'layout': None, 'current_level': 0, 'player_pos': (0, 0), '1p_goal_pos': (0, 0), 'start_time': 0, 'remaining_time': 0, 'pause_start_time': 0, 'time_limit': 0, 'bot_pos': (0, 0), 'bot_goal_pos': (0, 0), 'vs_player_goal_pos': (0, 0), 'bot_path': [], 'bot_move_timer': 0, 'bot_delay': 15, 'mouse_pos': (0, 0), 'click': False, 'action': None }

    running = True
    while running:
        game_data['mouse_pos'] = pygame.mouse.get_pos(); game_data['click'] = False; game_data['action'] = None
        next_game_state = game_data['game_state']

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            current_state = game_data['game_state']
            if current_state != 'home':
                 if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: game_data['click'] = True
                 # Gọi hàm xử lý input, truyền fonts
                 if current_state == '1_player': next_game_state = one_player.handle_input_1p(event, game_data)
                 elif current_state == 'paused_1p': next_game_state = one_player.handle_input_paused_1p(event, game_data, fonts)
                 elif current_state == 'win_1p' or current_state == 'lose_1p': next_game_state = one_player.handle_input_end_1p(event, game_data, fonts)
                 elif current_state == 'vs_bot': next_game_state = vs_bot.handle_input_vs(event, game_data)
                 elif current_state == 'paused_vs': next_game_state = vs_bot.handle_input_paused_vs(event, game_data, fonts)
                 elif current_state == 'player_wins_vs' or current_state == 'bot_wins_vs': next_game_state = vs_bot.handle_input_end_vs(event, game_data, fonts)
            elif current_state == 'home':
                 if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: game_data['click'] = True

        # --- Xử lý Action (Replay/Next Level/Replay All/Go Home) --- <<< CẬP NHẬT
        action = game_data.get('action')
        if action:
            current_level = game_data['current_level']
            if action == 'replay_1p': maze_surface, success = start_level_1p(current_level, game_data); next_game_state = '1_player' if success else 'home'
            elif action == 'next_level_1p': maze_surface, success = start_level_1p(current_level + 1, game_data); next_game_state = '1_player' if success else 'home'
            elif action == 'replay_all_1p': maze_surface, success = start_level_1p(1, game_data); next_game_state = '1_player' if success else 'home'
            elif action == 'replay_vs': maze_surface, success = start_level_vs(current_level, game_data); next_game_state = 'vs_bot' if success else 'home'
            elif action == 'next_level_vs': maze_surface, success = start_level_vs(current_level + 1, game_data); next_game_state = 'vs_bot' if success else 'home'
            elif action == 'replay_all_vs': maze_surface, success = start_level_vs(1, game_data); next_game_state = 'vs_bot' if success else 'home'
            elif action == 'go_home': # <<< XỬ LÝ GO_HOME
                 next_game_state = 'home'
                 game_data['click'] = False # Reset click để tránh lỗi kích hoạt nút home exit
            game_data['action'] = None # Reset action

        # --- Cập nhật trạng thái game ---
        game_data['game_state'] = next_game_state
        # --- Cập nhật logic game ---
        current_state = game_data['game_state']
        if current_state == '1_player': game_data['game_state'] = one_player.update_1p(game_data)
        elif current_state == 'vs_bot': game_data['game_state'] = vs_bot.update_vs(game_data)

        # --- Vẽ màn hình ---
        current_state = game_data['game_state']
        if current_state == 'home':
            screen.fill(settings.WHITE); utils.draw_text(screen, 'NO ESCAPE', fonts['large'], settings.RED, settings.WIDTH // 2, settings.HEIGHT // 4)
            button_1p_rect = pygame.Rect(settings.WIDTH // 2 - 100, settings.HEIGHT // 2 - 50, 200, 50); button_vs_bot_rect = pygame.Rect(settings.WIDTH // 2 - 100, settings.HEIGHT // 2 + 20, 200, 50); button_exit_rect = pygame.Rect(settings.WIDTH // 2 - 100, settings.HEIGHT // 2 + 90, 200, 50)
            pygame.draw.rect(screen, settings.GREEN, button_1p_rect); pygame.draw.rect(screen, settings.GREEN, button_vs_bot_rect); pygame.draw.rect(screen, settings.RED, button_exit_rect)
            utils.draw_text(screen, '1 Player', fonts['button'], settings.BLACK, button_1p_rect.centerx, button_1p_rect.centery); utils.draw_text(screen, 'VS Bot', fonts['button'], settings.BLACK, button_vs_bot_rect.centerx, button_vs_bot_rect.centery); utils.draw_text(screen, 'Exit', fonts['button'], settings.BLACK, button_exit_rect.centerx, button_exit_rect.centery)
            if game_data['click']: # Chỉ xử lý click home nếu click xảy ra ở frame này VÀ state là home
                if button_1p_rect.collidepoint(game_data['mouse_pos']): maze_surface, success = start_level_1p(1, game_data); game_data['game_state'] = '1_player' if success else 'home'
                elif button_vs_bot_rect.collidepoint(game_data['mouse_pos']): maze_surface, success = start_level_vs(1, game_data); game_data['game_state'] = 'vs_bot' if success else 'home'
                elif button_exit_rect.collidepoint(game_data['mouse_pos']): running = False
        # Gọi hàm vẽ tương ứng
        elif current_state == '1_player': one_player.draw_1p(screen, maze_surface, game_data, fonts)
        elif current_state == 'paused_1p': one_player.draw_paused_1p(screen, maze_surface, game_data, fonts)
        elif current_state == 'win_1p': one_player.draw_win_1p(screen, game_data, fonts)
        elif current_state == 'lose_1p': one_player.draw_lose_1p(screen, game_data, fonts)
        elif current_state == 'vs_bot': vs_bot.draw_vs(screen, maze_surface, game_data, fonts)
        elif current_state == 'paused_vs': vs_bot.draw_paused_vs(screen, maze_surface, game_data, fonts)
        elif current_state == 'player_wins_vs': vs_bot.draw_player_wins_vs(screen, game_data, fonts)
        elif current_state == 'bot_wins_vs': vs_bot.draw_bot_wins_vs(screen, game_data, fonts)

        pygame.display.flip(); clock.tick(settings.FPS)
    pygame.quit(); sys.exit()
if __name__ == '__main__': run_game()
# -------- Hết file: noescape.py --------