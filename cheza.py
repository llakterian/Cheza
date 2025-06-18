import os
import sys
import random
import pygame
import json

# Initialize paths
GAME_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(GAME_DIR)

# Game constants
GRID_WIDTH = 10
GRID_HEIGHT = 20
MIN_GRID_SIZE = 20  # Minimum size of each block in pixels
MAX_GRID_SIZE = 50  # Maximum size of each block in pixels
DEFAULT_GRID_SIZE = 30
MIN_WINDOW_WIDTH = 400
MIN_WINDOW_HEIGHT = 600
INITIAL_WINDOW_WIDTH = 800  # Larger initial window size
INITIAL_WINDOW_HEIGHT = 900

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
COLORS = [
    (0, 255, 255), (0, 0, 255), (255, 165, 0),
    (255, 255, 0), (0, 255, 0), (128, 0, 128),
    (255, 0, 0)
]

# Complete Tetrimino shapes
SHAPES = {
    'I': [[[0,0,0,0], [1,1,1,1], [0,0,0,0], [0,0,0,0]],
          [[0,0,1,0], [0,0,1,0], [0,0,1,0], [0,0,1,0]]],
    'J': [[[1,0,0], [1,1,1], [0,0,0]],
          [[0,1,1], [0,1,0], [0,1,0]],
          [[0,0,0], [1,1,1], [0,0,1]],
          [[0,1,0], [0,1,0], [1,1,0]]],
    'L': [[[0,0,1], [1,1,1], [0,0,0]],
          [[0,1,0], [0,1,0], [0,1,1]],
          [[0,0,0], [1,1,1], [1,0,0]],
          [[1,1,0], [0,1,0], [0,1,0]]],
    'O': [[[1,1], [1,1]]],
    'S': [[[0,1,1], [1,1,0], [0,0,0]],
          [[0,1,0], [0,1,1], [0,0,1]]],
    'T': [[[0,1,0], [1,1,1], [0,0,0]],
          [[0,1,0], [0,1,1], [0,1,0]],
          [[0,0,0], [1,1,1], [0,1,0]],
          [[0,1,0], [1,1,0], [0,1,0]]],
    'Z': [[[1,1,0], [0,1,1], [0,0,0]],
          [[0,0,1], [0,1,1], [0,1,0]]]
}

class Tetrimino:
    def __init__(self, shape_type, x=GRID_WIDTH//2-1, y=0):
        self.shape_type = shape_type
        self.shape = SHAPES[shape_type]
        self.rotation = 0
        self.x = x
        self.y = y
        self.color = COLORS[list(SHAPES.keys()).index(shape_type)]

    def get_current_shape(self):
        return self.shape[self.rotation % len(self.shape)]

class Game:
    def __init__(self):
        self.high_score = self.load_high_score()
        self.grid_size = DEFAULT_GRID_SIZE
        self.setup_window()
        self.load_assets()
        self.reset_game()
        
    def setup_window(self):
        """Initialize window with icon"""
        self.screen = pygame.display.set_mode(
            (INITIAL_WINDOW_WIDTH, INITIAL_WINDOW_HEIGHT), 
            pygame.RESIZABLE
        )
        pygame.display.set_caption("Cheza - Tetris for Kids")
        
        # Set icon
        icon_path = os.path.join(GAME_DIR, 'assets/cheza_icon.png')
        if os.path.exists(icon_path):
            icon = pygame.image.load(icon_path)
            pygame.display.set_icon(icon)
        else:
            self.create_default_icon()

    def handle_resize(self, event):
        """Handle window resize events"""
        if event.type == pygame.VIDEORESIZE:
            # Calculate possible grid size based on width and height
            width_based = (event.w - 200) // GRID_WIDTH  # Leave space for UI
            height_based = (event.h - 100) // GRID_HEIGHT
            
            # Choose the smaller of the two, constrained to min/max
            new_size = min(width_based, height_based, MAX_GRID_SIZE)
            new_size = max(new_size, MIN_GRID_SIZE)
            
            # Only update if significant change
            if abs(new_size - self.grid_size) > 2:
                self.grid_size = new_size
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                return True
        return False

    def load_sound(self, filename):
        """Load sound file with silent fallback"""
        try:
            sound_path = os.path.join('sounds', filename)
            if os.path.exists(sound_path):
                return pygame.mixer.Sound(sound_path)
            else:
                # Create a silent sound as fallback
                return pygame.mixer.Sound(buffer=b'\x00\x00' * 1000)
        except pygame.error:
            # Return silent sound if loading fails
            return pygame.mixer.Sound(buffer=b'\x00\x00' * 1000)

    def load_assets(self):
        """Load all game assets with fallbacks"""
        # Create directories if they don't exist
        os.makedirs('sounds', exist_ok=True)
        
        # Sound effects with silent fallbacks
        self.sounds = {
            'move': self.load_sound('move.wav'),
            'rotate': self.load_sound('rotate.wav'),
            'clear': self.load_sound('clear.wav'),
            'game_over': self.load_sound('gameover.wav')
        }
        
        # Fonts (with dynamic sizing based on grid size)
        self.fonts = {
            'small': pygame.font.SysFont('comicsans', max(15, self.grid_size // 2)),
            'medium': pygame.font.SysFont('comicsans', max(20, self.grid_size // 1.5)),
            'large': pygame.font.SysFont('comicsans', max(30, self.grid_size))
        }

    def create_default_icon(self):
        """Create a default icon if none exists"""
        icon_surface = pygame.Surface((32, 32))
        icon_surface.fill((0, 255, 255))
        pygame.display.set_icon(icon_surface)

    def reset_game(self):
        """Reset game state for new game"""
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_time = 0
        self.fall_speed = 500  # milliseconds
        self.game_over = False
        self.paused = False
        self.current_piece = self.get_new_piece()
        self.next_piece = self.get_new_piece()

    def toggle_pause(self):
        """Toggle pause state"""
        self.paused = not self.paused

    def get_new_piece(self):
        """Generate a new random tetrimino"""
        shape_type = random.choice(list(SHAPES.keys()))
        return Tetrimino(shape_type)

    def is_valid_position(self, piece, dx=0, dy=0, rotation=None):
        """Check if piece position is valid"""
        if rotation is None:
            rotation = piece.rotation
        
        shape = piece.shape[rotation % len(piece.shape)]
        
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = piece.x + x + dx
                    new_y = piece.y + y + dy
                    
                    if (new_x < 0 or new_x >= GRID_WIDTH or 
                        new_y >= GRID_HEIGHT or 
                        (new_y >= 0 and self.grid[new_y][new_x])):
                        return False
        return True

    def place_piece(self, piece):
        """Place piece on the grid"""
        shape = piece.get_current_shape()
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    grid_x = piece.x + x
                    grid_y = piece.y + y
                    if grid_y >= 0:
                        self.grid[grid_y][grid_x] = COLORS.index(piece.color) + 1

    def clear_lines(self):
        """Clear completed lines"""
        lines_to_clear = []
        for y in range(GRID_HEIGHT):
            if all(self.grid[y]):
                lines_to_clear.append(y)
        
        for y in lines_to_clear:
            del self.grid[y]
            self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
        
        if lines_to_clear:
            self.sounds['clear'].play()
            self.lines_cleared += len(lines_to_clear)
            self.score += len(lines_to_clear) * 100 * self.level
            self.level = self.lines_cleared // 10 + 1
            self.fall_speed = max(50, 500 - (self.level - 1) * 50)

    def handle_input(self, event):
        """Handle keyboard input"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                if self.is_valid_position(self.current_piece, dx=-1) and not self.paused:
                    self.current_piece.x -= 1
                    self.sounds['move'].play()
            elif event.key == pygame.K_RIGHT:
                if self.is_valid_position(self.current_piece, dx=1) and not self.paused:
                    self.current_piece.x += 1
                    self.sounds['move'].play()
            elif event.key == pygame.K_DOWN:
                if self.is_valid_position(self.current_piece, dy=1) and not self.paused:
                    self.current_piece.y += 1
                    self.score += 1
            elif event.key == pygame.K_UP:
                new_rotation = (self.current_piece.rotation + 1) % len(self.current_piece.shape)
                if self.is_valid_position(self.current_piece, rotation=new_rotation) and not self.paused:
                    self.current_piece.rotation = new_rotation
                    self.sounds['rotate'].play()
            elif event.key == pygame.K_p:  # Pause with P key
                self.toggle_pause()
            elif event.key == pygame.K_r and self.game_over:
                self.reset_game()

    def update(self, dt):
        """Update game state"""
        if self.game_over or self.paused:
            return
        
        self.fall_time += dt
        if self.fall_time >= self.fall_speed:
            if self.is_valid_position(self.current_piece, dy=1):
                self.current_piece.y += 1
            else:
                self.place_piece(self.current_piece)
                self.clear_lines()
                self.current_piece = self.next_piece
                self.next_piece = self.get_new_piece()
                
                if not self.is_valid_position(self.current_piece):
                    self.game_over = True
                    self.sounds['game_over'].play()
                    if self.score > self.high_score:
                        self.high_score = self.score
                        self.save_high_score()
            
            self.fall_time = 0

    def draw(self):
        """Draw everything with dynamic sizing"""
        self.screen.fill(BLACK)
        
        # Calculate centered grid position
        grid_total_width = GRID_WIDTH * self.grid_size
        grid_total_height = GRID_HEIGHT * self.grid_size
        grid_x = (self.screen.get_width() - grid_total_width) // 2
        grid_y = (self.screen.get_height() - grid_total_height) // 3
        
        # Draw grid
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(
                    grid_x + x * self.grid_size,
                    grid_y + y * self.grid_size,
                    self.grid_size,
                    self.grid_size
                )
                
                if self.grid[y][x]:
                    color = COLORS[self.grid[y][x] - 1]
                    pygame.draw.rect(self.screen, color, rect)
                
                pygame.draw.rect(self.screen, LIGHT_GRAY, rect, 1)
        
        # Draw current piece
        if not self.game_over and not self.paused:
            shape = self.current_piece.get_current_shape()
            for y, row in enumerate(shape):
                for x, cell in enumerate(row):
                    if cell:
                        rect = pygame.Rect(
                            grid_x + (self.current_piece.x + x) * self.grid_size,
                            grid_y + (self.current_piece.y + y) * self.grid_size,
                            self.grid_size,
                            self.grid_size
                        )
                        pygame.draw.rect(self.screen, self.current_piece.color, rect)
                        pygame.draw.rect(self.screen, WHITE, rect, 2)
        
        # Draw UI
        self.draw_ui(grid_x + grid_total_width + 20)

    def draw_ui(self, ui_x):
        """Draw user interface with dynamic positioning"""
        ui_y = 50
        
        # Score
        score_text = self.fonts['medium'].render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (ui_x, ui_y))
        
        # High Score
        high_score_text = self.fonts['small'].render(f"High: {self.high_score}", True, WHITE)
        self.screen.blit(high_score_text, (ui_x, ui_y + 40))
        
        # Level
        level_text = self.fonts['small'].render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (ui_x, ui_y + 80))
        
        # Lines
        lines_text = self.fonts['small'].render(f"Lines: {self.lines_cleared}", True, WHITE)
        self.screen.blit(lines_text, (ui_x, ui_y + 120))
        
        # Resize instructions
        resize_text = self.fonts['small'].render("Resize window to adjust board size", True, WHITE)
        self.screen.blit(resize_text, (20, self.screen.get_height() - 30))
        
        # Game Over
        if self.game_over:
            game_over_text = self.fonts['large'].render("GAME OVER", True, WHITE)
            restart_text = self.fonts['small'].render("Press R to restart", True, WHITE)
            text_x = (self.screen.get_width() - game_over_text.get_width()) // 2
            self.screen.blit(game_over_text, (text_x, self.screen.get_height() // 3))
            self.screen.blit(restart_text, (text_x, self.screen.get_height() // 3 + 60))
        
        # Pause Status
        if self.paused:
            pause_text = self.fonts['large'].render("PAUSED", True, WHITE)
            continue_text = self.fonts['small'].render("Press P to continue", True, WHITE)
            text_x = (self.screen.get_width() - pause_text.get_width()) // 2
            self.screen.blit(pause_text, (text_x, self.screen.get_height() // 3))
            self.screen.blit(continue_text, (text_x, self.screen.get_height() // 3 + 60))

    def run(self):
        """Main game loop with resize handling"""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            dt = clock.tick(60)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.handle_resize(event)
                else:
                    self.handle_input(event)
            
            self.update(dt)
            self.draw()
        
        pygame.quit()
        sys.exit()

    def load_high_score(self):
        try:
            with open('highscore.json', 'r') as f:
                return json.load(f).get('high_score', 0)
        except:
            return 0

    def save_high_score(self):
        with open('highscore.json', 'w') as f:
            json.dump({'high_score': self.high_score}, f)

if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    game = Game()
    game.run()