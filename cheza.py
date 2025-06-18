import pygame
import random
import json

# Constants
GRID_WIDTH, GRID_HEIGHT = 10, 20
BLOCK_SIZE = 30
SCREEN_WIDTH = GRID_WIDTH * BLOCK_SIZE + 200
SCREEN_HEIGHT = GRID_HEIGHT * BLOCK_SIZE
GRID_COLOR = (40, 40, 40)
BACKGROUND_COLOR = (20, 20, 20)

# Tetrimino colors and shapes
COLORS = [
    (0, 240, 240),   # I - Cyan
    (0, 0, 240),     # J - Blue
    (240, 160, 0),   # L - Orange
    (240, 240, 0),   # O - Yellow
    (0, 240, 0),     # S - Green
    (160, 0, 240),   # T - Purple
    (240, 0, 0)      # Z - Red
]

SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]],  # L
    [[1, 1], [1, 1]],  # O
    [[0, 1, 1], [1, 1, 0]],  # S
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 1, 0], [0, 1, 1]]   # Z
]

class Tetrimino:
    def __init__(self):
        self.shape_idx = random.randint(0, len(SHAPES)-1)
        self.shape = SHAPES[self.shape_idx]
        self.color = COLORS[self.shape_idx]
        self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0
        self.rotation = 0
    
    def rotate(self):
        # Matrix rotation (90 degrees clockwise)
        return [list(row)[::-1] for row in zip(*self.shape)]
    
    def valid_position(self, shape, x, y, grid):
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    if (x + j < 0 or x + j >= GRID_WIDTH or 
                        y + i >= GRID_HEIGHT or 
                        (y + i >= 0 and grid[y + i][x + j])):
                        return False
        return True

class TetrisGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24, bold=True)
        self.reset_game()
    
    def reset_game(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.held_piece = None
        self.can_hold = True
        self.score = 0
        self.level = 1
        self.lines = 0
        self.game_over = False
        self.paused = False
        self.fall_time = 0
        self.fall_speed = self.get_fall_speed()
    
    def new_piece(self):
        return Tetrimino()
    
    def get_fall_speed(self):
        # Speed increases every 10 lines
        return max(100, 800 - (self.level - 1) * 50)
    
    def draw_block(self, x, y, color):
        rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, (255, 255, 255), rect, 1)
    
    def draw_grid(self):
        # Draw grid background
        pygame.draw.rect(self.screen, GRID_COLOR, 
                        (0, 0, GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE))
        
        # Draw grid lines
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(self.screen, (60, 60, 60), 
                           (x * BLOCK_SIZE, 0), 
                           (x * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE), 1)
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(self.screen, (60, 60, 60), 
                           (0, y * BLOCK_SIZE), 
                           (GRID_WIDTH * BLOCK_SIZE, y * BLOCK_SIZE), 1)
        
        # Draw placed blocks
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x]:
                    self.draw_block(x, y, COLORS[self.grid[y][x]-1])
    
    def draw_piece(self, piece):
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    self.draw_block(piece.x + x, piece.y + y, piece.color)
    
    def draw_ui(self):
        # Side panel background
        pygame.draw.rect(self.screen, (30, 30, 30), 
                       (GRID_WIDTH * BLOCK_SIZE, 0, 
                        SCREEN_WIDTH - GRID_WIDTH * BLOCK_SIZE, SCREEN_HEIGHT))
        
        # Score
        self.draw_text(f"SCORE: {self.score}", (GRID_WIDTH * BLOCK_SIZE + 20, 20))
        
        # Level
        self.draw_text(f"LEVEL: {self.level}", (GRID_WIDTH * BLOCK_SIZE + 20, 60))
        
        # Lines
        self.draw_text(f"LINES: {self.lines}", (GRID_WIDTH * BLOCK_SIZE + 20, 100))
        
        # Next piece
        self.draw_text("NEXT:", (GRID_WIDTH * BLOCK_SIZE + 20, 160))
        self.draw_piece_preview(self.next_piece, GRID_WIDTH * BLOCK_SIZE + 40, 200)
        
        # Hold piece
        self.draw_text("HOLD:", (GRID_WIDTH * BLOCK_SIZE + 20, 300))
        if self.held_piece:
            self.draw_piece_preview(self.held_piece, GRID_WIDTH * BLOCK_SIZE + 40, 340)
        
        # Controls
        controls = [
            "CONTROLS:",
            "← → ↓ - Move",
            "↑ - Rotate",
            "Space - Hard Drop",
            "C - Hold",
            "P - Pause",
            "R - Restart"
        ]
        for i, text in enumerate(controls):
            self.draw_text(text, (GRID_WIDTH * BLOCK_SIZE + 20, 420 + i * 30), size=18)
    
    def draw_piece_preview(self, piece, x, y):
        for py, row in enumerate(piece.shape):
            for px, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, piece.color,
                                   (x + px * 20, y + py * 20, 20, 20))
                    pygame.draw.rect(self.screen, (255, 255, 255),
                                   (x + px * 20, y + py * 20, 20, 20), 1)
    
    def draw_text(self, text, pos, color=(255, 255, 255), size=24):
        font = pygame.font.SysFont('Arial', size, bold=True)
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, pos)
    
    def clear_lines(self):
        lines_cleared = 0
        new_grid = []
        
        for row in self.grid:
            if all(row):
                lines_cleared += 1
            else:
                new_grid.append(row)
        
        # Add new empty lines at the top
        new_grid = [[0]*GRID_WIDTH for _ in range(lines_cleared)] + new_grid
        self.grid = new_grid
        
        if lines_cleared > 0:
            self.lines += lines_cleared
            # Adjusted scoring system (more reasonable points)
            scores = {1: 40, 2: 100, 3: 300, 4: 500}
            self.score += scores.get(lines_cleared, 0)
            
            # Level up every 10 lines
            self.level = self.lines // 10 + 1
            self.fall_speed = self.get_fall_speed()
    
    def hold_piece(self):
        if not self.can_hold:
            return
        
        if self.held_piece is None:
            self.held_piece = Tetrimino()
            self.held_piece.shape_idx = self.current_piece.shape_idx
            self.held_piece.color = self.current_piece.color
            self.held_piece.shape = self.current_piece.shape
            self.current_piece = self.next_piece
            self.next_piece = self.new_piece()
        else:
            # Swap current and held pieces
            self.current_piece, self.held_piece = self.held_piece, self.current_piece
            self.current_piece.x = GRID_WIDTH // 2 - len(self.current_piece.shape[0]) // 2
            self.current_piece.y = 0
        
        self.can_hold = False
    
    def hard_drop(self):
        while self.current_piece.valid_position(
            self.current_piece.shape,
            self.current_piece.x,
            self.current_piece.y + 1,
            self.grid
        ):
            self.current_piece.y += 1
            self.score += 1  # Reduced bonus for hard drop
        
        self.lock_piece()
    
    def lock_piece(self):
        # Place the piece on the grid
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell and 0 <= self.current_piece.y + y < GRID_HEIGHT:
                    self.grid[self.current_piece.y + y][self.current_piece.x + x] = self.current_piece.shape_idx + 1
        
        self.clear_lines()
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        self.can_hold = True
        
        # Check for game over
        if not self.current_piece.valid_position(
            self.current_piece.shape,
            self.current_piece.x,
            self.current_piece.y,
            self.grid
        ):
            self.game_over = True
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and not self.paused:
                    if self.current_piece.valid_position(
                        self.current_piece.shape,
                        self.current_piece.x - 1,
                        self.current_piece.y,
                        self.grid
                    ):
                        self.current_piece.x -= 1
                
                elif event.key == pygame.K_RIGHT and not self.paused:
                    if self.current_piece.valid_position(
                        self.current_piece.shape,
                        self.current_piece.x + 1,
                        self.current_piece.y,
                        self.grid
                    ):
                        self.current_piece.x += 1
                
                elif event.key == pygame.K_DOWN and not self.paused:
                    if self.current_piece.valid_position(
                        self.current_piece.shape,
                        self.current_piece.x,
                        self.current_piece.y + 1,
                        self.grid
                    ):
                        self.current_piece.y += 1
                        self.score += 0.5  # Small bonus for soft drop
                
                elif event.key == pygame.K_UP and not self.paused:
                    rotated = self.current_piece.rotate()
                    if self.current_piece.valid_position(
                        rotated,
                        self.current_piece.x,
                        self.current_piece.y,
                        self.grid
                    ):
                        self.current_piece.shape = rotated
                
                elif event.key == pygame.K_SPACE and not self.paused:
                    self.hard_drop()
                
                elif event.key == pygame.K_c and not self.paused:
                    self.hold_piece()
                
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
                
                elif event.key == pygame.K_r and (self.game_over or self.paused):
                    self.reset_game()
        
        return True
    
    def update(self, dt):
        if self.game_over or self.paused:
            return
        
        self.fall_time += dt
        if self.fall_time >= self.fall_speed:
            self.fall_time = 0
            if self.current_piece.valid_position(
                self.current_piece.shape,
                self.current_piece.x,
                self.current_piece.y + 1,
                self.grid
            ):
                self.current_piece.y += 1
            else:
                self.lock_piece()
    
    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        self.draw_text("GAME OVER", (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 40), size=48)
        self.draw_text(f"FINAL SCORE: {int(self.score)}", (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 20))
        self.draw_text("Press R to restart", (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 60))
    
    def draw_pause(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        self.draw_text("PAUSED", (SCREEN_WIDTH//2 - 80, SCREEN_HEIGHT//2 - 20), size=48)
        self.draw_text("Press P to continue", (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 40))
    
    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60)
            
            running = self.handle_input()
            self.update(dt)
            
            # Drawing
            self.screen.fill(BACKGROUND_COLOR)
            self.draw_grid()
            
            # Draw current piece
            if not self.game_over and not self.paused:
                self.draw_piece(self.current_piece)
            
            self.draw_ui()
            
            if self.game_over:
                self.draw_game_over()
            elif self.paused:
                self.draw_pause()
            
            pygame.display.flip()

if __name__ == "__main__":
    game = TetrisGame()
    game.run()
    pygame.quit()