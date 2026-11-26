import pygame
import random
import time
import copy

# --- Config ---
pygame.init()
WIDTH, HEIGHT = 540, 650
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku")

WHITE, BLACK, GRAY = (255, 255, 255), (0, 0, 0), (128, 128, 128)
BLUE, RED, GREEN = (50, 120, 240), (220, 20, 60), (34, 139, 34)
BG_COLOR = (245, 245, 245)

FONT = pygame.font.SysFont("arial", 35, bold=True)
UI_FONT = pygame.font.SysFont("arial", 20, bold=True)
VICTORY_FONT = pygame.font.SysFont("arial", 70, bold=True)

# --- Sudoku Logic ---
def is_valid(board, num, pos):
    for j in range(9):
        if board[pos[0]][j] == num and pos[1] != j: return False
    for i in range(9):
        if board[i][pos[1]] == num and pos[0] != i: return False
    bx, by = pos[1] // 3, pos[0] // 3
    for i in range(by*3, by*3 + 3):
        for j in range(bx*3, bx*3 + 3):
            if board[i][j] == num and (i, j) != pos: return False
    return True

def find_empty(board):
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0: return (i, j)
    return None

def solve(board):
    find = find_empty(board)
    if not find: return True
    r, c = find
    for i in random.sample(range(1, 10), 9):
        if is_valid(board, i, (r, c)):
            board[r][c] = i
            if solve(board): return True
            board[r][c] = 0
    return False

def generate_level(difficulty):
    board = [[0 for _ in range(9)] for _ in range(9)]
    solve(board)
    solution = copy.deepcopy(board)
    counts = {"Easy": 20, "Medium": 40, "Hard": 55}
    attempts = counts.get(difficulty, 40)
    while attempts > 0:
        r, c = random.randint(0, 8), random.randint(0, 8)
        if board[r][c] != 0:
            board[r][c] = 0
            attempts -= 1
    return board, solution

# --- GUI ---
class Cube:
    def __init__(self, val, r, c):
        self.value = val
        self.row, self.col = r, c
        self.selected = False
        self.fixed = True if val != 0 else False

    def draw(self, screen, is_wrong):
        gap = 540 / 9
        x, y = self.col * gap, self.row * gap
        if self.selected:
            pygame.draw.rect(screen, BLUE, (x, y, gap, gap), 4) # Thicker highlight
        if self.value != 0:
            color = RED if is_wrong else (BLACK if self.fixed else GRAY)
            txt = FONT.render(str(self.value), 1, color)
            screen.blit(txt, (x + (gap/2 - txt.get_width()/2), y + (gap/2 - txt.get_height()/2)))

class Grid:
    def __init__(self, difficulty):
        self.vals, self.solution = generate_level(difficulty)
        self.cubes = [[Cube(self.vals[i][j], i, j) for j in range(9)] for i in range(9)]
        self.selected_pos = None # Track as (row, col)
        self.check_mode = False

    def select(self, r, c):
        # Reset all selections
        for row in self.cubes:
            for cube in row:
                cube.selected = False
        # Set new selection
        self.cubes[r][c].selected = True
        self.selected_pos = (r, c)

    def draw(self, screen):
        gap = 540 / 9
        for i in range(10):
            thick = 4 if i % 3 == 0 else 1
            pygame.draw.line(screen, BLACK, (0, i * gap), (540, i * gap), thick)
            pygame.draw.line(screen, BLACK, (i * gap, 0), (i * gap, 540), thick)
        for i in range(9):
            for j in range(9):
                is_wrong = False
                if self.check_mode and self.cubes[i][j].value != 0:
                    if self.cubes[i][j].value != self.solution[i][j]:
                        is_wrong = True
                self.cubes[i][j].draw(screen, is_wrong)

    def is_finished(self):
        for i in range(9):
            for j in range(9):
                if self.cubes[i][j].value != self.solution[i][j]: return False
        return True

# --- Main Functions ---
def main_menu():
    while True:
        SCREEN.fill(BG_COLOR)
        title = FONT.render("SUDOKU", 1, BLACK)
        SCREEN.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        btns = []
        for i, level in enumerate(["Easy", "Medium", "Hard"]):
            rect = pygame.Rect(WIDTH//2 - 100, 220 + i*80, 200, 50)
            pygame.draw.rect(SCREEN, BLUE, rect, border_radius=10)
            txt = UI_FONT.render(level, 1, WHITE)
            SCREEN.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))
            btns.append((rect, level))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"
            if event.type == pygame.MOUSEBUTTONDOWN:
                for rect, level in btns:
                    if rect.collidepoint(event.pos): return level

def play_game(difficulty):
    grid = Grid(difficulty)
    run, won = True, False
    start_time = time.time()
    
    # Define Button Rects for global hit detection
    hint_btn = pygame.Rect(50, 570, 120, 40)
    check_btn = pygame.Rect(210, 570, 120, 40)
    menu_btn_rect = pygame.Rect(WIDTH//2 - 100, 350, 200, 50) # Defined once here
    
    while run:
        if not won: passed_time = round(time.time() - start_time)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                
                # Check for win button click specifically when won is True
                if won:
                    if menu_btn_rect.collidepoint(pos): 
                        return "MENU"
                
                # Normal gameplay clicks
                elif pos[1] < 540:
                    r, c = int(pos[1]//(540/9)), int(pos[0]//(540/9))
                    grid.select(r, c)
                elif hint_btn.collidepoint(pos) and not won:
                    if grid.selected_pos:
                        r, c = grid.selected_pos
                        if not grid.cubes[r][c].fixed:
                            grid.cubes[r][c].value = grid.solution[r][c]
                elif check_btn.collidepoint(pos) and not won:
                    grid.check_mode = not grid.check_mode

            if not won and event.type == pygame.KEYDOWN:
                if grid.selected_pos:
                    r, c = grid.selected_pos
                    if not grid.cubes[r][c].fixed:
                        if pygame.K_1 <= event.key <= pygame.K_9: grid.cubes[r][c].value = event.key - 48
                        if event.key in [pygame.K_BACKSPACE, pygame.K_DELETE, pygame.K_0]: grid.cubes[r][c].value = 0
                if event.key == pygame.K_c: grid.check_mode = not grid.check_mode
                if event.key == pygame.K_h and grid.selected_pos:
                    r, c = grid.selected_pos
                    if not grid.cubes[r][c].fixed: grid.cubes[r][c].value = grid.solution[r][c]

        SCREEN.fill(WHITE)
        grid.draw(SCREEN)
        
        # Draw UI
        pygame.draw.rect(SCREEN, GREEN, hint_btn, border_radius=5)
        pygame.draw.rect(SCREEN, BLUE, check_btn, border_radius=5)
        SCREEN.blit(UI_FONT.render("HINT (H)", 1, WHITE), (72, 580))
        SCREEN.blit(UI_FONT.render("CHECK (C)", 1, WHITE), (225, 580))
        
        timer_txt = UI_FONT.render(f"Time: {passed_time//60:02d}:{passed_time%60:02d}", 1, BLACK)
        SCREEN.blit(timer_txt, (380, 580))
        
        if grid.check_mode and not won:
            SCREEN.blit(UI_FONT.render("CHECK ON", 1, RED), (WIDTH//2 - 45, 545))

        if not won and grid.is_finished(): won = True
            
        if won:
            overlay = pygame.Surface((540, 540)); overlay.set_alpha(210); overlay.fill(WHITE)
            SCREEN.blit(overlay, (0, 0))
            v_msg = VICTORY_FONT.render("VICTORY!", 1, GREEN)
            SCREEN.blit(v_msg, (WIDTH//2 - v_msg.get_width()//2, 180))
            
            # Use the consistent menu_btn_rect for drawing
            pygame.draw.rect(SCREEN, BLUE, menu_btn_rect, border_radius=10)
            txt = UI_FONT.render("MAIN MENU", 1, WHITE)
            SCREEN.blit(txt, (menu_btn_rect.centerx - txt.get_width()//2, menu_btn_rect.centery - txt.get_height()//2))

        pygame.display.update()

def main():
    while True:
        choice = main_menu()
        if choice == "QUIT": break
        result = play_game(choice)
        if result == "QUIT": break

if __name__ == "__main__":
    main()
    pygame.quit()
