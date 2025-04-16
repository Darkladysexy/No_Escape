# -------- File: maze.py --------
import pygame
import random
# Import settings để dùng hằng số nếu cần (ví dụ màu nền khi vẽ)
import settings

class Cell:
    """Đại diện cho một ô trong lưới mê cung."""
    def __init__(self, x, y, cell_size):
        self.x = x # Tọa độ cột lưới
        self.y = y # Tọa độ hàng lưới
        self.cell_size = cell_size
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.visited = False # Dùng cho thuật toán sinh mê cung

    def draw(self, surface, color, wall_thickness=1):
        """Vẽ các bức tường của ô lên bề mặt được cung cấp."""
        px = self.x * self.cell_size # Tọa độ pixel x góc trên trái
        py = self.y * self.cell_size # Tọa độ pixel y góc trên trái

        # Vẽ 4 tường nếu chúng tồn tại (True)
        if self.walls['top']:
            pygame.draw.line(surface, color, (px, py), (px + self.cell_size, py), wall_thickness)
        if self.walls['right']:
            pygame.draw.line(surface, color, (px + self.cell_size, py), (px + self.cell_size, py + self.cell_size), wall_thickness)
        if self.walls['bottom']:
            pygame.draw.line(surface, color, (px + self.cell_size, py + self.cell_size), (px, py + self.cell_size), wall_thickness)
        if self.walls['left']:
            pygame.draw.line(surface, color, (px, py + self.cell_size), (px, py), wall_thickness)

    def get_neighbors(self, grid, cols, rows):
        """Tìm các ô lân cận chưa được thăm (cho thuật toán sinh)."""
        neighbors = []
        indices = [
            (self.x, self.y - 1), # Trên
            (self.x + 1, self.y), # Phải
            (self.x, self.y + 1), # Dưới
            (self.x - 1, self.y)  # Trái
        ]
        for i, j in indices:
            if 0 <= i < cols and 0 <= j < rows:
                neighbor_cell = grid[j][i] # Grid truy cập theo [hàng][cột]
                if not neighbor_cell.visited:
                    neighbors.append(neighbor_cell)
        return neighbors

class Maze:
    """Lớp tạo và quản lý mê cung."""
    def __init__(self, cols, rows, cell_size, entry_pos=(0, 0), exit_pos=None):
        self.cols = cols
        self.rows = rows
        self.cell_size = cell_size
        self.entry_pos = entry_pos
        self.exit_pos = (cols - 1, rows - 1) if exit_pos is None else exit_pos
        # Tạo lưới 2D chứa các đối tượng Cell
        self.grid = [[Cell(col, row, cell_size) for col in range(cols)] for row in range(rows)]
        # Sinh cấu trúc mê cung bên trong
        self._generate_maze(start_cell_coords=self.entry_pos)
        # Mở tường vào/ra
        self._open_entry_exit()

    def _remove_walls(self, current_cell, next_cell):
        """Loại bỏ bức tường giữa hai ô liền kề."""
        dx = current_cell.x - next_cell.x; dy = current_cell.y - next_cell.y
        if dx == 1: current_cell.walls['left'] = False; next_cell.walls['right'] = False
        elif dx == -1: current_cell.walls['right'] = False; next_cell.walls['left'] = False
        elif dy == 1: current_cell.walls['top'] = False; next_cell.walls['bottom'] = False
        elif dy == -1: current_cell.walls['bottom'] = False; next_cell.walls['top'] = False

    def _generate_maze(self, start_cell_coords=(0,0)):
        """Sinh mê cung bằng thuật toán Randomized DFS."""
        stack = []; start_col, start_row = start_cell_coords
        if not (0 <= start_col < self.cols and 0 <= start_row < self.rows): start_col, start_row = 0, 0
        start_cell = self.grid[start_row][start_col]; start_cell.visited = True; stack.append(start_cell)
        while stack:
            current_cell = stack[-1]; neighbors = current_cell.get_neighbors(self.grid, self.cols, self.rows)
            if neighbors:
                next_cell = random.choice(neighbors); next_cell.visited = True
                self._remove_walls(current_cell, next_cell); stack.append(next_cell)
            else: stack.pop()
        # Reset visited để có thể dùng cho việc khác (tìm đường) nếu cần
        # for r in self.grid:
        #     for c in r: c.visited = False

    def _open_entry_exit(self):
        """Mở tường ngoài tại các ô lối vào và lối ra."""
        entry_col, entry_row = self.entry_pos; exit_col, exit_row = self.exit_pos
        if 0 <= entry_col < self.cols and 0 <= entry_row < self.rows:
            cell_entry = self.grid[entry_row][entry_col]
            if entry_row == 0: cell_entry.walls['top'] = False
            elif entry_col == 0: cell_entry.walls['left'] = False
            elif entry_row == self.rows - 1: cell_entry.walls['bottom'] = False
            elif entry_col == self.cols - 1: cell_entry.walls['right'] = False
            else: cell_entry.walls['top'] = False # Mặc định nếu không ở biên
        if 0 <= exit_col < self.cols and 0 <= exit_row < self.rows:
            cell_exit = self.grid[exit_row][exit_col]
            if exit_row == self.rows - 1 and self.exit_pos != self.entry_pos: cell_exit.walls['bottom'] = False
            elif exit_col == self.cols - 1 and self.exit_pos != self.entry_pos: cell_exit.walls['right'] = False
            elif exit_row == 0 and self.exit_pos != self.entry_pos: cell_exit.walls['top'] = False
            elif exit_col == 0 and self.exit_pos != self.entry_pos: cell_exit.walls['left'] = False
            else: cell_exit.walls['bottom'] = False # Mặc định nếu không ở biên hoặc trùng

    def draw(self, surface, wall_color, background_color, wall_thickness):
        """Vẽ toàn bộ mê cung lên surface được cung cấp."""
        surface.fill(background_color) # Xóa nền của surface trước khi vẽ
        for row in self.grid:
            for cell in row:
                cell.draw(surface, wall_color, wall_thickness)

    def get_cell(self, col, row):
         """Lấy đối tượng Cell tại tọa độ lưới (col, row)."""
         if 0 <= col < self.cols and 0 <= row < self.rows:
             return self.grid[row][col]
         return None