import pygame
import random
import sys
import os

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Game constants
GRID_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
MIN_WINDOW_WIDTH = 400
MIN_WINDOW_HEIGHT = 600
INITIAL_WINDOW_WIDTH = 500
INITIAL_WINDOW_HEIGHT = 700

# Colors
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

class Game:
    def __init__(self):
        self.reset_game()
        self.setup_window()
        self.load_assets()
        
    def reset_game(self):
        self.locked_positions = {}
        self.grid = self.create_grid()
        self.change_piece = False
        self.current_piece = self.get_shape()
        self.next_piece = self.get_shape()
        self.score = 0
        self.level = 1
        self.fall_time = 0
        self.level_time = 0
        self.fall_speed = 0.5
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False
        
    def setup_window(self):
        """Initialize the game window with proper settings"""
        self.screen = pygame.display.set_mode(
            (INITIAL_WINDOW_WIDTH, INITIAL_WINDOW_HEIGHT), 
            pygame.RESIZABLE | pygame.DOUBLEBUF
        )
        pygame.display.set_caption("Cheza - Tetris for Kids")
        
        # Create default icon if none exists
        try:
            icon = pygame.image.load('assets/cheza_icon.png')
            pygame.display.set_icon(icon)
        except:
            self.create_default_icon()
    
    def create_default_icon(self):
        """Create a simple programmatic icon"""
        icon_surface = pygame.Surface((64, 64))
        icon_surface.fill(BLACK)
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
        for i, color in enumerate(colors):
            pygame.draw.rect(icon_surface, color, (i*16, i*16, 16, 16))
        pygame.display.set_icon(icon_surface)
    
    def load_assets(self):
        """Load game assets with proper error handling"""
        # Create assets directory if it doesn't exist
        if not os.path.exists('assets'):
            os.makedirs('assets')
        
        # Create sounds directory if it doesn't exist
        if not os.path.exists('sounds'):
            os.makedirs('sounds')
        
        # Initialize sound effects with silent fallbacks
        self.sounds = {
            'move': self.load_sound('sounds/move.wav'),
            'rotate': self.load_sound('sounds/rotate.wav'),
            'clear': self.load_sound('sounds/clear.wav'),
            'game_over': self.load_sound('sounds/gameover.wav')
        }
        
        # Initialize fonts
        self.fonts = {
            'small': pygame.font.SysFont('comicsans', 25),
            'medium': pygame.font.SysFont('comicsans', 35),
            'large': pygame.font.SysFont('comicsans', 50)
        }
    
    def load_sound(self, path):
        """Load a sound file with silent fallback"""
        try:
            return pygame.mixer.Sound(path)
        except:
            # Return silent sound if file not found
            return pygame.mixer.Sound(buffer=bytearray(0))
    
    def handle_events(self):
        """Handle all pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.VIDEORESIZE:
                # Ensure minimum window size
                width = max(event.w, MIN_WINDOW_WIDTH)
                height = max(event.h, MIN_WINDOW_HEIGHT)
                self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
            
            elif event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_RETURN:
                        self.reset_game()
                        self.game_over = False
                
                elif not self.game_over:
                    if event.key == pygame.K_LEFT:
                        self.move_piece(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.move_piece(1, 0)
                    elif event.key == pygame.K_DOWN:
                        self.move_piece(0, 1)
                    elif event.key == pygame.K_UP:
                        self.rotate_piece()
                    elif event.key == pygame.K_SPACE:
                        self.hard_drop()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
    
    def move_piece(self, dx, dy):
        """Move the current piece with collision detection"""
        self.current_piece.x += dx
        self.current_piece.y += dy
        
        if not self.valid_space(self.current_piece):
            self.current_piece.x -= dx
            self.current_piece.y -= dy
        else:
            if dx != 0 or dy != 0:  # Don't play sound for rotation
                self.sounds['move'].play()
    
    def rotate_piece(self):
        """Rotate the current piece with collision detection"""
        original_shape = self.current_piece.shape
        # Transpose and reverse rows to rotate 90 degrees
        self.current_piece.shape = [list(row) for row in zip(*self.current_piece.shape[::-1])]
        
        if not self.valid_space(self.current_piece):
            self.current_piece.shape = original_shape
        else:
            self.sounds['rotate'].play()
    
    def hard_drop(self):
        """Drop the piece immediately to the bottom"""
        while self.valid_space(self.current_piece):
            self.current_piece.y += 1
            self.sounds['move'].play()
        self.current_piece.y -= 1
        self.change_piece = True
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            
            if not self.game_over:
                self.update_game()
            
            self.render()
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()
    
    def update_game(self):
        """Update game state"""
        self.fall_time += self.clock.get_rawtime()
        self.level_time += self.clock.get_rawtime()
        
        # Increase level every 30 seconds
        if self.level_time / 1000 > 30 and self.level < 10:
            self.level_time = 0
            self.level += 1
            self.fall_speed *= 0.8
        
        # Piece falling
        if self.fall_time / 1000 > self.fall_speed:
            self.fall_time = 0
            self.current_piece.y += 1
            if not self.valid_space(self.current_piece) and self.current_piece.y > 0:
                self.current_piece.y -= 1
                self.change_piece = True
        
        if self.change_piece:
            self.lock_piece()
            self.check_game_over()
        
        self.clock.tick()
    
    def lock_piece(self):
        """Lock the current piece and check for completed rows"""
        for pos in self.convert_shape_format(self.current_piece):
            p = (pos[0], pos[1])
            self.locked_positions[p] = self.current_piece.color
        
        self.current_piece = self.next_piece
        self.next_piece = self.get_shape()
        self.change_piece = False
        rows_cleared = self.clear_rows()
        self.score += rows_cleared * 10 * self.level
    
    def check_game_over(self):
        """Check if game is over"""
        if self.check_lost(self.locked_positions):
            self.sounds['game_over'].play()
            self.game_over = True
    
    def render(self):
        """Render all game elements"""
        self.screen.fill(BLACK)
        
        if self.game_over:
            self.draw_game_over()
        else:
            self.draw_game()
        
        pygame.display.update()
    
    def draw_game(self):
        """Draw the active game state"""
        self.grid = self.create_grid()
        
        # Draw title
        title = self.fonts['large'].render("CHEZA", 1, WHITE)
        self.screen.blit(title, (self.screen.get_width() // 2 - title.get_width() // 2, 10))
        
        # Calculate dynamic positions
        grid_width_px = GRID_WIDTH * GRID_SIZE
        grid_height_px = GRID_HEIGHT * GRID_SIZE
        grid_x = (self.screen.get_width() - grid_width_px) // 2
        grid_y = 100  # Fixed position from top
        
        # Ensure grid stays centered and visible
        if grid_x < 20:
            grid_x = 20
        
        # Draw score and level
        score_text = self.fonts['medium'].render(f"Score: {self.score}", 1, WHITE)
        level_text = self.fonts['medium'].render(f"Level: {self.level}", 1, WHITE)
        
        self.screen.blit(score_text, (20, 60))
        self.screen.blit(level_text, (20, 100))
        
        # Draw next piece preview
        next_text = self.fonts['medium'].render("Next:", 1, WHITE)
        next_x = self.screen.get_width() - 150
        self.screen.blit(next_text, (next_x, 60))
        
        # Draw next piece
        if self.next_piece:
            for y, row in enumerate(self.next_piece.shape):
                for x, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(
                            self.screen, self.next_piece.color,
                            (next_x + x * GRID_SIZE, 100 + y * GRID_SIZE, 
                             GRID_SIZE, GRID_SIZE), 0
                        )
        
        # Draw grid with current piece
        self.draw_grid(grid_x, grid_y)
        
        # Draw border around play area
        border_rect = pygame.Rect(
            grid_x - 2, grid_y - 2,
            grid_width_px + 4, grid_height_px + 4
        )
        pygame.draw.rect(self.screen, WHITE, border_rect, 2)
    
    def draw_game_over(self):
        """Draw game over screen"""
        self.screen.fill(BLACK)
        game_over_text = self.fonts['large'].render("GAME OVER", 1, WHITE)
        score_text = self.fonts['medium'].render(f"Final Score: {self.score}", 1, WHITE)
        restart_text = self.fonts['medium'].render("Press ENTER to Play Again", 1, WHITE)
        
        self.screen.blit(game_over_text, (
            self.screen.get_width() // 2 - game_over_text.get_width() // 2,
            self.screen.get_height() // 2 - 100
        ))
        self.screen.blit(score_text, (
            self.screen.get_width() // 2 - score_text.get_width() // 2,
            self.screen.get_height() // 2
        ))
        self.screen.blit(restart_text, (
            self.screen.get_width() // 2 - restart_text.get_width() // 2,
            self.screen.get_height() // 2 + 100
        ))
    
    def draw_grid(self, grid_x, grid_y):
        """Draw the game grid with current piece"""
        # Draw locked pieces
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if (x, y) in self.locked_positions:
                    pygame.draw.rect(
                        self.screen, self.locked_positions[(x, y)],
                        (grid_x + x * GRID_SIZE, grid_y + y * GRID_SIZE,
                         GRID_SIZE, GRID_SIZE), 0
                    )
        
        # Draw current piece
        for pos in self.convert_shape_format(self.current_piece):
            x, y = pos
            if y >= 0:  # Only draw if visible
                pygame.draw.rect(
                    self.screen, self.current_piece.color,
                    (grid_x + x * GRID_SIZE, grid_y + y * GRID_SIZE,
                     GRID_SIZE, GRID_SIZE), 0
                )
        
        # Draw grid lines
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(
                self.screen, GRAY,
                (grid_x, grid_y + y * GRID_SIZE),
                (grid_x + GRID_WIDTH * GRID_SIZE, grid_y + y * GRID_SIZE)
            )
        
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(
                self.screen, GRAY,
                (grid_x + x * GRID_SIZE, grid_y),
                (grid_x + x * GRID_SIZE, grid_y + GRID_HEIGHT * GRID_SIZE)
            )
    
    # ... (Keep all the existing Tetrimino class and helper methods from previous version)
    # Just update them to use self. instead of global variables

if __name__ == "__main__":
    game = Game()
    game.run()