# -------- File: noescape.py --------
import pygame
import sys
# Import các module đã tạo
import settings
import utils
from maze import Maze
import one_player
import vs_bot

def run_game():
    # --- Khởi tạo Pygame và các thành phần cơ bản ---
    pygame.init()
    screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
    pygame.display.set_caption("No Escape Maze Game")
    clock = pygame.time.Clock()

    # --- Tải Fonts ---
    fonts = {
        'large': pygame.font.Font(None, settings.FONT_SIZE_LARGE) if settings.FONT_NAME is None else pygame.font.SysFont(settings.FONT_NAME, settings.FONT_SIZE_LARGE),
        'button': pygame.font.Font(None, settings.FONT_SIZE_BUTTON) if settings.FONT_NAME is None else pygame.font.SysFont(settings.FONT_NAME, settings.FONT_SIZE_BUTTON),
        'info': pygame.font.Font(None, settings.FONT_SIZE_INFO) if settings.FONT_NAME is None else pygame.font.SysFont(settings.FONT_NAME, settings.FONT_SIZE_INFO),
        'pause': pygame.font.Font(None, settings.FONT_SIZE_PAUSE) if settings.FONT_NAME is None else pygame.font.SysFont(settings.FONT_NAME, settings.FONT_SIZE_PAUSE)
    }
    # Xử lý lỗi font nếu cần thiết (ví dụ, nếu sysfont không tồn tại)
    # (Trong ví dụ này bỏ qua để đơn giản)

    # --- Surface để vẽ mê cung ---
    maze_surface = pygame.Surface((settings.MAZE_SURFACE_WIDTH, settings.MAZE_SURFACE_HEIGHT))

    # --- Dữ liệu Game (Quản lý trạng thái) ---
    game_data = {
        'game_state': 'home', # Trạng thái ban đầu
        'maze': None,
        # Dữ liệu 1 Player
        'player_pos': (0, 0),
        '1p_goal_pos': (0, 0),
        'start_time': 0,
        'remaining_time': settings.TIME_LIMIT_1P,
        'pause_start_time': 0,
        # Dữ liệu VS Bot
        'bot_pos': (0, 0),
        'bot_goal_pos': (0, 0),
        'vs_player_goal_pos': (0, 0),
        'bot_path': [],
        'bot_move_timer': 0,
        # Dữ liệu click chuột (sẽ được cập nhật mỗi frame)
        'mouse_pos': (0, 0),
        'click': False,
    }

    # --- Vòng lặp Game chính ---
    running = True
    while running:
        # --- Xử lý sự kiện ---
        game_data['mouse_pos'] = pygame.mouse.get_pos()
        game_data['click'] = False # Reset click mỗi frame

        # Biến tạm lưu trạng thái mới trả về từ các hàm xử lý input
        next_game_state = game_data['game_state']

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Gọi hàm xử lý input tương ứng với trạng thái hiện tại
            current_state = game_data['game_state']
            if current_state == '1_player':
                 next_game_state = one_player.handle_input_1p(event, game_data)
            elif current_state == 'paused_1p':
                 next_game_state = one_player.handle_input_paused_1p(event, game_data)
            elif current_state == 'win_1p' or current_state == 'lose_1p':
                 next_game_state = one_player.handle_input_end_1p(event, game_data)
            elif current_state == 'vs_bot':
                 next_game_state = vs_bot.handle_input_vs(event, game_data)
            elif current_state == 'paused_vs':
                 next_game_state = vs_bot.handle_input_paused_vs(event, game_data)
            elif current_state == 'player_wins_vs' or current_state == 'bot_wins_vs':
                 next_game_state = vs_bot.handle_input_end_vs(event, game_data)
            elif current_state == 'home':
                 # Xử lý click nút Home trực tiếp ở đây
                 if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                     game_data['click'] = True # Đánh dấu có click cho xử lý nút home
                 # (Thoát game được xử lý riêng ở cuối vòng lặp home)


        # --- Cập nhật trạng thái game ---
        game_data['game_state'] = next_game_state # Cập nhật trạng thái mới nhất

        # Gọi hàm cập nhật logic tương ứng
        current_state = game_data['game_state'] # Lấy lại trạng thái (có thể đã thay đổi)
        if current_state == '1_player':
            game_data['game_state'] = one_player.update_1p(game_data)
        elif current_state == 'vs_bot':
            game_data['game_state'] = vs_bot.update_vs(game_data)
        # Các trạng thái khác không cần update logic phức tạp (chỉ chờ input)

        # --- Vẽ màn hình ---
        current_state = game_data['game_state'] # Lấy lại trạng thái lần nữa
        if current_state == 'home':
            # Vẽ màn hình home trực tiếp
            screen.fill(settings.WHITE)
            utils.draw_text(screen, 'NO ESCAPE', fonts['large'], settings.RED, settings.WIDTH // 2, settings.HEIGHT // 4)
            button_1p_rect = pygame.Rect(settings.WIDTH // 2 - 100, settings.HEIGHT // 2 - 50, 200, 50)
            button_vs_bot_rect = pygame.Rect(settings.WIDTH // 2 - 100, settings.HEIGHT // 2 + 20, 200, 50)
            button_exit_rect = pygame.Rect(settings.WIDTH // 2 - 100, settings.HEIGHT // 2 + 90, 200, 50)
            pygame.draw.rect(screen, settings.GREEN, button_1p_rect); pygame.draw.rect(screen, settings.GREEN, button_vs_bot_rect); pygame.draw.rect(screen, settings.RED, button_exit_rect)
            utils.draw_text(screen, '1 Player', fonts['button'], settings.BLACK, button_1p_rect.centerx, button_1p_rect.centery); utils.draw_text(screen, 'VS Bot', fonts['button'], settings.BLACK, button_vs_bot_rect.centerx, button_vs_bot_rect.centery); utils.draw_text(screen, 'Exit', fonts['button'], settings.BLACK, button_exit_rect.centerx, button_exit_rect.centery)
            # Xử lý click nút home (sau khi đã lấy sự kiện click)
            if game_data['click']:
                if button_1p_rect.collidepoint(game_data['mouse_pos']):
                    game_data['maze'] = Maze(settings.MAZE_COLS, settings.MAZE_ROWS, settings.CELL_SIZE); game_data['player_pos'] = game_data['maze'].entry_pos; game_data['1p_goal_pos'] = game_data['maze'].exit_pos
                    game_data['start_time'] = pygame.time.get_ticks(); game_data['remaining_time'] = settings.TIME_LIMIT_1P; game_data['game_state'] = '1_player'
                elif button_vs_bot_rect.collidepoint(game_data['mouse_pos']):
                    game_data['maze'] = Maze(settings.MAZE_COLS, settings.MAZE_ROWS, settings.CELL_SIZE); game_data['player_pos'] = game_data['maze'].entry_pos; game_data['bot_pos'] = game_data['maze'].exit_pos
                    game_data['vs_player_goal_pos'] = game_data['bot_pos']; game_data['bot_goal_pos'] = game_data['player_pos']
                    game_data['bot_path'] = utils.find_path_bfs(game_data['maze'], game_data['bot_pos'], game_data['bot_goal_pos'])
                    if game_data['bot_path'] is None: game_data['game_state'] = 'home'
                    else: game_data['game_state'] = 'vs_bot'; game_data['bot_move_timer'] = 0
                elif button_exit_rect.collidepoint(game_data['mouse_pos']):
                    running = False # Thoát game

        elif current_state == '1_player':
            one_player.draw_1p(screen, maze_surface, game_data, fonts)
        elif current_state == 'paused_1p':
            one_player.draw_paused_1p(screen, maze_surface, game_data, fonts)
        elif current_state == 'win_1p':
            one_player.draw_win_1p(screen, game_data, fonts)
        elif current_state == 'lose_1p':
            one_player.draw_lose_1p(screen, game_data, fonts)
        elif current_state == 'vs_bot':
            vs_bot.draw_vs(screen, maze_surface, game_data, fonts)
        elif current_state == 'paused_vs':
             vs_bot.draw_paused_vs(screen, maze_surface, game_data, fonts)
        elif current_state == 'player_wins_vs':
             vs_bot.draw_player_wins_vs(screen, game_data, fonts)
        elif current_state == 'bot_wins_vs':
             vs_bot.draw_bot_wins_vs(screen, game_data, fonts)


        # --- Cập nhật hiển thị ---
        pygame.display.flip()

        # --- Giới hạn FPS ---
        clock.tick(settings.FPS)

    # --- Kết thúc Pygame ---
    pygame.quit()
    sys.exit()

# --- Chạy game ---
if __name__ == '__main__':
    run_game()

# -------- Hết file: noescape.py --------