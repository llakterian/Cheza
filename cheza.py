import pygame
import random
import time
import sys
import os

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Add this function near the top of your code
def create_default_icon():
    icon_surface = pygame.Surface((64, 64))
    icon_surface.fill((0, 0, 0))  # Black background
    
    # Draw simple Tetris blocks
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
    for i, color in enumerate(colors):
        pygame.draw.rect(icon_surface, color, (i*16, i*16, 16, 16))
    
    return icon_surface

# The icon loading code:
try:
    icon = pygame.image.load('assets/cheza_icon.png')
    pygame.display.set_icon(icon)
except:
    print("Using generated icon")
    icon = create_default_icon()
    pygame.display.set_icon(icon)

# Constants 
SCREEN_WIDTH = 400  # Reduced from 800 to fit the grid better
SCREEN_HEIGHT = 600  # This should show the full grid now
GRID_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SIDEBAR_WIDTH = 100  # Reduced sidebar width

# screen initialization to allow resizing
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Cheza - Tetris for Kids")

# function to handle window resizing
def handle_resize(event):
    global SCREEN_WIDTH, SCREEN_HEIGHT, screen
    SCREEN_WIDTH = event.w
    SCREEN_HEIGHT = event.h
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)

# event handler
for event in pygame.event.get():
    if event.type == pygame.QUIT:
        run = False
        pygame.quit()
        sys.exit()
    elif event.type == pygame.VIDEORESIZE:
        handle_resize(event)
    
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
COLORS = [
    (0, 255, 255),    # Cyan - I
    (0, 0, 255),      # Blue - J
    (255, 165, 0),    # Orange - L
    (255, 255, 0),    # Yellow - O
    (0, 255, 0),      # Green - S
    (128, 0, 128),    # Purple - T
    (255, 0, 0)       # Red - Z
]

# Tetrimino shapes
SHAPES = [
    [[1, 1, 1, 1]],   # I
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]],  # L
    [[1, 1], [1, 1]],        # O
    [[0, 1, 1], [1, 1, 0]],  # S
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 1, 0], [0, 1, 1]]   # Z
]

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cheza - Tetris for Kids")

# Clock for controlling game speed
clock = pygame.time.Clock()

# Fonts
font_small = pygame.font.SysFont('comicsans', 25)
font_medium = pygame.font.SysFont('comicsans', 35)
font_large = pygame.font.SysFont('comicsans', 50)

# Sound effects (we'll handle cases where files don't exist)
try:
    move_sound = pygame.mixer.Sound('sounds/move.wav')
    rotate_sound = pygame.mixer.Sound('sounds/rotate.wav')
    clear_sound = pygame.mixer.Sound('sounds/clear.wav')
    game_over_sound = pygame.mixer.Sound('sounds/gameover.wav')
except:
    # Create silent sounds if files don't exist
    move_sound = pygame.mixer.Sound(buffer=bytearray(0))
    rotate_sound = pygame.mixer.Sound(buffer=bytearray(0))
    clear_sound = pygame.mixer.Sound(buffer=bytearray(0))
    game_over_sound = pygame.mixer.Sound(buffer=bytearray(0))

class Tetrimino:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = COLORS[SHAPES.index(shape)]
        self.rotation = 0

    def rotate(self):
        self.rotation = (self.rotation + 1) % 4
        # Transpose and reverse rows to rotate 90 degrees
        self.shape = [list(row) for row in zip(*self.shape[::-1])]
        rotate_sound.play()

def create_grid(locked_positions={}):
    grid = [[(0, 0, 0) for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if (x, y) in locked_positions:
                grid[y][x] = locked_positions[(x, y)]
    
    return grid

def draw_grid(surface, grid):
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            pygame.draw.rect(surface, grid[y][x], 
                            (x * GRID_SIZE + (SCREEN_WIDTH - GRID_WIDTH * GRID_SIZE) // 2, 
                             y * GRID_SIZE + 50, 
                             GRID_SIZE, GRID_SIZE), 0)
    
    # Draw grid lines
    for y in range(GRID_HEIGHT + 1):
        pygame.draw.line(surface, GRAY, 
                        ((SCREEN_WIDTH - GRID_WIDTH * GRID_SIZE) // 2, y * GRID_SIZE + 50),
                        ((SCREEN_WIDTH + GRID_WIDTH * GRID_SIZE) // 2, y * GRID_SIZE + 50))
    
    for x in range(GRID_WIDTH + 1):
        pygame.draw.line(surface, GRAY, 
                        ((SCREEN_WIDTH - GRID_WIDTH * GRID_SIZE) // 2 + x * GRID_SIZE, 50),
                        ((SCREEN_WIDTH - GRID_WIDTH * GRID_SIZE) // 2 + x * GRID_SIZE, 
                         GRID_HEIGHT * GRID_SIZE + 50))

def draw_window(surface, grid, score, level, next_piece):
    surface.fill(BLACK)
    
    # Calculate dynamic positions based on window size
    grid_x = (SCREEN_WIDTH - GRID_WIDTH * GRID_SIZE) // 2
    if grid_x < 10:  # Minimum margin
        grid_x = 10
    
    # Draw title
    title = font_large.render("CHEZA", 1, WHITE)
    surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 5))
    
    # Draw score and level with dynamic positioning
    score_text = font_medium.render(f"Score: {score}", 1, WHITE)
    level_text = font_medium.render(f"Level: {level}", 1, WHITE)
    
    surface.blit(score_text, (10, 50))
    surface.blit(level_text, (10, 90))
    
    # Draw next piece preview
    next_text = font_medium.render("Next:", 1, WHITE)
    surface.blit(next_text, (SCREEN_WIDTH - 110, 50))
    
    # Draw next piece
    if next_piece:
        for y, row in enumerate(next_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(surface, next_piece.color, 
                                    (SCREEN_WIDTH - 110 + x * GRID_SIZE, 
                                     90 + y * GRID_SIZE, 
                                     GRID_SIZE, GRID_SIZE), 0)
    
    # Draw grid with dynamic positioning
    draw_grid(surface, grid, grid_x)
    
    # Draw border around play area
    border_rect = pygame.Rect(grid_x - 2, 
                             50 - 2, 
                             GRID_WIDTH * GRID_SIZE + 4, 
                             GRID_HEIGHT * GRID_SIZE + 4)
    pygame.draw.rect(surface, WHITE, border_rect, 2)

def draw_grid(surface, grid, grid_x):
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            pygame.draw.rect(surface, grid[y][x], 
                           (grid_x + x * GRID_SIZE, 
                            y * GRID_SIZE + 50, 
                            GRID_SIZE, GRID_SIZE), 0)
    
    # Draw grid lines
    for y in range(GRID_HEIGHT + 1):
        pygame.draw.line(surface, GRAY, 
                        (grid_x, y * GRID_SIZE + 50),
                        (grid_x + GRID_WIDTH * GRID_SIZE, y * GRID_SIZE + 50))
    
    for x in range(GRID_WIDTH + 1):
        pygame.draw.line(surface, GRAY, 
                        (grid_x + x * GRID_SIZE, 50),
                        (grid_x + x * GRID_SIZE, GRID_HEIGHT * GRID_SIZE + 50)) 
    
    # Draw border around play area
    border_rect = pygame.Rect((SCREEN_WIDTH - GRID_WIDTH * GRID_SIZE) // 2 - 2, 
                             50 - 2, 
                             GRID_WIDTH * GRID_SIZE + 4, 
                             GRID_HEIGHT * GRID_SIZE + 4)
    pygame.draw.rect(surface, WHITE, border_rect, 2)

def valid_space(shape, grid):
    accepted_pos = [[(x, y) for x in range(GRID_WIDTH) if grid[y][x] == (0, 0, 0)] for y in range(GRID_HEIGHT)]
    accepted_pos = [x for sub in accepted_pos for x in sub]
    
    formatted = convert_shape_format(shape)
    
    for pos in formatted:
        if pos not in accepted_pos:
            if pos[1] > -1:
                return False
    return True

def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False

def convert_shape_format(shape):
    positions = []
    shape_format = shape.shape
    
    for y, line in enumerate(shape_format):
        for x, cell in enumerate(line):
            if cell:
                positions.append((shape.x + x, shape.y + y))
    
    return positions

def clear_rows(grid, locked):
    inc = 0
    for y in range(len(grid)-1, -1, -1):
        row = grid[y]
        if (0, 0, 0) not in row:
            inc += 1
            clear_sound.play()
            for x in range(len(row)):
                try:
                    del locked[(x, y)]
                except:
                    continue
    
    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < 0:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)
    
    return inc

def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, 1, color)
    
    surface.blit(label, (SCREEN_WIDTH // 2 - label.get_width() // 2, 
                        SCREEN_HEIGHT // 2 - label.get_height() // 2))

def get_shape():
    return Tetrimino(5, 0, random.choice(SHAPES))

def main():
    locked_positions = {}
    grid = create_grid(locked_positions)
    
    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.5  # seconds
    level_time = 0
    score = 0
    level = 1
    
    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()
        
        # Increase level every 30 seconds
        if level_time / 1000 > 30:
            level_time = 0
            if level < 10:  # Max level
                level += 1
                fall_speed *= 0.8  # Increase speed
        
        # Piece falling
        if fall_time / 1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                    else:
                        move_sound.play()
                
                if event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                    else:
                        move_sound.play()
                
                if event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                    else:
                        move_sound.play()
                
                if event.key == pygame.K_UP:
                    current_piece.rotate()
                    if not valid_space(current_piece, grid):
                        current_piece.rotation -= 1
                        current_piece.rotation %= 4
                        current_piece.shape = SHAPES[SHAPES.index(current_piece.shape)]
                
                if event.key == pygame.K_SPACE:
                    while valid_space(current_piece, grid):
                        current_piece.y += 1
                        move_sound.play()
                    current_piece.y -= 1
        
        shape_pos = convert_shape_format(current_piece)
        
        # Color the grid with current piece
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color
        
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            score += clear_rows(grid, locked_positions) * 10 * level
        
        draw_window(screen, grid, score, level, next_piece)
        pygame.display.update()
        
        if check_lost(locked_positions):
            game_over_sound.play()
            draw_text_middle(screen, "GAME OVER!", 80, WHITE)
            pygame.display.update()
            pygame.time.delay(2000)
            run = False

def main_menu():
    run = True
    while run:
        screen.fill(BLACK)
        draw_text_middle(screen, "Press Any Key To Play", 60, WHITE)
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                main()
    
    pygame.quit()

if __name__ == "__main__":
    # Create sounds directory if it doesn't exist
    if not os.path.exists('sounds'):
        os.makedirs('sounds')
    
    main_menu()