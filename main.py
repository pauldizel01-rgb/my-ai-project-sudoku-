import pygame
import random
import time
import json
import os
from copy import deepcopy

pygame.init()

WIDTH, HEIGHT = 600, 750
CELL_SIZE = 60
GRID_SIZE = 9
GRID_OFFSET_X = (WIDTH - GRID_SIZE * CELL_SIZE) // 2
GRID_OFFSET_Y = 80

CONFIG_FILE = "config.json"

LIGHT_THEME = {
    "bg": (255, 255, 255),
    "grid_line": (180, 180, 180),
    "grid_thick": (0, 0, 0),
    "cell_selected": (255, 230, 100),
    "cell_row_col": (180, 200, 255),
    "text_fixed": (0, 0, 0),
    "text_user": (30, 70, 150),
    "text_error": (200, 50, 50),
    "text_hint": (50, 180, 80),
    "button_bg": (30, 70, 150),
    "button_hover": (50, 100, 200),
    "button_text": (255, 255, 255),
    "title": (30, 70, 150),
    "subtitle": (100, 100, 100),
    "hint_text": (180, 180, 180),
    "hotkey": (180, 180, 180),
}

DARK_THEME = {
    "bg": (30, 30, 40),
    "grid_line": (80, 80, 100),
    "grid_thick": (200, 200, 220),
    "cell_selected": (200, 180, 50),
    "cell_row_col": (60, 70, 120),
    "text_fixed": (220, 220, 230),
    "text_user": (100, 150, 255),
    "text_error": (255, 80, 80),
    "text_hint": (80, 220, 120),
    "button_bg": (60, 60, 90),
    "button_hover": (80, 100, 150),
    "button_text": (230, 230, 240),
    "title": (100, 150, 255),
    "subtitle": (150, 150, 170),
    "hint_text": (100, 100, 120),
    "hotkey": (100, 100, 120),
}

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Судоку")
clock = pygame.time.Clock()
font_large = pygame.font.Font(None, 48)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 28)
font_timer = pygame.font.Font(None, 32)

RED = (200, 50, 50)
GREEN = (50, 180, 80)
GOLD = (255, 200, 50)
BLUE = (50, 100, 200)


def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"theme": "light"}


def save_config(config: dict):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)


def get_theme() -> dict:
    config = load_config()
    return LIGHT_THEME if config.get("theme") == "light" else DARK_THEME


def toggle_theme():
    config = load_config()
    config["theme"] = "dark" if config["theme"] == "light" else "light"
    save_config(config)
    return config["theme"]


def load_best_times() -> dict[str, float | None]:
    best_file = "best_times.json"
    if os.path.exists(best_file):
        with open(best_file, "r") as f:
            return json.load(f)
    return {"easy": None, "medium": None, "hard": None}


def save_best_times(times):
    best_file = "best_times.json"
    with open(best_file, "w") as f:
        json.dump(times, f)


def is_valid(board, row, col, num):
    for i in range(9):
        if board[row][i] == num or board[i][col] == num:
            return False
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True


def solve_sudoku(board):
    empty = find_empty(board)
    if not empty:
        return True
    row, col = empty
    for num in range(1, 10):
        if is_valid(board, row, col, num):
            board[row][col] = num
            if solve_sudoku(board):
                return True
            board[row][col] = 0
    return False


def find_empty(board):
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                return (i, j)
    return None


def generate_sudoku(difficulty):
    board = [[0] * 9 for _ in range(9)]
    fill_board(board)
    solution = deepcopy(board)
    empty_count = {"easy": 30, "medium": 40, "hard": 50}[difficulty]
    cells_to_remove = empty_count
    positions = [(i, j) for i in range(9) for j in range(9)]
    random.shuffle(positions)
    removed = 0
    for pos in positions:
        if removed >= cells_to_remove:
            break
        row, col = pos
        backup = board[row][col]
        board[row][col] = 0
        test_board = deepcopy(board)
        if count_solutions(test_board) == 1:
            removed += 1
        else:
            board[row][col] = backup
    return board, solution


def count_solutions(board):
    empty = find_empty(board)
    if not empty:
        return 1
    row, col = empty
    count = 0
    for num in range(1, 10):
        if is_valid(board, row, col, num):
            board[row][col] = num
            count += count_solutions(board)
            board[row][col] = 0
            if count > 1:
                return count
    return count


def fill_board(board):
    nums = list(range(1, 10))
    random.shuffle(nums)
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                for num in nums:
                    if is_valid(board, i, j, num):
                        board[i][j] = num
                        if fill_board(board):
                            return True
                        board[i][j] = 0
                return False
    return True


class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.is_hovered = False
    
    def draw(self, surface, theme):
        color = theme["button_hover"] if self.is_hovered else theme["button_bg"]
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        text_surf = font_small.render(self.text, True, theme["button_text"])
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class ThemeButton:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH - 60, 10, 50, 30)
        self.is_hovered = False
    
    def draw(self, surface, theme):
        is_light = theme == LIGHT_THEME
        color = theme["button_hover"] if self.is_hovered else theme["button_bg"]
        pygame.draw.rect(surface, color, self.rect, border_radius=15)
        icon = "☀" if is_light else "☾"
        text_surf = font_small.render(icon, True, theme["button_text"])
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class MenuState:
    def __init__(self):
        self.buttons = []
        self.theme_btn = ThemeButton()
        self.difficulty_labels = ["Лёгкий", "Средний", "Сложный"]
        self.difficulties = ["easy", "medium", "hard"]
        self.best_times = load_best_times()
        self.hover_difficulty = -1
        for i in range(3):
            y = 280 + i * 90
            self.buttons.append(pygame.Rect(WIDTH // 2 - 120, y, 240, 60))
    
    def draw(self, theme):
        screen.fill(theme["bg"])
        
        title = font_large.render("С У Д О К У", True, theme["title"])
        title_rect = title.get_rect(center=(WIDTH // 2, 100))
        screen.blit(title, title_rect)
        
        subtitle = font_small.render("Выберите сложность", True, theme["subtitle"])
        sub_rect = subtitle.get_rect(center=(WIDTH // 2, 200))
        screen.blit(subtitle, sub_rect)
        
        for i, (btn, label, diff) in enumerate(zip(self.buttons, self.difficulty_labels, self.difficulties)):
            color = theme["button_hover"] if self.hover_difficulty == i else theme["button_bg"]
            pygame.draw.rect(screen, color, btn, border_radius=10)
            text_surf = font_medium.render(label, True, theme["button_text"])
            text_rect = text_surf.get_rect(center=btn.center)
            screen.blit(text_surf, text_rect)
            
            best_time = self.best_times.get(diff)
            if best_time:
                mins, secs = divmod(int(best_time), 60)
                best_text = f"Рекорд: {mins:02d}:{secs:02d}"
            else:
                best_text = "Рекорд: --:--"
            best_surf = font_small.render(best_text, True, theme["hint_text"])
            best_rect = best_surf.get_rect(center=(btn.centerx, btn.bottom + 18))
            screen.blit(best_surf, best_rect)
        
        hint = font_small.render("1, 2, 3 или клик для выбора", True, theme["hint_text"])
        hint_rect = hint.get_rect(center=(WIDTH // 2, 680))
        screen.blit(hint, hint_rect)
        
        self.theme_btn.draw(screen, theme)
        
        pygame.display.flip()
    
    def handle_click(self, pos):
        if self.theme_btn.is_clicked(pos):
            return "theme"
        for i, btn in enumerate(self.buttons):
            if btn.collidepoint(pos):
                return self.difficulties[i]
        return None
    
    def handle_key(self, key):
        if key == pygame.K_1:
            return "easy"
        elif key == pygame.K_2:
            return "medium"
        elif key == pygame.K_3:
            return "hard"
        return None
    
    def update_hover(self, pos):
        self.theme_btn.check_hover(pos)
        self.hover_difficulty = -1
        for i, btn in enumerate(self.buttons):
            if btn.collidepoint(pos):
                self.hover_difficulty = i


class GameState:
    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.board, self.solution = generate_sudoku(difficulty)
        self.user_board = deepcopy(self.board)
        self.selected = None
        self.timer = 0
        self.start_time = time.time()
        self.errors = 0
        self.history = []
        self.hints_used = 0
        self.is_solved = False
        self.show_solution = False
        self.win_animation = None
        self.theme_btn = ThemeButton()
        self.buttons = [
            Button(20, 620, 100, 40, "Новая"),
            Button(130, 620, 100, 40, "Решить"),
            Button(240, 620, 100, 40, "Подсказка"),
            Button(350, 620, 100, 40, "Отмена"),
            Button(460, 620, 100, 40, "Меню"),
        ]
        self.hotkey_labels = ["N", "S", "H", "Z", "ESC"]
    
    def draw(self, theme):
        elapsed = time.time() - self.start_time
        if not self.is_solved:
            self.timer = elapsed
        
        screen.fill(theme["bg"])
        
        difficulty_names = {"easy": "Лёгкий", "medium": "Средний", "hard": "Сложный"}
        diff_text = font_medium.render(f"{difficulty_names[self.difficulty]}", True, theme["subtitle"])
        screen.blit(diff_text, (20, 15))
        
        mins, secs = divmod(int(self.timer), 60)
        timer_text = font_timer.render(f"Время: {mins:02d}:{secs:02d}", True, theme["title"])
        screen.blit(timer_text, (WIDTH - 180, 15))
        
        error_text = font_small.render(f"Ошибки: {self.errors}/3", True, RED)
        screen.blit(error_text, (WIDTH // 2 - 50, 15))
        
        self.draw_grid(theme)
        
        for btn in self.buttons:
            btn.draw(screen, theme)
        
        for i, label in enumerate(self.hotkey_labels):
            x = 30 + i * 110
            key_text = font_small.render(f"[{label}]", True, theme["hotkey"])
            screen.blit(key_text, (x, 668))
        
        self.theme_btn.draw(screen, theme)
        
        if self.is_solved:
            self.draw_win_animation(theme)
        
        pygame.display.flip()
    
    def draw_grid(self, theme):
        for i in range(10):
            thick = i % 3 == 0
            color = theme["grid_thick"] if thick else theme["grid_line"]
            pygame.draw.line(screen, color,
                           (GRID_OFFSET_X, GRID_OFFSET_Y + i * CELL_SIZE),
                           (GRID_OFFSET_X + GRID_SIZE * CELL_SIZE, GRID_OFFSET_Y + i * CELL_SIZE),
                           3 if thick else 1)
            pygame.draw.line(screen, color,
                           (GRID_OFFSET_X + i * CELL_SIZE, GRID_OFFSET_Y),
                           (GRID_OFFSET_X + i * CELL_SIZE, GRID_OFFSET_Y + GRID_SIZE * CELL_SIZE),
                           3 if thick else 1)
        
        for row in range(9):
            for col in range(9):
                x = GRID_OFFSET_X + col * CELL_SIZE
                y = GRID_OFFSET_Y + row * CELL_SIZE
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                
                if self.selected and self.selected == (row, col):
                    pygame.draw.rect(screen, theme["cell_selected"], rect)
                elif self.selected:
                    sel_row, sel_col = self.selected
                    if row == sel_row or col == sel_col:
                        pygame.draw.rect(screen, theme["cell_row_col"], rect)
                    elif row // 3 == sel_row // 3 and col // 3 == sel_col // 3:
                        pygame.draw.rect(screen, theme["cell_row_col"], rect)
                
                value = self.user_board[row][col]
                if value != 0:
                    original = self.board[row][col]
                    if self.show_solution and not original:
                        color = theme["text_hint"]
                    elif not original:
                        if self.user_board[row][col] != self.solution[row][col]:
                            color = theme["text_error"]
                        else:
                            color = theme["text_user"]
                    else:
                        color = theme["text_fixed"]
                    font_size = font_medium if original else font_small
                    text = font_size.render(str(value), True, color)
                    text_rect = text.get_rect(center=rect.center)
                    screen.blit(text, text_rect)
    
    def draw_win_animation(self, theme):
        if self.win_animation is None:
            self.win_animation = {"time": 0, "particles": []}
            colors = [GOLD, GREEN, theme["title"], RED]
            for _ in range(50):
                self.win_animation["particles"].append({
                    "x": WIDTH // 2,
                    "y": HEIGHT // 2,
                    "vx": random.uniform(-5, 5),
                    "vy": random.uniform(-8, -2),
                    "color": random.choice(colors),
                    "size": random.randint(5, 12),
                    "life": 1.0
                })
        
        self.win_animation["time"] += 0.016
        
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        alpha = int(min(180, self.win_animation["time"] * 100))
        overlay.fill((255, 255, 255, alpha))
        screen.blit(overlay, (0, 0))
        
        for p in self.win_animation["particles"]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.2
            p["life"] -= 0.015
            if p["life"] > 0:
                alpha = int(255 * p["life"])
                color = (*p["color"][:3], alpha)
                pygame.draw.circle(screen, color, (int(p["x"]), int(p["y"])), int(p["size"] * p["life"]))
        
        if self.win_animation["time"] < 2:
            win_text = font_large.render("ПОБЕДА!", True, GREEN)
            win_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
            pygame.draw.rect(screen, theme["bg"], win_rect.inflate(40, 20), border_radius=10)
            screen.blit(win_text, win_rect)
            
            mins, secs = divmod(int(self.timer), 60)
            time_text = font_medium.render(f"Время: {mins:02d}:{secs:02d}", True, theme["subtitle"])
            time_rect = time_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
            screen.blit(time_text, time_rect)
            
            best = load_best_times()
            best_time = best.get(self.difficulty)
            if best_time is None or self.timer < best_time:
                new_record = font_small.render("Новый рекорд!", True, GOLD)
                new_rect = new_record.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
                screen.blit(new_record, new_rect)
    
    def handle_click(self, pos):
        if self.theme_btn.is_clicked(pos):
            return "theme"
        if self.is_solved and self.win_animation and self.win_animation["time"] > 1.5:
            return "menu"
        
        for btn in self.buttons:
            if btn.is_clicked(pos):
                return self.handle_button(btn.text)
        
        if GRID_OFFSET_X <= pos[0] < GRID_OFFSET_X + 9 * CELL_SIZE:
            if GRID_OFFSET_Y <= pos[1] < GRID_OFFSET_Y + 9 * CELL_SIZE:
                col = (pos[0] - GRID_OFFSET_X) // CELL_SIZE
                row = (pos[1] - GRID_OFFSET_Y) // CELL_SIZE
                if self.board[row][col] == 0:
                    self.selected = (row, col)
                    return "continue"
        
        return "continue"
    
    def handle_button(self, text):
        if text == "Новая":
            return "new"
        elif text == "Решить":
            self.show_solution = not self.show_solution
            if self.show_solution:
                self.user_board = deepcopy(self.solution)
                self.check_win()
            return "continue"
        elif text == "Подсказка":
            return "hint"
        elif text == "Отмена":
            return "undo"
        elif text == "Меню":
            return "menu"
        return "continue"
    
    def handle_key(self, key):
        if key == pygame.K_ESCAPE:
            return "menu"
        elif key == pygame.K_t:
            return "theme"
        elif key == pygame.K_n:
            return "new"
        elif key == pygame.K_s:
            self.show_solution = not self.show_solution
            if self.show_solution:
                self.user_board = deepcopy(self.solution)
                self.check_win()
            return "continue"
        elif key == pygame.K_h:
            return "hint"
        elif key == pygame.K_z:
            return "undo"
        elif key == pygame.K_BACKSPACE or key == pygame.K_DELETE:
            if self.selected and self.board[self.selected[0]][self.selected[1]] == 0:
                self.history.append(deepcopy(self.user_board))
                self.user_board[self.selected[0]][self.selected[1]] = 0
        elif pygame.K_1 <= key <= pygame.K_9:
            if self.selected and self.board[self.selected[0]][self.selected[1]] == 0:
                num = key - pygame.K_0
                self.history.append(deepcopy(self.user_board))
                self.user_board[self.selected[0]][self.selected[1]] = num
                if num != self.solution[self.selected[0]][self.selected[1]]:
                    self.errors += 1
                    if self.errors >= 3:
                        self.show_solution = True
                        self.user_board = deepcopy(self.solution)
                self.check_win()
        return "continue"
    
    def give_hint(self):
        empty_cells = []
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0 and self.user_board[i][j] == 0:
                    empty_cells.append((i, j))
        
        if not empty_cells:
            return False
        
        row, col = random.choice(empty_cells)
        self.selected = (row, col)
        self.history.append(deepcopy(self.user_board))
        self.user_board[row][col] = self.solution[row][col]
        self.hints_used += 1
        self.check_win()
        return True
    
    def undo(self):
        if self.history:
            self.user_board = self.history.pop()
            return True
        return False
    
    def check_win(self):
        for i in range(9):
            for j in range(9):
                if self.user_board[i][j] != self.solution[i][j]:
                    return
        self.is_solved = True
        best_times = load_best_times()
        best_time = best_times.get(self.difficulty)
        if best_time is None or self.timer < best_time:
            best_times[self.difficulty] = self.timer
            save_best_times(best_times)
    
    def update_hover(self, pos):
        self.theme_btn.check_hover(pos)
        for btn in self.buttons:
            btn.check_hover(pos)


def main():
    state = "menu"
    menu = MenuState()
    game = None
    theme = get_theme()
    
    running = True
    while running:
        events = pygame.event.get()
        
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if state == "menu":
                    result = menu.handle_click(pos)
                    if result == "theme":
                        toggle_theme()
                        theme = get_theme()
                    elif result:
                        game = GameState(result)
                        state = "game"
                elif state == "game" and game:
                    result = game.handle_click(pos)
                    if result == "theme":
                        toggle_theme()
                        theme = get_theme()
                    elif result == "menu":
                        state = "menu"
                        menu.best_times = load_best_times()
                    elif result == "new":
                        game = GameState(game.difficulty)
                    elif result == "hint":
                        game.give_hint()
                    elif result == "undo":
                        game.undo()
            elif event.type == pygame.MOUSEMOTION:
                pos = pygame.mouse.get_pos()
                if state == "menu":
                    menu.update_hover(pos)
                elif state == "game" and game:
                    game.update_hover(pos)
            elif event.type == pygame.KEYDOWN:
                if state == "menu":
                    result = menu.handle_key(event.key)
                    if result:
                        game = GameState(result)
                        state = "game"
                elif state == "game" and game:
                    result = game.handle_key(event.key)
                    if result == "theme":
                        toggle_theme()
                        theme = get_theme()
                    elif result == "menu":
                        state = "menu"
                        menu.best_times = load_best_times()
                    elif result == "new":
                        game = GameState(game.difficulty)
                    elif result == "hint":
                        game.give_hint()
                    elif result == "undo":
                        game.undo()
        
        if state == "menu":
            menu.draw(theme)
        elif state == "game" and game:
            game.draw(theme)
        
        clock.tick(60)
    
    pygame.quit()


if __name__ == "__main__":
    main()
