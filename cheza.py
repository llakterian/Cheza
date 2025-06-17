import pygame
import random
import sys
import os
import math
from pygame import gfxdraw

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Get the absolute path to the game directory
GAME_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(GAME_DIR)

# Game constants
GRID_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
VISIBLE_HEIGHT = 20
MIN_WINDOW_WIDTH = 500
MIN_WINDOW_HEIGHT = 700
INITIAL_WINDOW_WIDTH = 600
INITIAL_WINDOW_HEIGHT = 800
PREVIEW_COUNT = 5  # Number of next pieces to show

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
LIGHT_GRAY = (200, 200, 200)
GHOST_ALPHA = 100  # Transparency for ghost piece

# Piece colors with modern Tetris palette
COLORS = [
    (0, 240, 240),    # Cyan - I
    (0, 0, 240),      # Blue - J
    (240, 160, 0),    # Orange - L
    (240, 240, 0),    # Yellow - O
    (0, 240, 0),      # Green - S
    (160, 0, 240),    # Purple - T
    (240, 0, 0)       # Red - Z
]

# Tetrimino shapes with all rotations
SHAPES = {
    'I': [
        [[0, 0, 0, 0],
         [1, 1, 1, 1],
         [0, 0, 0, 0],
         [0, 0, 0, 0]],
    'J': [
        [[1, 0, 0],
         [1, 1, 1],
         [0, 0, 0]],
    'L': [
        [[0, 0, 1],
         [1, 1, 1],
         [0, 0, 0]],
    'O': [
        [[1, 1],
         [1, 1]],
    'S': [
        [[0, 1, 1],
         [1, 1, 0],
         [0, 0, 0]],
    'T': [
        [[0, 1, 0],
         [1, 1, 1],
         [0, 0, 0]],
    'Z': [
        [[1, 1, 0],
         [0, 1, 1],
         [0, 0, 0]]
}

# Wall kick data for rotation (based on SRS)
WALL_KICKS = {
    'JLSTZ': {
        0: {1: [(-1, 0), (-1, 1), (0, -2), (-1, -2)]},
        1: {2: [(1, 0), (1, -1), (0, 2), (1, 2)]},
        2: {3: [(1, 0), (1, 1), (0, -2), (1, -2)]},
        3: {0: [(-1, 0), (-1, -1), (0, 2), (-1, 2)]}
    },
    'I': {
        0: {1: [(-2, 0), (1, 0), (-2, -1), (1, 2)]},
        1: {2: [(-1, 0), (2, 0), (-1, 2), (2, -1)]},
        2: {3: [(2, 0), (-1, 0), (2, 1), (-1, -2)]},
        3: {0: [(1, 0), (-2, 0), (1, -2), (-2, 1)]}
    },
    'O': {}  # O piece doesn't rotate
}

class Game:
    def __init__(self):
        # Game state
        self.reset_game()
        
        # Setup window and assets
        self.setup_window()
        self.load_assets()
        
        # Input handling
        self.move_delay = 0.1  # Seconds before auto-repeat starts
        self.move_repeat = 0.03  # Seconds between auto-repeats
        self.last_move_time = 0
        self.move_direction = 0  # -1 for left, 1 for right
        self.soft_drop_active = False
        
        # Animation states
        self.are_timer = 0  # Appearance delay after piece spawn
        self.are_delay = 0.1  # Seconds
        self.line_clear_timer = 0
        self.line_clear_delay = 0.3  # Seconds
        self.lines_clearing = []
        
        # Game timing
        self.fall_speeds = [
            1.0, 0.8, 0.6, 0.5, 0.4, 0.3, 0.25, 0.2, 0.15, 0.1, 0.05
        ]
        
    def reset_game(self):
        """Reset all game state variables"""
        self.grid = [[(0, 0, 0) for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.locked_positions = {}
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.combo = -1
        self.game_over = False
        self.paused = False
        
        # Piece management
        self.bag = []
        self.next_pieces = []
        self.hold_piece = None
        self.hold_available = True
        self.current_piece = None
        
        # Game timing
        self.fall_time = 0
        self.level_time = 0
        self.fall_speed = self.fall_speeds[min(self.level - 1, len(self.fall_speeds) - 1)]
        
        # Initialize piece systems
        self.fill_bag()
        self.current_piece = self.spawn_piece()
        self.fill_next_pieces()
        
    def setup_window(self):
        """Initialize the game window with proper settings"""
        self.screen = pygame.display.set_mode(
            (INITIAL_WINDOW_WIDTH, INITIAL_WINDOW_HEIGHT), 
            pygame.RESIZABLE | pygame.DOUBLEBUF
        )
        pygame.display.set_caption("Cheza - Ultimate Tetris Experience")
        
        # Create default icon if none exists
        try:
            icon_path = os.path.join(GAME_DIR, 'assets/cheza_icon.png')
            icon = pygame.image.load(icon_path)
            pygame.display.set_icon(icon)
        except Exception as e:
            print(f"Error loading icon: {e}")
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
            'game_over': self.load_sound('sounds/gameover.wav'),
            'hold': self.load_sound('sounds/hold.wav'),
            'drop': self.load_sound('sounds/drop.wav'),
            'tspin': self.load_sound('sounds/tspin.wav'),
            'combo': self.load_sound('sounds/combo.wav')
        }
        
        # Initialize fonts
        self.fonts = {
            'small': pygame.font.SysFont('Arial', 20),
            'medium': pygame.font.SysFont('Arial', 30),
            'large': pygame.font.SysFont('Arial', 50),
            'title': pygame.font.SysFont('Arial', 70, bold=True)
        }
    
    def load_sound(self, path):
        """Load a sound file with silent fallback"""
        try:
            sound_path = os.path.join(GAME_DIR, path)
            return pygame.mixer.Sound(sound_path)
        except Exception as e:
            print(f"Error loading sound {path}: {e}")
            return pygame.mixer.Sound(buffer=bytearray(0))
    
    def fill_bag(self):
        """Fill the randomizer bag with all 7 pieces (7-bag system)"""
        if not self.bag:
            self.bag = list(SHAPES.keys())
            random.shuffle(self.bag)
    
    def spawn_piece(self):
        """Get a new piece from the bag"""
        if not self.bag:
            self.fill_bag()
        
        piece_type = self.bag.pop()
        shape = SHAPES[piece_type]
        color = COLORS[list(SHAPES.keys()).index(piece_type)]
        
        # Center the piece
        x = GRID_WIDTH // 2 - len(shape[0]) // 2
        y = 0 if piece_type != 'I' else -1  # I piece spawns one row higher
        
        return Tetrimino(x, y, shape, color, piece_type)
    
    def fill_next_pieces(self):
        """Fill the next pieces queue"""
        while len(self.next_pieces) < PREVIEW_COUNT:
            if not self.bag:
                self.fill_bag()
            self.next_pieces.append(self.spawn_piece())
    
    def hold_current_piece(self):
        """Hold the current piece"""
        if not self.hold_available:
            return
        
        self.sounds['hold'].play()
        
        if self.hold_piece is None:
            self.hold_piece = self.current_piece
            self.current_piece = self.next_pieces.pop(0)
            self.fill_next_pieces()
        else:
            self.hold_piece, self.current_piece = self.current_piece, self.hold_piece
            self.current_piece.x = GRID_WIDTH // 2 - len(self.current_piece.shape[0]) // 2
            self.current_piece.y = 0 if self.current_piece.piece_type != 'I' else -1
        
        self.hold_available = False
    
    def rotate_piece(self, direction=1):
        """Rotate the current piece with wall kicks"""
        if self.current_piece.piece_type == 'O':
            return  # O piece doesn't rotate
        
        original_rotation = self.current_piece.rotation
        original_shape = self.current_piece.shape
        
        # Rotate the piece
        self.current_piece.rotation = (self.current_piece.rotation + direction) % 4
        self.current_piece.shape = [list(row) for row in zip(*self.current_piece.shape[::-1])]
        
        # Get wall kick data
        piece_type = 'I' if self.current_piece.piece_type == 'I' else 'JLSTZ'
        kicks = WALL_KICKS[piece_type].get(original_rotation, {}).get(self.current_piece.rotation, [])
        
        # Try each kick
        for kick in kicks:
            self.current_piece.x += kick[0]
            self.current_piece.y += kick[1]
            
            if self.valid_space(self.current_piece):
                self.sounds['rotate'].play()
                
                # Check for T-Spin
                if self.current_piece.piece_type == 'T':
                    corners = 0
                    offsets = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
                    for dx, dy in offsets:
                        x, y = self.current_piece.x + dx, self.current_piece.y + dy
                        if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT or (x, y) in self.locked_positions:
                            corners += 1
                    
                    if corners >= 3:
                        self.sounds['tspin'].play()
                        self.last_tspin = True
                
                return True
        
        # If no kicks worked, revert rotation
        self.current_piece.rotation = original_rotation
        self.current_piece.shape = original_shape
        return False
    
    def valid_space(self, piece):
        """Check if piece is in valid position"""
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    px = piece.x + x
                    py = piece.y + y
                    
                    if (px < 0 or px >= GRID_WIDTH or 
                        py >= GRID_HEIGHT or 
                        (py >= 0 and (px, py) in self.locked_positions)):
                        return False
        return True
    
    def lock_piece(self):
        """Lock the current piece into the grid"""
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    px = self.current_piece.x + x
                    py = self.current_piece.y + y
                    if py >= 0:  # Only lock if above the death line
                        self.locked_positions[(px, py)] = self.current_piece.color
        
        # Check for line clears
        self.clear_lines()
        
        # Spawn new piece
        self.current_piece = self.next_pieces.pop(0)
        self.fill_next_pieces()
        self.hold_available = True
        self.are_timer = pygame.time.get_ticks() / 1000
        
        # Check for game over
        if not self.valid_space(self.current_piece):
            self.game_over = True
            self.sounds['game_over'].play()
    
    def clear_lines(self):
        """Check and clear completed lines"""
        lines_to_clear = []
        
        for y in range(GRID_HEIGHT):
            if all((x, y) in self.locked_positions for x in range(GRID_WIDTH)):
                lines_to_clear.append(y)
        
        if lines_to_clear:
            self.sounds['clear'].play()
            self.lines_clearing = lines_to_clear
            self.line_clear_timer = pygame.time.get_ticks() / 1000
            
            # Calculate score
            line_count = len(lines_to_clear)
            self.lines_cleared += line_count
            self.level = min(1 + self.lines_cleared // 10, len(self.fall_speeds))
            self.fall_speed = self.fall_speeds[self.level - 1]
            
            # Scoring based on modern Tetris guidelines
            base_scores = {1: 100, 2: 300, 3: 500, 4: 800}
            score_multiplier = self.level
            
            if hasattr(self, 'last_tspin') and self.last_tspin:
                tspin_scores = {0: 400, 1: 800, 2: 1200, 3: 1600}
                self.score += tspin_scores.get(line_count, 0) * score_multiplier
                del self.last_tspin
            else:
                self.score += base_scores.get(line_count, 0) * score_multiplier
            
            # Combo system
            if self.combo >= 0:
                self.score += 50 * self.combo * score_multiplier
                self.sounds['combo'].play()
            self.combo += 1
        else:
            self.combo = -1
    
    def process_line_clears(self):
        """Actually remove the lines after animation"""
        # Remove the lines
        for y in sorted(self.lines_clearing, reverse=True):
            # Remove the line
            for x in range(GRID_WIDTH):
                if (x, y) in self.locked_positions:
                    del self.locked_positions[(x, y)]
            
            # Move everything above down
            for yy in range(y - 1, -1, -1):
                for x in range(GRID_WIDTH):
                    if (x, yy) in self.locked_positions:
                        self.locked_positions[(x, yy + 1)] = self.locked_positions.pop((x, yy))
        
        self.lines_clearing = []
    
    def hard_drop(self):
        """Instantly drop the piece"""
        while self.valid_space(self.current_piece):
            self.current_piece.y += 1
        
        self.current_piece.y -= 1
        self.sounds['drop'].play()
        self.lock_piece()
    
    def get_ghost_piece(self):
        """Calculate where the piece would land"""
        ghost = Tetrimino(
            self.current_piece.x,
            self.current_piece.y,
            self.current_piece.shape,
            self.current_piece.color,
            self.current_piece.piece_type
        )
        
        while self.valid_space(ghost):
            ghost.y += 1
        
        ghost.y -= 1
        return ghost
    
    def draw_piece(self, piece, surface=None, offset_x=0, offset_y=0, alpha=255, ghost=False):
        """Draw a piece with optional transparency and offset"""
        if surface is None:
            surface = self.screen
        
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    px = piece.x + x
                    py = piece.y + y
                    
                    if 0 <= py < GRID_HEIGHT:
                        rect = pygame.Rect(
                            offset_x + px * GRID_SIZE,
                            offset_y + py * GRID_SIZE,
                            GRID_SIZE, GRID_SIZE
                        )
                        
                        if ghost:
                            # Draw ghost piece with outline
                            s = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
                            s.fill((*piece.color, GHOST_ALPHA))
                            surface.blit(s, rect)
                            
                            pygame.draw.rect(
                                surface, 
                                (*piece.color, alpha), 
                                rect, 
                                1
                            )
                        else:
                            # Draw normal piece
                            pygame.draw.rect(
                                surface, 
                                piece.color, 
                                rect
                            )
                            
                            # Add some shading for 3D effect
                            pygame.draw.rect(
                                surface, 
                                (min(c + 40, 255) for c in piece.color), 
                                rect.inflate(-4, -4), 
                                2
                            )
    
    def draw_grid(self, offset_x, offset_y):
        """Draw the game grid"""
        # Draw locked pieces
        for (x, y), color in self.locked_positions.items():
            if 0 <= y < GRID_HEIGHT:
                rect = pygame.Rect(
                    offset_x + x * GRID_SIZE,
                    offset_y + y * GRID_SIZE,
                    GRID_SIZE, GRID_SIZE
                )
                
                # Draw the cell
                pygame.draw.rect(self.screen, color, rect)
                
                # Add cell border
                pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)
        
        # Draw grid lines
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(
                self.screen, GRAY,
                (offset_x + x * GRID_SIZE, offset_y),
                (offset_x + x * GRID_SIZE, offset_y + VISIBLE_HEIGHT * GRID_SIZE)
            )
        
        for y in range(VISIBLE_HEIGHT + 1):
            pygame.draw.line(
                self.screen, GRAY,
                (offset_x, offset_y + y * GRID_SIZE),
                (offset_x + GRID_WIDTH * GRID_SIZE, offset_y + y * GRID_SIZE)
            )
        
        # Draw line clear animation
        current_time = pygame.time.get_ticks() / 1000
        if self.lines_clearing and current_time - self.line_clear_timer < self.line_clear_delay:
            progress = (current_time - self.line_clear_timer) / self.line_clear_delay
            flash_color = (
                int(255 * (1 - progress)),
                int(255 * (1 - progress)),
                int(255 * (1 - progress))
            )
            
            for y in self.lines_clearing:
                if 0 <= y < GRID_HEIGHT:
                    rect = pygame.Rect(
                        offset_x,
                        offset_y + y * GRID_SIZE,
                        GRID_WIDTH * GRID_SIZE,
                        GRID_SIZE
                    )
                    pygame.draw.rect(self.screen, flash_color, rect)
    
    def draw_sidebar(self):
        """Draw the sidebar with score, level, etc."""
        sidebar_x = GRID_WIDTH * GRID_SIZE + 50
        
        # Draw score
        score_text = self.fonts['medium'].render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (sidebar_x, 50))
        
        # Draw level
        level_text = self.fonts['medium'].render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (sidebar_x, 100))
        
        # Draw lines
        lines_text = self.fonts['medium'].render(f"Lines: {self.lines_cleared}", True, WHITE)
        self.screen.blit(lines_text, (sidebar_x, 150))
        
        # Draw next pieces
        next_text = self.fonts['medium'].render("Next:", True, WHITE)
        self.screen.blit(next_text, (sidebar_x, 220))
        
        for i, piece in enumerate(self.next_pieces[:PREVIEW_COUNT]):
            # Draw each next piece preview
            for y, row in enumerate(piece.shape):
                for x, cell in enumerate(row):
                    if cell:
                        rect = pygame.Rect(
                            sidebar_x + x * GRID_SIZE,
                            270 + i * 80 + y * GRID_SIZE,
                            GRID_SIZE, GRID_SIZE
                        )
                        pygame.draw.rect(self.screen, piece.color, rect)
                        pygame.draw.rect(self.screen, BLACK, rect, 1)
        
        # Draw hold piece
        hold_text = self.fonts['medium'].render("Hold:", True, WHITE)
        self.screen.blit(hold_text, (sidebar_x, 550))
        
        if self.hold_piece:
            for y, row in enumerate(self.hold_piece.shape):
                for x, cell in enumerate(row):
                    if cell:
                        rect = pygame.Rect(
                            sidebar_x + x * GRID_SIZE,
                            600 + y * GRID_SIZE,
                            GRID_SIZE, GRID_SIZE
                        )
                        pygame.draw.rect(self.screen, self.hold_piece.color, rect)
                        pygame.draw.rect(self.screen, BLACK, rect, 1)
    
    def draw_game(self):
        """Draw the entire game state"""
        self.screen.fill(BLACK)
        
        # Calculate grid position (centered horizontally)
        grid_width = GRID_WIDTH * GRID_SIZE
        grid_height = VISIBLE_HEIGHT * GRID_SIZE
        grid_x = (self.screen.get_width() - grid_width) // 2 - 100
        grid_y = 50
        
        # Draw title
        title = self.fonts['title'].render("CHEZA", True, WHITE)
        self.screen.blit(title, (self.screen.get_width() // 2 - title.get_width() // 2, 5))
        
        # Draw the grid background
        pygame.draw.rect(
            self.screen, GRAY,
            (grid_x - 5, grid_y - 5, grid_width + 10, grid_height + 10),
            0
        )
        
        # Draw the grid
        self.draw_grid(grid_x, grid_y)
        
        # Draw ghost piece
        if not self.lines_clearing and not self.game_over and not self.paused:
            ghost = self.get_ghost_piece()
            self.draw_piece(ghost, offset_x=grid_x, offset_y=grid_y, ghost=True)
        
        # Draw current piece (if not in ARE delay)
        current_time = pygame.time.get_ticks() / 1000
        if (not self.lines_clearing and not self.game_over and not self.paused and 
            current_time - self.are_timer > self.are_delay):
            self.draw_piece(self.current_piece, offset_x=grid_x, offset_y=grid_y)
        
        # Draw sidebar
        self.draw_sidebar()
        
        # Draw game over or paused screen
        if self.game_over:
            overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.fonts['large'].render("GAME OVER", True, WHITE)
            score_text = self.fonts['medium'].render(f"Final Score: {self.score}", True, WHITE)
            restart_text = self.fonts['medium'].render("Press ENTER to Restart", True, WHITE)
            
            self.screen.blit(game_over_text, (
                self.screen.get_width() // 2 - game_over_text.get_width() // 2,
                self.screen.get_height() // 2 - 60
            ))
            self.screen.blit(score_text, (
                self.screen.get_width() // 2 - score_text.get_width() // 2,
                self.screen.get_height() // 2
            ))
            self.screen.blit(restart_text, (
                self.screen.get_width() // 2 - restart_text.get_width() // 2,
                self.screen.get_height() // 2 + 60
            ))
        elif self.paused:
            overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            pause_text = self.fonts['large'].render("PAUSED", True, WHITE)
            continue_text = self.fonts['medium'].render("Press P to Continue", True, WHITE)
            
            self.screen.blit(pause_text, (
                self.screen.get_width() // 2 - pause_text.get_width() // 2,
                self.screen.get_height() // 2 - 30
            ))
            self.screen.blit(continue_text, (
                self.screen.get_width() // 2 - continue_text.get_width() // 2,
                self.screen.get_height() // 2 + 30
            ))
    
    def handle_events(self):
        """Handle all pygame events"""
        current_time = pygame.time.get_ticks() / 1000
        
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
                elif self.paused:
                    if event.key == pygame.K_p:
                        self.paused = False
                else:
                    if event.key == pygame.K_LEFT:
                        self.move_piece(-1, 0)
                        self.move_direction = -1
                        self.last_move_time = current_time
                    elif event.key == pygame.K_RIGHT:
                        self.move_piece(1, 0)
                        self.move_direction = 1
                        self.last_move_time = current_time
                    elif event.key == pygame.K_DOWN:
                        self.soft_drop_active = True
                    elif event.key == pygame.K_UP:
                        self.rotate_piece()
                    elif event.key == pygame.K_SPACE:
                        self.hard_drop()
                    elif event.key == pygame.K_c:
                        self.hold_current_piece()
                    elif event.key == pygame.K_p:
                        self.paused = True
            
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and self.move_direction == -1:
                    self.move_direction = 0
                elif event.key == pygame.K_RIGHT and self.move_direction == 1:
                    self.move_direction = 0
                elif event.key == pygame.K_DOWN:
                    self.soft_drop_active = False
    
    def update(self):
        """Update game state"""
        if self.game_over or self.paused:
            return
        
        current_time = pygame.time.get_ticks() / 1000
        
        # Handle DAS (Delayed Auto Shift)
        if self.move_direction != 0 and current_time - self.last_move_time > self.move_delay:
            if current_time - self.last_move_time > self.move_delay + self.move_repeat:
                self.move_piece(self.move_direction, 0)
                self.last_move_time = current_time
        
        # Handle soft drop
        if self.soft_drop_active:
            self.fall_speed = 0.05  # Much faster fall when holding down
        
        # Handle line clear animation
        if self.lines_clearing:
            if current_time - self.line_clear_timer > self.line_clear_delay:
                self.process_line_clears()
            return
        
        # Handle ARE (Appearance Delay)
        if current_time - self.are_timer <= self.are_delay:
            return
        
        # Normal piece falling
        self.fall_time += self.clock.get_rawtime()
        if self.fall_time / 1000 > self.fall_speed:
            self.fall_time = 0
            self.current_piece.y += 1
            
            if not self.valid_space(self.current_piece):
                self.current_piece.y -= 1
                self.lock_piece()
            
            # Reset soft drop speed if not actively pressing
            if not self.soft_drop_active:
                self.fall_speed = self.fall_speeds[min(self.level - 1, len(self.fall_speeds) - 1)]
    
    def run(self):
        """Main game loop"""
        self.clock = pygame.time.Clock()
        self.running = True
        
        while self.running:
            self.handle_events()
            self.update()
            self.draw_game()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

class Tetrimino:
    def __init__(self, x, y, shape, color, piece_type):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = color
        self.piece_type = piece_type
        self.rotation = 0  # 0-3 representing 0°, 90°, 180°, 270°

if __name__ == "__main__":
    game = Game()
    game.run()