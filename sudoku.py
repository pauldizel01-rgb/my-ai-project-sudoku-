import pygame
import random
import sys
import time
import json
import os
from copy import deepcopy

# Инициализация Pygame
pygame.init()

# Константы
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 750
BOARD_SIZE = 9
CELL_SIZE = 66
BOARD_WIDTH = CELL_SIZE * 9
BOARD_HEIGHT = CELL_SIZE * 9
OFFSET_X = (WINDOW_WIDTH - BOARD_WIDTH) // 2
OFFSET_Y = 10

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
LIGHT_BLUE = (173, 216, 230)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
LIGHT_GREEN = (144, 238, 144)

# Уровни сложности
DIFFICULTY_LEVELS = {
    'easy': 30,
    'medium': 40,
    'hard': 50
}

class SudokuGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Судоку")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 24)
        
        # Состояние игры
        self.game_state = 'menu'  # menu, playing, game_over
        self.selected_difficulty = None
        
        # Игровые переменные
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.original_board = [[0 for _ in range(9)] for _ in range(9)]
        self.solution = [[0 for _ in range(9)] for _ in range(9)]
        self.selected_cell = None
        self.difficulty = 'medium'
        self.errors = 0
        self.start_time = None
        self.game_over = False
        self.history = []
        
        # Загрузка лучших времен
        self.best_times = self.load_best_times()
        
        # Кнопки игры
        self.game_buttons = []
        self.create_game_buttons()
        
        # Кнопки меню
        self.menu_buttons = []
        self.create_menu_buttons()
    
    def create_menu_buttons(self):
        """Создание кнопок меню выбора сложности"""
        self.menu_buttons = []
        button_width = 200
        button_height = 60
        spacing = 20
        start_y = WINDOW_HEIGHT // 2 - 100
        
        difficulties = [
            ('Лёгкий', 'easy', LIGHT_GREEN),
            ('Средний', 'medium', YELLOW),
            ('Сложный', 'hard', ORANGE)
        ]
        
        for i, (text, diff, color) in enumerate(difficulties):
            x = (WINDOW_WIDTH - button_width) // 2
            y = start_y + i * (button_height + spacing)
            self.menu_buttons.append({
                'rect': pygame.Rect(x, y, button_width, button_height),
                'text': text,
                'difficulty': diff,
                'color': color,
                'hover': False
            })
    
    def create_game_buttons(self):
        """Создание кнопок игрового интерфейса"""
        self.game_buttons = []
        button_width = 75
        button_height = 30
        
        buttons_text = [
            ('Новая', self.new_game),
            ('Решить', self.solve_board),
            ('Подсказка', self.hint),
            ('Отмена', self.undo),
            ('Меню', self.return_to_menu)
        ]
        
        for text, action in buttons_text:
            self.game_buttons.append({
                'rect': pygame.Rect(0, 0, button_width, button_height),
                'text': text,
                'action': action
            })
    
    def load_best_times(self):
        """Загрузка лучших времен из файла"""
        try:
            if os.path.exists('sudoku_best_times.json'):
                with open('sudoku_best_times.json', 'r') as f:
                    return json.load(f)
        except:
            pass
        return {'easy': None, 'medium': None, 'hard': None}
    
    def save_best_times(self):
        """Сохранение лучших времен в файл"""
        try:
            with open('sudoku_best_times.json', 'w') as f:
                json.dump(self.best_times, f)
        except:
            pass
    
    def start_game(self, difficulty):
        """Начать игру с выбранной сложностью"""
        self.selected_difficulty = difficulty
        self.difficulty = difficulty
        self.game_state = 'playing'
        self.new_game()
    
    def return_to_menu(self):
        """Вернуться в главное меню"""
        self.game_state = 'menu'
        self.selected_difficulty = None
        self.selected_cell = None
    
    def new_game(self):
        """Начать новую игру"""
        # Генерация полного решенного судоку
        self.generate_full_board()
        self.solution = deepcopy(self.board)
        
        # Удаление клеток в зависимости от сложности
        empty_cells = DIFFICULTY_LEVELS[self.difficulty]
        self.remove_cells(empty_cells)
        
        self.original_board = deepcopy(self.board)
        self.errors = 0
        self.start_time = time.time()
        self.game_over = False
        self.history = []
        self.selected_cell = None
    
    def generate_full_board(self):
        """Генерация полностью заполненного судоку"""
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.fill_board()
    
    def fill_board(self):
        """Заполнение доски с помощью backtracking"""
        numbers = list(range(1, 10))
        
        def solve():
            for i in range(9):
                for j in range(9):
                    if self.board[i][j] == 0:
                        random.shuffle(numbers)
                        for num in numbers:
                            if self.is_valid_move(i, j, num):
                                self.board[i][j] = num
                                if solve():
                                    return True
                                self.board[i][j] = 0
                        return False
            return True
        
        solve()
    
    def is_valid_move(self, row, col, num):
        """Проверка, можно ли поставить число в клетку"""
        # Проверка строки
        for j in range(9):
            if self.board[row][j] == num:
                return False
        
        # Проверка столбца
        for i in range(9):
            if self.board[i][col] == num:
                return False
        
        # Проверка блока 3x3
        block_row = row // 3 * 3
        block_col = col // 3 * 3
        for i in range(block_row, block_row + 3):
            for j in range(block_col, block_col + 3):
                if self.board[i][j] == num:
                    return False
        
        return True
    
    def remove_cells(self, count):
        """Удаление указанного количества клеток"""
        cells = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(cells)
        
        removed = 0
        for i, j in cells:
            if removed < count:
                self.board[i][j] = 0
                removed += 1
    
    def solve_board(self):
        """Автоматическое решение судоку"""
        if self.game_over or self.game_state != 'playing':
            return
        
        self.save_state()
        
        for i in range(9):
            for j in range(9):
                if self.original_board[i][j] == 0:
                    self.board[i][j] = self.solution[i][j]
        
        self.check_win()
    
    def hint(self):
        """Подсказка - заполняет одну правильную клетку"""
        if self.game_over or self.game_state != 'playing':
            return
        
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0 and self.original_board[i][j] == 0:
                    self.save_state()
                    self.board[i][j] = self.solution[i][j]
                    self.check_win()
                    return
    
    def undo(self):
        """Отмена последнего хода"""
        if self.history and self.game_state == 'playing':
            last_state = self.history.pop()
            self.board = last_state['board']
            self.errors = last_state['errors']
            self.check_win()
    
    def save_state(self):
        """Сохранение текущего состояния для отмены"""
        self.history.append({
            'board': deepcopy(self.board),
            'errors': self.errors
        })
        
        if len(self.history) > 50:
            self.history.pop(0)
    
    def make_move(self, row, col, num):
        """Сделать ход"""
        if self.game_over or self.game_state != 'playing':
            return False
        
        if self.original_board[row][col] != 0:
            return False
        
        self.save_state()
        
        if num == self.solution[row][col]:
            self.board[row][col] = num
            self.check_win()
            return True
        else:
            self.board[row][col] = num
            self.errors += 1
            self.check_win()
            return False
    
    def check_win(self):
        """Проверка на победу"""
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0 or self.board[i][j] != self.solution[i][j]:
                    return False
        
        self.game_over = True
        
        if self.start_time:
            elapsed_time = int(time.time() - self.start_time)
            if self.best_times[self.difficulty] is None or elapsed_time < self.best_times[self.difficulty]:
                self.best_times[self.difficulty] = elapsed_time
                self.save_best_times()
        
        return True
    
    def draw_menu(self):
        """Отрисовка главного меню"""
        self.screen.fill(WHITE)
        
        # Заголовок
        title_text = self.big_font.render("СУДОКУ", True, PURPLE)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 100))
        self.screen.blit(title_text, title_rect)
        
        # Подзаголовок
        subtitle_text = self.font.render("Выберите уровень сложности", True, DARK_GRAY)
        subtitle_rect = subtitle_text.get_rect(center=(WINDOW_WIDTH // 2, 180))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Кнопки сложности
        for button in self.menu_buttons:
            # Эффект наведения
            mouse_pos = pygame.mouse.get_pos()
            if button['rect'].collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, button['color'], button['rect'])
                pygame.draw.rect(self.screen, BLACK, button['rect'], 3)
            else:
                pygame.draw.rect(self.screen, button['color'], button['rect'])
                pygame.draw.rect(self.screen, BLACK, button['rect'], 2)
            
            text = self.font.render(button['text'], True, BLACK)
            text_rect = text.get_rect(center=button['rect'].center)
            self.screen.blit(text, text_rect)
        
        # Отображение лучших времен
        y_offset = WINDOW_HEIGHT - 120
        best_title = self.small_font.render("Лучшие времена:", True, DARK_GRAY)
        self.screen.blit(best_title, (WINDOW_WIDTH // 2 - 80, y_offset))
        
        difficulties = [('Лёгкий', 'easy'), ('Средний', 'medium'), ('Сложный', 'hard')]
        for i, (name, diff) in enumerate(difficulties):
            if self.best_times[diff]:
                minutes = self.best_times[diff] // 60
                seconds = self.best_times[diff] % 60
                time_text = f"{name}: {minutes:02d}:{seconds:02d}"
            else:
                time_text = f"{name}: ---"
            
            time_surface = self.small_font.render(time_text, True, BLACK)
            self.screen.blit(time_surface, (WINDOW_WIDTH // 2 - 60, y_offset + 25 + i * 25))
    
    def draw_game(self):
        """Отрисовка игрового экрана"""
        self.screen.fill(WHITE)
        
        # Отрисовка сетки
        self.draw_grid()
        
        # Отрисовка чисел
        self.draw_numbers()
        
        # Отрисовка информации
        self.draw_info()
        
        # Отрисовка кнопок
        self.draw_game_buttons()
        
        # Отрисовка анимации победы
        if self.game_over:
            self.draw_win_animation()
    
    def draw_grid(self):
        """Отрисовка сетки"""
        for i in range(10):
            line_width = 1 if i % 3 != 0 else 3
            pygame.draw.line(self.screen, BLACK, 
                           (OFFSET_X + i * CELL_SIZE, OFFSET_Y),
                           (OFFSET_X + i * CELL_SIZE, OFFSET_Y + BOARD_HEIGHT),
                           line_width)
            pygame.draw.line(self.screen, BLACK,
                           (OFFSET_X, OFFSET_Y + i * CELL_SIZE),
                           (OFFSET_X + BOARD_WIDTH, OFFSET_Y + i * CELL_SIZE),
                           line_width)
    
    def draw_numbers(self):
        """Отрисовка чисел"""
        for i in range(9):
            for j in range(9):
                num = self.board[i][j]
                if num != 0:
                    if self.original_board[i][j] != 0:
                        color = BLACK
                    else:
                        if num != self.solution[i][j]:
                            color = RED
                        else:
                            color = BLUE
                    
                    if self.selected_cell:
                        selected_row, selected_col = self.selected_cell
                        if i == selected_row or j == selected_col or \
                           (i // 3 == selected_row // 3 and j // 3 == selected_col // 3):
                            if not self.game_over:
                                pygame.draw.rect(self.screen, LIGHT_BLUE,
                                               (OFFSET_X + j * CELL_SIZE,
                                                OFFSET_Y + i * CELL_SIZE,
                                                CELL_SIZE, CELL_SIZE))
                    
                    if self.selected_cell and (i, j) == self.selected_cell:
                        pygame.draw.rect(self.screen, YELLOW,
                                       (OFFSET_X + j * CELL_SIZE,
                                        OFFSET_Y + i * CELL_SIZE,
                                        CELL_SIZE, CELL_SIZE))
                    
                    text = self.font.render(str(num), True, color)
                    text_rect = text.get_rect(center=(OFFSET_X + j * CELL_SIZE + CELL_SIZE // 2,
                                                      OFFSET_Y + i * CELL_SIZE + CELL_SIZE // 2))
                    self.screen.blit(text, text_rect)
    
    def draw_game_buttons(self):
        """Отрисовка игровых кнопок"""
        button_width = 75
        button_height = 30
        total_buttons = len(self.game_buttons)
        spacing = 10
        total_width = total_buttons * button_width + (total_buttons - 1) * spacing
        x_start = (WINDOW_WIDTH - total_width) // 2
        y_pos = BOARD_HEIGHT + OFFSET_Y + 100
        
        for i, button in enumerate(self.game_buttons):
            x = x_start + i * (button_width + spacing)
            button['rect'].x = x
            button['rect'].y = y_pos
            
            pygame.draw.rect(self.screen, GRAY, button['rect'])
            pygame.draw.rect(self.screen, BLACK, button['rect'], 2)
            text = self.small_font.render(button['text'], True, BLACK)
            text_rect = text.get_rect(center=button['rect'].center)
            self.screen.blit(text, text_rect)
    
    def draw_info(self):
        """Отрисовка информации"""
        info_y_start = BOARD_HEIGHT + OFFSET_Y + 10
        
        if self.start_time and not self.game_over:
            elapsed = int(time.time() - self.start_time)
        elif self.game_over and self.start_time:
            elapsed = int(time.time() - self.start_time)
        else:
            elapsed = 0
        
        minutes = elapsed // 60
        seconds = elapsed % 60
        timer_text = f"Время: {minutes:02d}:{seconds:02d}"
        timer_surface = self.font.render(timer_text, True, BLACK)
        self.screen.blit(timer_surface, (10, info_y_start))
        
        errors_text = f"Ошибки: {self.errors}"
        errors_surface = self.font.render(errors_text, True, RED if self.errors > 0 else BLACK)
        self.screen.blit(errors_surface, (10, info_y_start + 40))
        
        # Отображение текущей сложности
        diff_names = {'easy': 'Лёгкий', 'medium': 'Средний', 'hard': 'Сложный'}
        diff_text = f"Сложность: {diff_names[self.difficulty]}"
        diff_surface = self.small_font.render(diff_text, True, DARK_GRAY)
        self.screen.blit(diff_surface, (10, info_y_start + 75))
        
        if self.best_times[self.difficulty]:
            best = self.best_times[self.difficulty]
            minutes = best // 60
            seconds = best % 60
            best_text = f"Лучшее: {minutes:02d}:{seconds:02d}"
            best_surface = self.small_font.render(best_text, True, DARK_GRAY)
            self.screen.blit(best_surface, (10, info_y_start + 100))
    
    def draw_win_animation(self):
        """Анимация победы"""
        alpha = abs(pygame.time.get_ticks() // 50 % 20 - 10) / 10
        size = int(48 + alpha * 10)
        win_font = pygame.font.Font(None, size)
        win_text = win_font.render("ПОБЕДА!", True, ORANGE)
        text_rect = win_text.get_rect(center=(WINDOW_WIDTH // 2, BOARD_HEIGHT // 2))
        
        s = pygame.Surface((WINDOW_WIDTH, BOARD_HEIGHT))
        s.set_alpha(128)
        s.fill(WHITE)
        self.screen.blit(s, (0, OFFSET_Y))
        self.screen.blit(win_text, text_rect)
    
    def handle_menu_click(self, pos):
        """Обработка клика в меню"""
        for button in self.menu_buttons:
            if button['rect'].collidepoint(pos):
                self.start_game(button['difficulty'])
                return
    
    def handle_game_click(self, pos):
        """Обработка клика в игре"""
        for button in self.game_buttons:
            if button['rect'].collidepoint(pos):
                button['action']()
                return
        
        if OFFSET_X <= pos[0] <= OFFSET_X + BOARD_WIDTH and OFFSET_Y <= pos[1] <= OFFSET_Y + BOARD_HEIGHT:
            col = (pos[0] - OFFSET_X) // CELL_SIZE
            row = (pos[1] - OFFSET_Y) // CELL_SIZE
            if 0 <= row < 9 and 0 <= col < 9:
                self.selected_cell = (row, col)
    
    def handle_game_key(self, key):
        """Обработка нажатий клавиш в игре"""
        if self.selected_cell and not self.game_over:
            row, col = self.selected_cell
            
            if pygame.K_1 <= key <= pygame.K_9:
                num = key - pygame.K_0
                self.make_move(row, col, num)
            elif key == pygame.K_BACKSPACE or key == pygame.K_DELETE:
                if self.original_board[row][col] == 0:
                    self.save_state()
                    self.board[row][col] = 0
                    self.check_win()
        
        if key == pygame.K_h:
            self.hint()
        elif key == pygame.K_n:
            self.new_game()
        elif key == pygame.K_s:
            self.solve_board()
        elif key == pygame.K_ESCAPE:
            self.return_to_menu()
    
    def run(self):
        """Главный игровой цикл"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_state == 'menu':
                        self.handle_menu_click(event.pos)
                    elif self.game_state == 'playing':
                        self.handle_game_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if self.game_state == 'playing':
                        self.handle_game_key(event.key)
                    elif self.game_state == 'menu' and event.key == pygame.K_ESCAPE:
                        running = False
            
            if self.game_state == 'menu':
                self.draw_menu()
            elif self.game_state == 'playing':
                self.draw_game()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = SudokuGame()
    game.run()
