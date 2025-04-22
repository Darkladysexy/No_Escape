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
    # Đảm bảo trả về đường dẫn chuẩn hóa (dùng nếu cần)
    # return os.path.normpath(os.path.join(base_path, relative_path))
    return os.path.join(base_path, relative_path)


# --- Hàm Khởi tạo Level 1 Player ---
def start_level_1p(level, game_data):
    if level not in settings.LEVELS: print(f"Lỗi: Level {level} không tồn tại!"); return None, False
    level_info = settings.LEVELS[level]; cols, rows = level_info['cols'], level_info['rows']; time_limit = level_info['time_1p']
    cell_size, offset_x, offset_y, surf_w, surf_h = utils.calculate_maze_layout(cols, rows)
    if cell_size <= 0: # Kiểm tra cell_size hợp lệ
         print(f"Lỗi: Kích thước ô tính toán không hợp lệ cho Level {level} ({cols}x{rows})")
         return None, False
    game_data['current_level'] = level; game_data['maze'] = Maze(cols, rows, cell_size); game_data['player_pos'] = game_data['maze'].entry_pos
    game_data['1p_goal_pos'] = game_data['maze'].exit_pos; game_data['start_time'] = pygame.time.get_ticks(); game_data['time_limit'] = time_limit; game_data['remaining_time'] = time_limit
    game_data['pause_start_time'] = 0 # Đảm bảo reset khi bắt đầu level
    game_data['layout'] = {'cell_size': cell_size, 'offset_x': offset_x, 'offset_y': offset_y, 'surf_w': surf_w, 'surf_h': surf_h}
    new_maze_surface = pygame.Surface((surf_w, surf_h)); print(f"Bắt đầu 1P Level {level}")
    try:
         game_data['maze'].draw(new_maze_surface, wall_color=settings.BLACK, background_color=settings.WHITE, wall_thickness=settings.WALL_THICKNESS)
    except Exception as e_draw:
         print(f"Lỗi vẽ mê cung khởi tạo level 1P: {e_draw}")
         return None, False
    return new_maze_surface, True

# --- Hàm Khởi tạo Level VS Bot ---
def start_level_vs(level, game_data):
     if level not in settings.LEVELS: print(f"Lỗi: Level {level} không tồn tại!"); return None, False
     level_info = settings.LEVELS[level]; cols, rows = level_info['cols'], level_info['rows']; bot_delay = level_info['bot_delay_vs']
     cell_size, offset_x, offset_y, surf_w, surf_h = utils.calculate_maze_layout(cols, rows)
     if cell_size <= 0:
         print(f"Lỗi: Kích thước ô tính toán không hợp lệ cho Level {level} ({cols}x{rows})")
         return None, False
     game_data['current_level'] = level; game_data['maze'] = Maze(cols, rows, cell_size); game_data['player_pos'] = game_data['maze'].entry_pos
     game_data['bot_pos'] = game_data['maze'].exit_pos; game_data['vs_player_goal_pos'] = game_data['bot_pos']; game_data['bot_goal_pos'] = game_data['player_pos']
     game_data['bot_move_timer'] = 0; game_data['bot_delay'] = bot_delay
     game_data['layout'] = {'cell_size': cell_size, 'offset_x': offset_x, 'offset_y': offset_y, 'surf_w': surf_w, 'surf_h': surf_h}
     # Tìm đường đi cho bot NGAY KHI khởi tạo level
     game_data['bot_path'] = utils.find_path_bfs(game_data['maze'], game_data['bot_pos'], game_data['bot_goal_pos'])
     if game_data['bot_path'] is None:
         print(f"Lỗi VS Bot Level {level}: Không tìm được đường đi ban đầu cho bot!");
         # Có thể xử lý khác ở đây, ví dụ không cho bắt đầu level hoặc bot đứng yên
         game_data['bot_path'] = [] # Cho bot path rỗng để không bị lỗi khi truy cập
         # return None, False # Hoặc không cho bắt đầu level nếu không có đường
     new_maze_surface = pygame.Surface((surf_w, surf_h)); print(f"Bắt đầu VS Bot Level {level}")
     try:
         game_data['maze'].draw(new_maze_surface, wall_color=settings.BLACK, background_color=settings.WHITE, wall_thickness=settings.WALL_THICKNESS)
     except Exception as e_draw:
         print(f"Lỗi vẽ mê cung khởi tạo level VS: {e_draw}")
         return None, False
     return new_maze_surface, True


def run_game():
    pygame.init()
    # Khởi tạo mixer trước (nếu có dùng âm thanh)
    # try:
    #     pygame.mixer.init()
    # except pygame.error as e_mixer:
    #     print(f"Lỗi khởi tạo mixer: {e_mixer}. Âm thanh có thể không hoạt động.")

    screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
    pygame.display.set_caption("No Escape Maze Game")
    clock = pygame.time.Clock()

    # --- Fonts (Load từ file .ttf) ---
    fonts = {}
    try:
        # Đảm bảo file Chiller.ttf nằm cùng thư mục hoặc cung cấp đường dẫn đúng
        font_file_name = "Chiller.ttf"
        chiller_font_path = resource_path(font_file_name)

        # Load các kích thước font
        fonts['large'] = pygame.font.Font(chiller_font_path, settings.FONT_SIZE_LARGE + 50)
        fonts['button'] = pygame.font.Font(chiller_font_path, settings.FONT_SIZE_BUTTON + 5)
        fonts['pause_title'] = pygame.font.Font(chiller_font_path, settings.FONT_SIZE_PAUSE + 20)
        # Thống nhất dùng font Chiller cho Info nếu được
        fonts['info'] = pygame.font.Font(chiller_font_path, settings.FONT_SIZE_INFO )
        fonts['pause'] = fonts['pause_title'] # Dùng chung font cho tiêu đề pause

        print(f"Đã tải font: {font_file_name}")

    except Exception as e_font:
        print(f"Lỗi tải font file '{font_file_name}': {e_font}. Sử dụng font mặc định.")
        # Fallback về font mặc định của Pygame
        default_button_size = settings.FONT_SIZE_BUTTON
        default_large_size = settings.FONT_SIZE_LARGE + 10
        default_info_size = settings.FONT_SIZE_INFO
        default_pause_size = settings.FONT_SIZE_PAUSE
        try:
             fonts['large'] = pygame.font.Font(None, default_large_size)
             fonts['button'] = pygame.font.Font(None, default_button_size)
             fonts['info'] = pygame.font.Font(None, default_info_size)
             fonts['pause'] = pygame.font.Font(None, default_pause_size)
             fonts['pause_title'] = fonts['pause'] # Dùng chung font mặc định
        except Exception as e_fallback_font:
             print(f"Lỗi nghiêm trọng khi tải font mặc định: {e_fallback_font}")
             # Nếu cả font mặc định cũng lỗi, thoát game có thể là lựa chọn tốt nhất
             pygame.quit()
             sys.exit("Không thể tải font chữ cần thiết.")


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
        image_file_name = "BACKGR.JPG" # Sử dụng tên file mới
        image_path = resource_path(image_file_name)
        # Không cần kiểm tra os.path.exists nữa vì resource_path sẽ báo lỗi nếu không tìm thấy trong quá trình build EXE
        # hoặc trả về đường dẫn đúng khi chạy từ source
        home_bg_image = pygame.image.load(image_path).convert()
        home_bg_image = pygame.transform.scale(home_bg_image, (settings.WIDTH, settings.HEIGHT))
        print(f"Đã tải ảnh nền: {image_file_name}")
    except Exception as e:
        print(f"Lỗi khi load ảnh nền '{image_file_name}': {e}")
        print("Game sẽ chạy với nền màu tối.")


    running = True
    while running:
        game_data['mouse_pos'] = pygame.mouse.get_pos()
        game_data['click'] = False # Reset click mỗi frame
        current_game_state = game_data['game_state']
        next_game_state = current_game_state

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                 game_data['click'] = True
                 # Xử lý nút Pause khi đang chơi
                 if current_game_state == '1_player':
                     if settings.PAUSE_BUTTON_RECT.collidepoint(event.pos):
                         game_data['pause_start_time'] = pygame.time.get_ticks() # Ghi lại thời điểm pause
                         next_game_state = 'paused_1p'
                         game_data['click'] = False # Click này đã được xử lý
                 elif current_game_state == 'vs_bot':
                      if settings.PAUSE_BUTTON_RECT.collidepoint(event.pos):
                          # Chế độ VS Bot không cần quản lý pause_start_time phức tạp
                          next_game_state = 'paused_vs'
                          game_data['click'] = False # Click này đã được xử lý

            # --- Phân phối Input dựa trên State ---
            # Chỉ gọi hàm xử lý input tương ứng nếu có sự kiện liên quan
            if current_game_state == '1_player':
                if event.type == pygame.KEYDOWN: # Chỉ xử lý di chuyển
                    one_player.handle_input_1p(event, game_data)
            elif current_game_state == 'paused_1p':
                 if game_data['click']: # Chỉ gọi khi có click chuột
                      next_game_state_from_handler = one_player.handle_input_paused_1p(event, game_data, fonts)
                      # Chỉ cập nhật next_game_state nếu handler thực sự thay đổi nó
                      if next_game_state_from_handler != current_game_state:
                          next_game_state = next_game_state_from_handler
            elif current_game_state in ['win_1p', 'lose_1p']:
                 if game_data['click']:
                      # Hàm handle_input_end_* không đổi state, chỉ đặt action
                      one_player.handle_input_end_1p(event, game_data, fonts)
            elif current_game_state == 'vs_bot':
                 if event.type == pygame.KEYDOWN: # Chỉ xử lý di chuyển
                      vs_bot.handle_input_vs(event, game_data)
            elif current_game_state == 'paused_vs':
                 if game_data['click']:
                      next_game_state_from_handler = vs_bot.handle_input_paused_vs(event, game_data, fonts)
                      if next_game_state_from_handler != current_game_state:
                           next_game_state = next_game_state_from_handler
            elif current_game_state in ['player_wins_vs', 'bot_wins_vs']:
                  if game_data['click']:
                       # Hàm handle_input_end_* không đổi state, chỉ đặt action
                       vs_bot.handle_input_end_vs(event, game_data, fonts)
            elif current_game_state == 'home':
                 # Click nút home xử lý trong phần vẽ
                 pass

        # --- Xử lý Action ---
        action = game_data.get('action')
        if action:
            current_level = game_data['current_level']
            # Đặt lại maze_surface về None trước khi bắt đầu level mới/replay
            maze_surface = None
            success = False # Reset success flag

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
                 game_data['click'] = False # Reset click phòng trường hợp quay về home ngay

            game_data['action'] = None # Luôn reset action sau khi xử lý

        # --- Cập nhật trạng thái game ---
        if next_game_state != game_data['game_state']:
             game_data['game_state'] = next_game_state

        # --- Cập nhật logic game ---
        current_state_for_update = game_data['game_state']
        logic_state_change = None
        if current_state_for_update == '1_player':
             logic_state_change = one_player.update_1p(game_data)
        elif current_state_for_update == 'vs_bot':
             logic_state_change = vs_bot.update_vs(game_data)

        # Cập nhật state nếu logic game yêu cầu
        if logic_state_change and logic_state_change != game_data['game_state']:
            game_data['game_state'] = logic_state_change

        # --- Vẽ màn hình ---
        current_state_for_draw = game_data['game_state']
        if current_state_for_draw == 'home':
            # Vẽ ảnh nền hoặc màu nền dự phòng
            if home_bg_image:
                screen.blit(home_bg_image, (0, 0))
            else:
                screen.fill(settings.DARK_GRAY_BG)

            # Vẽ tiêu đề
            utils.draw_text(screen, 'NO ESCAPE', fonts['large'], settings.TITLE_RED,
                            settings.WIDTH // 2, settings.HEIGHT // 4 + 10)

            # Định nghĩa Rect và vẽ nút
            button_width = 220
            button_height = 55
            button_x = settings.WIDTH // 2 - button_width // 2
            button_1p_rect = pygame.Rect(button_x, settings.HEIGHT // 2 - 60, button_width, button_height)
            button_vs_bot_rect = pygame.Rect(button_x, settings.HEIGHT // 2 + 25, button_width, button_height)
            button_exit_rect = pygame.Rect(button_x, settings.HEIGHT // 2 + 110, button_width, button_height)

            # Vẽ nền bán trong suốt và viền nút (Tách ra để dễ đọc)
            button_list = [
                (button_1p_rect, settings.BUTTON_BG_DARK, '1 PLAYER'),
                (button_vs_bot_rect, settings.BUTTON_BG_DARK, 'VS BOT'),
                (button_exit_rect, settings.EXIT_BUTTON_BG_DARK, 'EXIT')
            ]
            for rect, bg_color, text in button_list:
                 try:
                     s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                     s.fill(bg_color)
                     screen.blit(s, rect.topleft)
                     pygame.draw.rect(screen, settings.BUTTON_BORDER_LIGHT, rect, 2)
                     utils.draw_text(screen, text, fonts['button'], settings.BUTTON_TEXT_LIGHT, rect.centerx, rect.centery)
                 except Exception as e_draw_button:
                     print(f"Lỗi vẽ nút '{text}': {e_draw_button}")

            # --- Vẽ HƯỚNG DẪN CHƠI ---
            instruction_text = "Di chuyen: WASD"
            instruction_font = fonts.get('button', fonts.get('info')) # Ưu tiên font button
            if not instruction_font: instruction_font = pygame.font.Font(None, 24)

            instruction_y = button_exit_rect.bottom + 50
            if instruction_y > settings.HEIGHT - 30 : instruction_y = settings.HEIGHT - 30

            utils.draw_text(screen, instruction_text, instruction_font, settings.BUTTON_TEXT_LIGHT,
                            settings.WIDTH // 2, instruction_y, center=True)
            # --- KẾT THÚC PHẦN HƯỚNG DẪN ---

            # Xử lý click nút home (chỉ khi có click ở frame này)
            if game_data['click']:
                mouse_pos = game_data['mouse_pos']
                clicked_on_button = False
                if button_1p_rect.collidepoint(mouse_pos):
                    maze_surface, success = start_level_1p(1, game_data)
                    game_data['game_state'] = '1_player' if success else 'home'
                    clicked_on_button = True
                elif button_vs_bot_rect.collidepoint(mouse_pos):
                    maze_surface, success = start_level_vs(1, game_data)
                    game_data['game_state'] = 'vs_bot' if success else 'home'
                    clicked_on_button = True
                elif button_exit_rect.collidepoint(mouse_pos):
                    running = False # Thoát game
                    clicked_on_button = True

                if clicked_on_button:
                    game_data['click'] = False # Reset click sau khi xử lý

        # --- Gọi hàm vẽ cho các state khác ---
        elif current_state_for_draw == '1_player':
            if maze_surface: one_player.draw_1p(screen, maze_surface, game_data, fonts)
            else: screen.fill(settings.BLACK); utils.draw_text(screen, "Loading Level...", fonts['button'], settings.WHITE, settings.WIDTH//2, settings.HEIGHT//2) # Màn hình chờ
        elif current_state_for_draw == 'paused_1p':
             # Hàm draw_paused_1p nên tự xử lý việc vẽ nền game mờ + menu
             one_player.draw_paused_1p(screen, maze_surface, game_data, fonts)
        elif current_state_for_draw == 'win_1p':
             one_player.draw_win_1p(screen, game_data, fonts)
        elif current_state_for_draw == 'lose_1p':
             one_player.draw_lose_1p(screen, game_data, fonts)
        elif current_state_for_draw == 'vs_bot':
             if maze_surface: vs_bot.draw_vs(screen, maze_surface, game_data, fonts)
             else: screen.fill(settings.BLACK); utils.draw_text(screen, "Loading Level...", fonts['button'], settings.WHITE, settings.WIDTH//2, settings.HEIGHT//2) # Màn hình chờ
        elif current_state_for_draw == 'paused_vs':
             vs_bot.draw_paused_vs(screen, maze_surface, game_data, fonts)
        elif current_state_for_draw == 'player_wins_vs':
             vs_bot.draw_player_wins_vs(screen, game_data, fonts)
        elif current_state_for_draw == 'bot_wins_vs':
             vs_bot.draw_bot_wins_vs(screen, game_data, fonts)
        else:
             # Fallback: Vẽ nền đen nếu state không xác định
             screen.fill(settings.BLACK)
             utils.draw_text(screen, f"Unknown State: {current_state_for_draw}", fonts['info'], settings.RED, 10, 10, center=False)

        pygame.display.flip()
        clock.tick(settings.FPS)

    pygame.quit()
    sys.exit()

# --- Chạy game ---
if __name__ == '__main__':
    # Thêm try-except ở đây để bắt lỗi tổng quát khi chạy game
    try:
        run_game()
    except Exception as main_exception:
        print("\n" + "="*20 + " LỖI TỔNG QUÁT KHI CHẠY GAME " + "="*20)
        print(f"Lỗi: {main_exception}")
        import traceback
        traceback.print_exc() # In chi tiết lỗi
        # Giữ cửa sổ console mở để xem lỗi (nếu chạy từ file .py)
        input("\nNhấn Enter để thoát...")
        pygame.quit()
        sys.exit(1) # Thoát với mã lỗi

# -------- Hết file: noescape.py --------