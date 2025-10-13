import pygame
import numpy as np
import random
import time
import sys

# Pygame initialization
pygame.init()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (240, 240, 240)
DARK_GRAY = (100, 100, 100)
BLUE = (65, 105, 225)
RED = (220, 20, 60)
GREEN = (34, 139, 34)
LIGHT_BLUE = (173, 216, 230)
ORANGE = (255, 165, 0)
PURPLE = (147, 112, 219)
GOLD = (255, 215, 0)
LIGHT_GREEN = (144, 238, 144)
DARK_BLUE = (30, 60, 120)
YELLOW = (255, 255, 0)

# Screen setup
WIDTH, HEIGHT = 550, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🎯 AI Sudoku Game - Complete Edition")

# Fonts
try:
    font_large = pygame.font.Font(None, 42)
    font_medium = pygame.font.Font(None, 32)
    font_small = pygame.font.Font(None, 24)
    font_tiny = pygame.font.Font(None, 20)
except:
    font_large = pygame.font.SysFont('arial', 42, bold=True)
    font_medium = pygame.font.SysFont('arial', 32)
    font_small = pygame.font.SysFont('arial', 24)
    font_tiny = pygame.font.SysFont('arial', 20)


class Celebration:
    def __init__(self):
        self.particles = []
        self.duration = 4.0
        self.start_time = 0
        self.active = False

    def start(self):
        self.active = True
        self.start_time = time.time()
        self.particles = []
        for _ in range(80):
            self.particles.append({
                'x': random.randint(50, WIDTH - 50),
                'y': random.randint(100, HEIGHT - 100),
                'size': random.randint(4, 12),
                'color': random.choice([(255, 215, 0), (255, 165, 0), (255, 69, 0), (255, 20, 147)]),
                'speed_x': random.uniform(-4, 4),
                'speed_y': random.uniform(-6, -2),
            })

    def update(self):
        if not self.active:
            return False

        if time.time() - self.start_time > self.duration:
            self.active = False
            return False

        for particle in self.particles:
            particle['x'] += particle['speed_x']
            particle['y'] += particle['speed_y']
            particle['speed_y'] += 0.15
        return True

    def draw(self, surface):
        if not self.active:
            return
        for particle in self.particles:
            pygame.draw.circle(surface, particle['color'], (int(particle['x']), int(particle['y'])), particle['size'])


class Timer:
    def __init__(self):
        self.start_time = time.time()
        self.paused = False
        self.pause_start = 0
        self.total_paused = 0

    def pause(self):
        if not self.paused:
            self.paused = True
            self.pause_start = time.time()

    def resume(self):
        if self.paused:
            self.paused = False
            self.total_paused += time.time() - self.pause_start

    def get_elapsed(self):
        if self.paused:
            return int(self.pause_start - self.start_time - self.total_paused)
        return int(time.time() - self.start_time - self.total_paused)

    def get_formatted_time(self):
        elapsed = self.get_elapsed()
        minutes = elapsed // 60
        seconds = elapsed % 60
        return f"{minutes:02d}:{seconds:02d}"


class SudokuGenerator:
    def __init__(self):
        self.board = np.zeros((9, 9), dtype=int)

    def is_valid(self, board, row, col, num):
        # Check row
        for j in range(9):
            if board[row][j] == num:
                return False
        # Check column
        for i in range(9):
            if board[i][col] == num:
                return False
        # Check 3x3 box
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if board[start_row + i][start_col + j] == num:
                    return False
        return True

    def solve(self, board):
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    for num in range(1, 10):
                        if self.is_valid(board, i, j, num):
                            board[i][j] = num
                            if self.solve(board):
                                return True
                            board[i][j] = 0
                    return False
        return True

    def generate(self, difficulty=0.5):
        # Create empty board
        board = np.zeros((9, 9), dtype=int)

        # Fill diagonal boxes
        for box in range(3):
            numbers = list(range(1, 10))
            random.shuffle(numbers)
            for i in range(3):
                for j in range(3):
                    board[box * 3 + i][box * 3 + j] = numbers.pop()

        # Solve the board
        self.solve(board)
        solved_board = board.copy()

        # Remove numbers based on difficulty
        cells_to_remove = int(81 * difficulty)
        removed = 0

        positions = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(positions)

        for row, col in positions:
            if removed >= cells_to_remove:
                break
            if board[row][col] != 0:
                board[row][col] = 0
                removed += 1

        return board, solved_board


class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=BLACK):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.current_color = color
        self.text_surface = font_small.render(text, True, text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def draw(self, surface):
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, DARK_GRAY, self.rect, 2, border_radius=8)
        surface.blit(self.text_surface, self.text_rect)

    def is_hovered(self, pos):
        if self.rect.collidepoint(pos):
            self.current_color = self.hover_color
            return True
        self.current_color = self.color
        return False


class SudokuGame:
    def __init__(self):
        self.generator = SudokuGenerator()
        self.timer = Timer()
        self.celebration = Celebration()

        # Initialize buttons first
        self.initialize_buttons()

        # Then start new game
        self.new_game()

    def initialize_buttons(self):
        # Board size and position
        self.cell_size = 45
        self.board_start_x = (WIDTH - (self.cell_size * 9)) // 2
        self.board_start_y = 100

        # Create buttons
        button_width, button_height = 110, 40

        # Row 1
        self.solve_button = Button(50, 520, button_width, button_height, "AI Solve", GREEN, LIGHT_GREEN)
        self.hint_button = Button(180, 520, button_width, button_height, "Get Hint", LIGHT_BLUE, (200, 230, 255))
        self.new_game_button = Button(310, 520, button_width, button_height, "New Game", ORANGE, (255, 200, 100))
        self.check_button = Button(50, 580, button_width, button_height, "Check", PURPLE, (200, 180, 255))

        # Row 2 - Difficulty buttons
        self.easy_button = Button(180, 580, 80, 40, "Easy", LIGHT_GREEN, (200, 255, 200))
        self.medium_button = Button(270, 580, 80, 40, "Medium", ORANGE, (255, 220, 150))
        self.hard_button = Button(360, 580, 80, 40, "Hard", (255, 100, 100), (255, 150, 150))

        # Additional features buttons
        self.auto_check_button = Button(50, 470, 150, 35, "Auto-Check: OFF", LIGHT_GRAY, (200, 200, 200))
        self.pause_button = Button(220, 470, 100, 35, "Pause", YELLOW, (255, 255, 150))

        # Game states
        self.auto_check_enabled = False
        self.game_paused = False
        self.wrong_cells = set()

    def new_game(self, difficulty=0.5):
        # Generate board where ALL cells are empty (editable)
        self.board, self.solved_board = self.generator.generate(difficulty)

        # No fixed numbers - all cells are editable
        self.original_board = np.zeros((9, 9), dtype=int)

        self.selected = None
        self.message = "🔄 New game started! Click ANY cell and press 1-9 to enter numbers."
        self.message_time = time.time()
        self.timer = Timer()
        self.mistakes = 0
        self.hints_used = 0
        self.game_won = False
        self.current_difficulty = difficulty
        self.wrong_cells = set()
        self.auto_check_enabled = False
        self.auto_check_button.text = "Auto-Check: OFF"
        self.game_paused = False
        self.pause_button.text = "Pause"

    def check_win(self):
        # Check if all cells match the solved board
        for i in range(9):
            for j in range(9):
                if self.board[i][j] != self.solved_board[i][j]:
                    return False
        return True

    def auto_check_wrong_cells(self):
        if not self.auto_check_enabled:
            return

        self.wrong_cells.clear()
        for i in range(9):
            for j in range(9):
                if self.board[i][j] != 0 and self.board[i][j] != self.solved_board[i][j]:
                    self.wrong_cells.add((i, j))

    def draw(self):
        # Draw background
        screen.fill(WHITE)

        # Draw celebration if active
        if self.celebration.active:
            self.celebration.draw(screen)

        # Draw title
        title_text = font_large.render("🎯 AI SUDOKU - COMPLETE", True, BLUE)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 20))

        # Draw game board background
        board_width = self.cell_size * 9
        board_bg = pygame.Rect(self.board_start_x - 10, self.board_start_y - 10,
                               board_width + 20, board_width + 20)
        pygame.draw.rect(screen, LIGHT_GRAY, board_bg, border_radius=12)
        pygame.draw.rect(screen, DARK_GRAY, board_bg, 3, border_radius=12)

        # Draw grid
        for i in range(10):
            thickness = 3 if i % 3 == 0 else 1

            # Horizontal lines
            pygame.draw.line(screen, BLACK,
                             (self.board_start_x, self.board_start_y + i * self.cell_size),
                             (self.board_start_x + 9 * self.cell_size, self.board_start_y + i * self.cell_size),
                             thickness)
            # Vertical lines
            pygame.draw.line(screen, BLACK,
                             (self.board_start_x + i * self.cell_size, self.board_start_y),
                             (self.board_start_x + i * self.cell_size, self.board_start_y + 9 * self.cell_size),
                             thickness)

        # Draw numbers and wrong cell highlights
        for i in range(9):
            for j in range(9):
                x = self.board_start_x + j * self.cell_size
                y = self.board_start_y + i * self.cell_size

                # Highlight wrong cells if auto-check is enabled
                if self.auto_check_enabled and (i, j) in self.wrong_cells:
                    pygame.draw.rect(screen, (255, 200, 200), (x, y, self.cell_size, self.cell_size))

                if self.board[i][j] != 0:
                    # All numbers are black (editable)
                    num_text = font_medium.render(str(self.board[i][j]), True, BLACK)
                    text_rect = num_text.get_rect(center=(x + self.cell_size // 2, y + self.cell_size // 2))
                    screen.blit(num_text, text_rect)
                else:
                    # Draw dot in empty cells
                    pygame.draw.circle(screen, LIGHT_GRAY, (x + self.cell_size // 2, y + self.cell_size // 2), 3)

        # Highlight selected cell
        if self.selected:
            row, col = self.selected
            x = self.board_start_x + col * self.cell_size
            y = self.board_start_y + row * self.cell_size

            # Green highlight for all cells (all editable)
            pygame.draw.rect(screen, GREEN, (x, y, self.cell_size, self.cell_size), 3)

        # Draw buttons
        self.solve_button.draw(screen)
        self.hint_button.draw(screen)
        self.new_game_button.draw(screen)
        self.check_button.draw(screen)
        self.easy_button.draw(screen)
        self.medium_button.draw(screen)
        self.hard_button.draw(screen)
        self.auto_check_button.draw(screen)
        self.pause_button.draw(screen)

        # Draw game info
        self.draw_game_info()

        # Draw message
        if self.message and time.time() - self.message_time < 3:
            msg_text = font_small.render(self.message, True, RED)
            screen.blit(msg_text, (WIDTH // 2 - msg_text.get_width() // 2, 450))

        # Draw congratulations if game is won
        if self.game_won:
            congrats_text = font_large.render("🎉 CONGRATULATIONS! 🎉", True, GOLD)
            screen.blit(congrats_text, (WIDTH // 2 - congrats_text.get_width() // 2, 250))

            solved_text = font_medium.render("You solved the Sudoku!", True, GREEN)
            screen.blit(solved_text, (WIDTH // 2 - solved_text.get_width() // 2, 310))

        # Draw pause overlay
        if self.game_paused:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))

            pause_text = font_large.render("⏸️ GAME PAUSED", True, WHITE)
            screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - 50))

            continue_text = font_medium.render("Press P or click Resume to continue", True, YELLOW)
            screen.blit(continue_text, (WIDTH // 2 - continue_text.get_width() // 2, HEIGHT // 2 + 10))

    def draw_game_info(self):
        # Time with pause indicator
        time_color = RED if self.game_paused else DARK_BLUE
        time_text = font_tiny.render(f"⏰ {self.timer.get_formatted_time()}{' ⏸️' if self.game_paused else ''}", True,
                                     time_color)
        screen.blit(time_text, (30, 60))

        # Hints
        hints_text = font_tiny.render(f"💡 Hints: {self.hints_used}", True, DARK_BLUE)
        screen.blit(hints_text, (150, 60))

        # Mistakes
        mistakes_text = font_tiny.render(f"❌ Mistakes: {self.mistakes}", True, DARK_BLUE)
        screen.blit(mistakes_text, (270, 60))

        # Progress
        filled_cells = np.count_nonzero(self.board)
        progress_text = font_tiny.render(f"📊 Progress: {filled_cells}/81", True, DARK_BLUE)
        screen.blit(progress_text, (390, 60))

        # Instructions
        instr_text = font_tiny.render("Click ANY cell → Press 1-9 → All cells editable", True, DARK_GRAY)
        screen.blit(instr_text, (WIDTH // 2 - instr_text.get_width() // 2, HEIGHT - 25))

        # Selected cell info
        if self.selected and not self.game_paused:
            row, col = self.selected
            cell_info = font_tiny.render(f"Selected: ({row + 1}, {col + 1})", True, BLUE)
            screen.blit(cell_info, (480, 60))

    def select(self, pos):
        if self.game_paused:
            return False

        x, y = pos
        if (self.board_start_x <= x <= self.board_start_x + 9 * self.cell_size and
                self.board_start_y <= y <= self.board_start_y + 9 * self.cell_size):
            col = (x - self.board_start_x) // self.cell_size
            row = (y - self.board_start_y) // self.cell_size
            if 0 <= row < 9 and 0 <= col < 9:
                self.selected = (row, col)
                if self.board[row][col] == 0:
                    self.message = f"✅ Cell ({row + 1}, {col + 1}) selected - Press 1-9 to enter number"
                else:
                    self.message = f"✅ Cell ({row + 1}, {col + 1}) selected - Press 1-9 to change or 0 to clear"
                self.message_time = time.time()
                return True
        return False

    def place_number(self, num):
        if self.game_paused:
            self.message = "⏸️ Game is paused - Resume to play"
            self.message_time = time.time()
            return False

        if not self.selected:
            self.message = "⚠️ Please select a cell first!"
            self.message_time = time.time()
            return False

        row, col = self.selected

        # Place the number
        old_value = self.board[row][col]
        self.board[row][col] = num

        # Auto-check if enabled
        if self.auto_check_enabled:
            self.auto_check_wrong_cells()

        # Check if the number is correct
        if num == self.solved_board[row][col]:
            self.message = f"✅ {num} placed at ({row + 1}, {col + 1})"
            # Check if game is won
            if self.check_win():
                self.game_won = True
                self.celebration.start()
                self.message = "🎉 Congratulations! Puzzle Solved!"
        else:
            self.mistakes += 1
            self.message = f"❌ {num} at ({row + 1}, {col + 1}) is wrong"

        self.message_time = time.time()
        return True

    def clear_cell(self):
        if self.game_paused:
            self.message = "⏸️ Game is paused - Resume to play"
            self.message_time = time.time()
            return False

        if not self.selected:
            self.message = "⚠️ Please select a cell first!"
            self.message_time = time.time()
            return False

        row, col = self.selected

        if self.board[row][col] == 0:
            self.message = f"ℹ️ Cell ({row + 1}, {col + 1}) is already empty"
        else:
            self.board[row][col] = 0
            self.message = f"🧹 Cleared cell ({row + 1}, {col + 1})"

        # Auto-check if enabled
        if self.auto_check_enabled:
            self.auto_check_wrong_cells()

        self.message_time = time.time()
        return True

    def solve_with_ai(self):
        if self.game_paused:
            self.message = "⏸️ Game is paused - Resume to play"
            self.message_time = time.time()
            return

        self.board = self.solved_board.copy()
        self.message = "✅ Solved with AI!"
        self.game_won = True
        self.celebration.start()
        self.message_time = time.time()

    def provide_hint(self):
        if self.game_paused:
            self.message = "⏸️ Game is paused - Resume to play"
            self.message_time = time.time()
            return False

        if not self.selected:
            self.message = "⚠️ Please select a cell first!"
            self.message_time = time.time()
            return False

        row, col = self.selected

        if self.board[row][col] != 0:
            self.message = f"ℹ️ Cell already has number {self.board[row][col]}"
            self.message_time = time.time()
            return False

        correct_num = self.solved_board[row][col]
        self.board[row][col] = correct_num
        self.hints_used += 1
        self.message = f"💡 Hint: {correct_num} placed at ({row + 1}, {col + 1})"
        self.message_time = time.time()

        # Auto-check if enabled
        if self.auto_check_enabled:
            self.auto_check_wrong_cells()

        # Check if game is won after hint
        if self.check_win():
            self.game_won = True
            self.celebration.start()
        return True

    def check_solution(self):
        if self.game_paused:
            self.message = "⏸️ Game is paused - Resume to play"
            self.message_time = time.time()
            return

        if self.check_win():
            self.message = "🎉 Perfect! Puzzle completely solved!"
            self.game_won = True
            self.celebration.start()
        else:
            # Count correct cells
            correct = 0
            total_filled = 0
            for i in range(9):
                for j in range(9):
                    if self.board[i][j] != 0:
                        total_filled += 1
                        if self.board[i][j] == self.solved_board[i][j]:
                            correct += 1

            if total_filled == 0:
                self.message = "ℹ️ No numbers entered yet!"
            else:
                self.message = f"📊 Progress: {correct}/{total_filled} correct"

        self.message_time = time.time()

    def toggle_auto_check(self):
        self.auto_check_enabled = not self.auto_check_enabled
        self.auto_check_button.text = f"Auto-Check: {'ON' if self.auto_check_enabled else 'OFF'}"
        if self.auto_check_enabled:
            self.auto_check_wrong_cells()
            self.message = "🔍 Auto-Check enabled - Wrong cells highlighted in red"
        else:
            self.wrong_cells.clear()
            self.message = "🔍 Auto-Check disabled"
        self.message_time = time.time()

    def toggle_pause(self):
        self.game_paused = not self.game_paused
        if self.game_paused:
            self.timer.pause()
            self.pause_button.text = "Resume"
            self.message = "⏸️ Game paused"
        else:
            self.timer.resume()
            self.pause_button.text = "Pause"
            self.message = "▶️ Game resumed"
        self.message_time = time.time()

    def check_button_click(self, pos):
        if self.game_paused and not self.pause_button.rect.collidepoint(pos):
            self.message = "⏸️ Game is paused - Click Resume first"
            self.message_time = time.time()
            return False

        if self.solve_button.is_hovered(pos):
            self.solve_with_ai()
        elif self.hint_button.is_hovered(pos):
            self.provide_hint()
        elif self.new_game_button.is_hovered(pos):
            self.new_game(self.current_difficulty)
        elif self.check_button.is_hovered(pos):
            self.check_solution()
        elif self.easy_button.is_hovered(pos):
            self.new_game(0.3)
        elif self.medium_button.is_hovered(pos):
            self.new_game(0.5)
        elif self.hard_button.is_hovered(pos):
            self.new_game(0.7)
        elif self.auto_check_button.is_hovered(pos):
            self.toggle_auto_check()
        elif self.pause_button.is_hovered(pos):
            self.toggle_pause()
        else:
            return self.select(pos)
        return False

    def update(self):
        if self.celebration.active:
            return self.celebration.update()
        return True

    def handle_keyboard(self, event):
        if event.key == pygame.K_p:
            self.toggle_pause()
            return True
        elif event.key == pygame.K_a:
            self.toggle_auto_check()
            return True
        elif event.key == pygame.K_c:
            if not self.game_paused:
                self.check_solution()
            return True
        elif event.key == pygame.K_h:
            if not self.game_paused:
                self.provide_hint()
            return True
        elif event.key == pygame.K_n:
            self.new_game(self.current_difficulty)
            return True
        elif event.key == pygame.K_s:
            if not self.game_paused:
                self.solve_with_ai()
            return True
        return False


def main():
    game = SudokuGame()
    clock = pygame.time.Clock()
    running = True

    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    game.check_button_click(mouse_pos)

            if event.type == pygame.KEYDOWN:
                # Handle special keys first
                if not game.handle_keyboard(event):
                    # Handle number keys
                    if not game.game_paused:
                        if event.key == pygame.K_1:
                            game.place_number(1)
                        elif event.key == pygame.K_2:
                            game.place_number(2)
                        elif event.key == pygame.K_3:
                            game.place_number(3)
                        elif event.key == pygame.K_4:
                            game.place_number(4)
                        elif event.key == pygame.K_5:
                            game.place_number(5)
                        elif event.key == pygame.K_6:
                            game.place_number(6)
                        elif event.key == pygame.K_7:
                            game.place_number(7)
                        elif event.key == pygame.K_8:
                            game.place_number(8)
                        elif event.key == pygame.K_9:
                            game.place_number(9)
                        elif event.key == pygame.K_0 or event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                            game.clear_cell()
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Update button hover states
        if not game.game_paused:
            game.solve_button.is_hovered(mouse_pos)
            game.hint_button.is_hovered(mouse_pos)
            game.new_game_button.is_hovered(mouse_pos)
            game.check_button.is_hovered(mouse_pos)
            game.easy_button.is_hovered(mouse_pos)
            game.medium_button.is_hovered(mouse_pos)
            game.hard_button.is_hovered(mouse_pos)
        game.auto_check_button.is_hovered(mouse_pos)
        game.pause_button.is_hovered(mouse_pos)

        # Update game state
        game.update()

        game.draw()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()