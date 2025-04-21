# -------- File: noescape.py --------
import pygame
import sys
import os # Thêm os và sys để xử lý đường dẫn tài nguyên
import settings
import utils
from maze import Maze
import one_player
import vs_bot

# --- Hàm Helper để lấy đường dẫn tài nguyên đúng cách ---
# Quan trọng khi đóng gói thành file EXE
def resource_path(relative_path):
    """ Lấy đường dẫn tuyệt đối đến tài nguyên, hoạt động cho dev và PyInstaller """
    try:
        # PyInstaller tạo thư mục tạm _MEIPASS và đặt tài nguyên ở đó khi chạy file EXE
        # getattr tránh lỗi nếu không có thuộc tính _MEIPASS (khi chạy từ source)
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    except Exception:
        # Fallback nếu có lỗi không mong muốn
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# --- Hàm Khởi tạo Level 1 Player ---
def start_level_1p(level, game_data):
    if level not in settings.LEVELS: print(f"Lỗi: Level {level} không tồn tại!"); return None, False
    level_info = settings.LEVELS[level]; cols, rows = level_info['cols'], level_info['rows']; time_limit = level_info['time_1p']
    cell_size, offset_x, offset_y, surf_w, surf_h = utils.calculate_maze_layout(cols, rows)
    game_data['current_level'] = level; game_data['maze'] = Maze(cols, rows, cell_size); game_data['player_pos'] = game_data['maze'].entry_pos
    game_data['1p_goal_pos'] = game_data['maze'].exit_pos; game_data['start_time'] = pygame.time.get_ticks(); game_data['time_limit'] = time_limit; game_data['remaining_time'] = time_limit
    game_data['layout'] = {'cell_size': cell_size, 'offset_x': offset_x, 'offset_y': offset_y, 'surf_w': surf_w, 'surf_h': surf_h}
    new_maze_surface = pygame.Surface((surf_w, surf_h)); print(f"Bắt đầu 1P Level {level}")
    game_data['maze'].draw(new_maze_surface, wall_color=settings.BLACK, background_color=settings.WHITE, wall_thickness=settings.WALL_THICKNESS)
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
     game_data['maze'].draw(new_maze_surface, wall_color=settings.BLACK, background_color=settings.WHITE, wall_thickness=settings.WALL_THICKNESS)
     return new_maze_surface, True


def run_game():
    pygame.init()
    # Khởi tạo mixer trước khi load âm thanh (nếu có)
    # pygame.mixer.init()
    screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
    pygame.display.set_caption("No Escape Maze Game")
    clock = pygame.time.Clock()

    # --- Fonts (Load từ file .ttf) ---
    fonts = {} # Khởi tạo dict rỗng
    try:
        # Xác định đường dẫn đến file font bằng hàm resource_path
        font_file_name = "Chiller.ttf" # Đảm bảo file này có trong thư mục dự án
        chiller_font_path = resource_path(font_file_name)

        # Load các kích thước font cần thiết từ file .ttf
        fonts['large'] = pygame.font.Font(chiller_font_path, settings.FONT_SIZE_LARGE + 50) # Font to cho Title
        fonts['button'] = pygame.font.Font(chiller_font_path, settings.FONT_SIZE_BUTTON + 5) # Font cho nút, tăng size chút
        fonts['pause_title'] = pygame.font.Font(chiller_font_path, settings.FONT_SIZE_PAUSE + 20) # Font riêng cho chữ "Paused" nếu muốn

        # Font info có thể vẫn dùng font hệ thống nếu muốn, hoặc dùng Chiller
        # fonts['info'] = pygame.font.SysFont(settings.FONT_NAME, settings.FONT_SIZE_INFO) # Giữ nguyên SysFont
        fonts['info'] = pygame.font.Font(chiller_font_path, settings.FONT_SIZE_INFO) # Hoặc dùng Chiller

        # Font cho các menu khác (có thể dùng large hoặc button)
        fonts['pause'] = fonts['pause_title'] # Dùng font pause_title cho menu pause
        print(f"Đã tải font: {font_file_name}")

    except Exception as e_font:
        print(f"Lỗi tải font file '{font_file_name}': {e_font}. Sử dụng font mặc định.")
        # Fallback về font mặc định của Pygame nếu load file lỗi
        fonts['large'] = pygame.font.Font(None, settings.FONT_SIZE_LARGE + 10)
        fonts['button'] = pygame.font.Font(None, settings.FONT_SIZE_BUTTON)
        fonts['info'] = pygame.font.Font(None, settings.FONT_SIZE_INFO)
        fonts['pause'] = pygame.font.Font(None, settings.FONT_SIZE_PAUSE)
        fonts['pause_title'] = fonts['pause']


    maze_surface = None # Surface để vẽ mê cung trong game
    game_data = {
        'game_state': 'home', 'maze': None, 'layout': None, 'current_level': 0,
        'player_pos': (0, 0), '1p_goal_pos': (0, 0), 'start_time': 0, 'remaining_time': 0,
        'pause_start_time': 0, 'time_limit': 0, 'bot_pos': (0, 0), 'bot_goal_pos': (0, 0),
        'vs_player_goal_pos': (0, 0), 'bot_path': [], 'bot_move_timer': 0, 'bot_delay': 15,
        'mouse_pos': (0, 0), 'click': False, 'action': None
    }

    # --- Load và Scale Ảnh Nền Home ---
    home_bg_image = None
    try:
        # Sử dụng tên file mới và hàm resource_path
        image_file_name = "BACKGR.JPG"
        image_path = resource_path(image_file_name) # Lấy đường dẫn đúng
        if os.path.exists(image_path): # Kiểm tra lại sự tồn tại (dù resource_path thường xử lý)
            home_bg_image = pygame.image.load(image_path).convert()
            home_bg_image = pygame.transform.scale(home_bg_image, (settings.WIDTH, settings.HEIGHT))
            print(f"Đã tải ảnh nền: {image_file_name}")
        else:
            print(f"Lỗi: Không tìm thấy file ảnh nền tại '{image_path}'")
    except Exception as e:
        print(f"Lỗi khi load ảnh nền: {e}")

    running = True
    while running:
        game_data['mouse_pos'] = pygame.mouse.get_pos()
        game_data['click'] = False
        current_game_state = game_data['game_state'] # Lưu state đầu vòng lặp
        next_game_state = current_game_state # Mặc định không đổi state

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Xử lý click chuột chung
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                 game_data['click'] = True # Đặt là true, các hàm xử lý input sẽ dùng nó
                 # Xử lý nút Pause trong màn hình chơi game
                 if current_game_state == '1_player':
                     if settings.PAUSE_BUTTON_RECT.collidepoint(event.pos):
                         game_data['pause_start_time'] = pygame.time.get_ticks()
                         next_game_state = 'paused_1p'
                         game_data['click'] = False # Đã xử lý click này
                 elif current_game_state == 'vs_bot':
                      if settings.PAUSE_BUTTON_RECT.collidepoint(event.pos):
                          next_game_state = 'paused_vs'
                          game_data['click'] = False # Đã xử lý click này

            # Gọi hàm xử lý input tương ứng với state hiện tại
            if current_game_state == '1_player':
                # Chỉ xử lý KEYDOWN (di chuyển), MOUSEBUTTONDOWN cho nút Pause đã xử lý ở trên
                if event.type == pygame.KEYDOWN:
                    one_player.handle_input_1p(event, game_data)
            elif current_game_state == 'paused_1p':
                 if game_data['click']: # Chỉ xử lý click nếu nó được đặt
                      next_game_state = one_player.handle_input_paused_1p(event, game_data, fonts)
            elif current_game_state in ['win_1p', 'lose_1p']:
                 if game_data['click']:
                      next_game_state = one_player.handle_input_end_1p(event, game_data, fonts)
            elif current_game_state == 'vs_bot':
                 if event.type == pygame.KEYDOWN:
                      vs_bot.handle_input_vs(event, game_data)
            elif current_game_state == 'paused_vs':
                 if game_data['click']:
                      next_game_state = vs_bot.handle_input_paused_vs(event, game_data, fonts)
            elif current_game_state in ['player_wins_vs', 'bot_wins_vs']:
                  if game_data['click']:
                       next_game_state = vs_bot.handle_input_end_vs(event, game_data, fonts)
            elif current_game_state == 'home':
                 # Xử lý click riêng cho nút home sẽ nằm trong phần vẽ home
                 pass # Không cần xử lý event đặc biệt ở đây nữa


        # --- Xử lý Action (Replay/Next Level/Replay All/Go Home) ---
        # Action được đặt bởi các hàm handle_input của màn hình Pause/End
        action = game_data.get('action')
        if action:
            current_level = game_data['current_level']
            if action == 'replay_1p':
                maze_surface, success = start_level_1p(current_level, game_data)
                next_game_state = '1_player' if success else 'home'
            elif action == 'next_level_1p':
                maze_surface, success = start_level_1p(current_level + 1, game_data)
                next_game_state = '1_player' if success else 'home'
            elif action == 'replay_all_1p':
                maze_surface, success = start_level_1p(1, game_data)
                next_game_state = '1_player' if success else 'home'
            elif action == 'replay_vs':
                maze_surface, success = start_level_vs(current_level, game_data)
                next_game_state = 'vs_bot' if success else 'home'
            elif action == 'next_level_vs':
                maze_surface, success = start_level_vs(current_level + 1, game_data)
                next_game_state = 'vs_bot' if success else 'home'
            elif action == 'replay_all_vs':
                maze_surface, success = start_level_vs(1, game_data)
                next_game_state = 'vs_bot' if success else 'home'
            elif action == 'go_home':
                 next_game_state = 'home'
                 game_data['click'] = False # Reset click để tránh lỗi kích hoạt nút home exit ngay
            game_data['action'] = None # Reset action sau khi xử lý

        # --- Cập nhật trạng thái game ---
        # Cập nhật state nếu có sự thay đổi từ event hoặc action
        if next_game_state != game_data['game_state']:
             game_data['game_state'] = next_game_state


        # --- Cập nhật logic game (Timer, Win/Lose, Bot movement) ---
        current_state_for_update = game_data['game_state'] # Lấy state *sau* khi xử lý input/action
        logic_state_change = None
        if current_state_for_update == '1_player':
             logic_state_change = one_player.update_1p(game_data)
        elif current_state_for_update == 'vs_bot':
             logic_state_change = vs_bot.update_vs(game_data)

        # Cập nhật state nếu logic game yêu cầu (ví dụ: hết giờ, chạm đích)
        if logic_state_change and logic_state_change != game_data['game_state']:
            game_data['game_state'] = logic_state_change


        # --- Vẽ màn hình ---
        current_state_for_draw = game_data['game_state'] # Lấy state cuối cùng để vẽ
        if current_state_for_draw == 'home':
            # Vẽ ảnh nền hoặc màu nền dự phòng
            if home_bg_image:
                screen.blit(home_bg_image, (0, 0))
            else:
                screen.fill(settings.DARK_GRAY_BG)

            # Vẽ tiêu đề với màu và font mới (load từ file)
            utils.draw_text(screen, 'NO ESCAPE', fonts['large'], settings.TITLE_RED,
                            settings.WIDTH // 2, settings.HEIGHT // 4 + 10)

            # Định nghĩa Rect cho các nút
            button_width = 220
            button_height = 55
            button_x = settings.WIDTH // 2 - button_width // 2
            button_1p_rect = pygame.Rect(button_x, settings.HEIGHT // 2 - 60, button_width, button_height)
            button_vs_bot_rect = pygame.Rect(button_x, settings.HEIGHT // 2 + 25, button_width, button_height)
            button_exit_rect = pygame.Rect(button_x, settings.HEIGHT // 2 + 110, button_width, button_height)

            # Vẽ Nút với nền bán trong suốt
            s_1p = pygame.Surface((button_1p_rect.width, button_1p_rect.height), pygame.SRCALPHA)
            s_1p.fill(settings.BUTTON_BG_DARK)
            screen.blit(s_1p, button_1p_rect.topleft)

            s_vs = pygame.Surface((button_vs_bot_rect.width, button_vs_bot_rect.height), pygame.SRCALPHA)
            s_vs.fill(settings.BUTTON_BG_DARK)
            screen.blit(s_vs, button_vs_bot_rect.topleft)

            s_exit = pygame.Surface((button_exit_rect.width, button_exit_rect.height), pygame.SRCALPHA)
            s_exit.fill(settings.EXIT_BUTTON_BG_DARK)
            screen.blit(s_exit, button_exit_rect.topleft)

            # Vẽ viền nút
            pygame.draw.rect(screen, settings.BUTTON_BORDER_LIGHT, button_1p_rect, 2)
            pygame.draw.rect(screen, settings.BUTTON_BORDER_LIGHT, button_vs_bot_rect, 2)
            pygame.draw.rect(screen, settings.BUTTON_BORDER_LIGHT, button_exit_rect, 2)

            # Vẽ chữ trên nút với font mới (load từ file)
            utils.draw_text(screen, '1 PLAYER', fonts['button'], settings.BUTTON_TEXT_LIGHT,
                            button_1p_rect.centerx, button_1p_rect.centery)
            utils.draw_text(screen, 'VS BOT', fonts['button'], settings.BUTTON_TEXT_LIGHT,
                            button_vs_bot_rect.centerx, button_vs_bot_rect.centery)
            utils.draw_text(screen, 'EXIT', fonts['button'], settings.BUTTON_TEXT_LIGHT,
                            button_exit_rect.centerx, button_exit_rect.centery)

            # Xử lý click nút home
            if game_data['click']: # Chỉ xử lý nếu có click ở frame này
                if button_1p_rect.collidepoint(game_data['mouse_pos']):
                    maze_surface, success = start_level_1p(1, game_data)
                    game_data['game_state'] = '1_player' if success else 'home'
                    game_data['click'] = False # Đã xử lý click
                elif button_vs_bot_rect.collidepoint(game_data['mouse_pos']):
                    maze_surface, success = start_level_vs(1, game_data)
                    game_data['game_state'] = 'vs_bot' if success else 'home'
                    game_data['click'] = False # Đã xử lý click
                elif button_exit_rect.collidepoint(game_data['mouse_pos']):
                    running = False # Thoát game
                    game_data['click'] = False # Đã xử lý click

        # --- Gọi hàm vẽ cho các state khác ---
        elif current_state_for_draw == '1_player':
            if maze_surface: one_player.draw_1p(screen, maze_surface, game_data, fonts)
        elif current_state_for_draw == 'paused_1p':
             if maze_surface: one_player.draw_paused_1p(screen, maze_surface, game_data, fonts)
        elif current_state_for_draw == 'win_1p':
             one_player.draw_win_1p(screen, game_data, fonts)
        elif current_state_for_draw == 'lose_1p':
             one_player.draw_lose_1p(screen, game_data, fonts)
        elif current_state_for_draw == 'vs_bot':
             if maze_surface: vs_bot.draw_vs(screen, maze_surface, game_data, fonts)
        elif current_state_for_draw == 'paused_vs':
             if maze_surface: vs_bot.draw_paused_vs(screen, maze_surface, game_data, fonts)
        elif current_state_for_draw == 'player_wins_vs':
             vs_bot.draw_player_wins_vs(screen, game_data, fonts)
        elif current_state_for_draw == 'bot_wins_vs':
             vs_bot.draw_bot_wins_vs(screen, game_data, fonts)


        pygame.display.flip()
        clock.tick(settings.FPS)

    pygame.quit()
    sys.exit()

# --- Chạy game ---
if __name__ == '__main__':
    run_game()

# -------- Hết file: noescape.py --------