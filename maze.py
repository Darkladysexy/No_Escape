# -------- File: maze.py --------
import pygame
import random

def get_gradient_color(start_color, end_color, t):
    """Trả về màu nằm giữa start_color và end_color theo tỷ lệ t (0..1)."""
    return (
        int(start_color[0] + (end_color[0] - start_color[0]) * t),
        int(start_color[1] + (end_color[1] - start_color[1]) * t),
        int(start_color[2] + (end_color[2] - start_color[2]) * t),
    )

class Cell:
    """Đại diện cho một ô trong lưới mê cung."""
    def __init__(self, x, y, cell_size):
        self.x = x
        self.y = y
        self.cell_size = cell_size
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.visited = False

    def draw(self, surface, color, wall_thickness=1):
        """Vẽ các bức tường của ô lên bề mặt được cung cấp."""
        px = self.x * self.cell_size
        py = self.y * self.cell_size
        cs = self.cell_size # cell_size
        ws = wall_thickness # wall thickness

        if self.walls['top']:
            pygame.draw.line(surface, color, (px, py), (px + cs, py), ws)
        if self.walls['right']:
            pygame.draw.line(surface, color, (px + cs, py), (px + cs, py + cs), ws)
        if self.walls['bottom']:
            pygame.draw.line(surface, color, (px + cs, py + cs), (px, py + cs), ws)
        if self.walls['left']:
            pygame.draw.line(surface, color, (px, py + cs), (px, py), ws)

    def get_neighbors(self, grid, cols, rows):
        """Tìm các ô lân cận chưa được thăm (cho thuật toán sinh)."""
        neighbors = []
        indices = [
            (self.x, self.y - 1), # Top
            (self.x + 1, self.y), # Right
            (self.x, self.y + 1), # Bottom
            (self.x - 1, self.y)  # Left
        ]
        for i, j in indices:
            if 0 <= i < cols and 0 <= j < rows:
                neighbor_cell = grid[j][i] # Grid is accessed [row][col]
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
        self.grid = [[Cell(col, row, cell_size) for col in range(cols)] for row in range(rows)]
        self._generate_maze(start_cell_coords=self.entry_pos)
        self._open_entry_exit()

    def _remove_walls(self, current_cell, next_cell):
        """Loại bỏ bức tường giữa hai ô liền kề."""
        dx = current_cell.x - next_cell.x
        dy = current_cell.y - next_cell.y
        if dx == 1: # current is right of next
            current_cell.walls['left'] = False; next_cell.walls['right'] = False
        elif dx == -1: # current is left of next
            current_cell.walls['right'] = False; next_cell.walls['left'] = False
        elif dy == 1: # current is below next
            current_cell.walls['top'] = False; next_cell.walls['bottom'] = False
        elif dy == -1: # current is above next
            current_cell.walls['bottom'] = False; next_cell.walls['top'] = False

    def _generate_maze(self, start_cell_coords=(0,0)):
        """Sinh mê cung bằng thuật toán Randomized DFS."""
        stack = []
        start_col, start_row = start_cell_coords
        if not (0 <= start_col < self.cols and 0 <= start_row < self.rows):
            start_col, start_row = 0, 0
        start_cell = self.grid[start_row][start_col]
        start_cell.visited = True
        stack.append(start_cell)
        while stack:
            current_cell = stack[-1]
            neighbors = current_cell.get_neighbors(self.grid, self.cols, self.rows)
            if neighbors:
                next_cell = random.choice(neighbors)
                next_cell.visited = True
                self._remove_walls(current_cell, next_cell)
                stack.append(next_cell)
            else:
                stack.pop()

    def _open_entry_exit(self):
        """Mở tường ngoài tại các ô lối vào và lối ra."""
        entry_col, entry_row = self.entry_pos
        exit_col, exit_row = self.exit_pos
        if 0 <= entry_col < self.cols and 0 <= entry_row < self.rows:
            cell_entry = self.grid[entry_row][entry_col]
            if entry_row == 0: cell_entry.walls['top'] = False
            elif entry_col == 0: cell_entry.walls['left'] = False
            elif entry_row == self.rows - 1: cell_entry.walls['bottom'] = False
            elif entry_col == self.cols - 1: cell_entry.walls['right'] = False
            else: cell_entry.walls['top'] = False
        if 0 <= exit_col < self.cols and 0 <= exit_row < self.rows:
            cell_exit = self.grid[exit_row][exit_col]
            if exit_row == self.rows - 1 and self.exit_pos != self.entry_pos: cell_exit.walls['bottom'] = False
            elif exit_col == self.cols - 1 and self.exit_pos != self.entry_pos: cell_exit.walls['right'] = False
            elif exit_row == 0 and self.exit_pos != self.entry_pos: cell_exit.walls['top'] = False
            elif exit_col == 0 and self.exit_pos != self.entry_pos: cell_exit.walls['left'] = False
            else: cell_exit.walls['bottom'] = False

    def draw(self, surface, wall_color=None, background_color=(0, 0, 0), wall_thickness=2):
    # """Vẽ toàn bộ mê cung với hiệu ứng màu gradient cho tường."""
        surface.fill(background_color)
        for row in self.grid:
            for cell in row:
                # Tính t dựa vào vị trí cell.x để tạo gradient ngang
                t = cell.x / (self.cols - 1) if self.cols > 1 else 0
                # Màu từ xanh dương → đỏ
                gradient_color = get_gradient_color((0, 0, 255), (255, 0, 0), t)
                cell.draw(surface, gradient_color, wall_thickness)


    def get_cell(self, col, row):
         """Lấy đối tượng Cell tại tọa độ lưới (col, row)."""
         if 0 <= col < self.cols and 0 <= row < self.rows:
             return self.grid[row][col]
         return None