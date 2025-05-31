import pygame
import sys
import random
import os

# Create assets directory if it doesn't exist
os.makedirs("assets", exist_ok=True)

# Initialize Pygame
pygame.init()
pygame.mixer.init() # Initialize the mixer for sounds

# --- Asset Loading ---
try:
    bird_img = pygame.image.load(os.path.join("assets", "bird.png")).convert_alpha()
except pygame.error as e:
    print(f"Warning: Could not load bird.png: {e}")
    bird_img = None

try:
    pipe_img = pygame.image.load(os.path.join("assets", "pipe.png")).convert_alpha()
except pygame.error as e:
    print(f"Warning: Could not load pipe.png: {e}")
    pipe_img = None

try:
    bg_img = pygame.image.load(os.path.join("assets", "background.png")).convert()
except pygame.error as e:
    print(f"Warning: Could not load background.png: {e}")
    bg_img = None

try:
    flap_sound = pygame.mixer.Sound(os.path.join("assets", "flap.wav"))
except pygame.error as e:
    print(f"Warning: Could not load flap.wav: {e}")
    flap_sound = None
try:
    score_sound = pygame.mixer.Sound(os.path.join("assets", "score.wav"))
except pygame.error as e:
    print(f"Warning: Could not load score.wav: {e}")
    score_sound = None
try:
    hit_sound = pygame.mixer.Sound(os.path.join("assets", "hit.wav"))
except pygame.error as e:
    print(f"Warning: Could not load hit.wav: {e}")
    hit_sound = None
# --- End Asset Loading ---

# Screen dimensions
SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512

# Create the game display window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Set window title
pygame.display.set_caption('Flappy Bird')

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Screen dimensions
SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512

# Colors
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Create the game display window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird')

# Clock for controlling frame rate
clock = pygame.time.Clock()

class Bird:
    def __init__(self):
        self.original_gravity = 0.25
        self.original_lift = -6

        if bird_img:
            self.image = bird_img
            self.rect = self.image.get_rect(center=(SCREEN_WIDTH / 4, SCREEN_HEIGHT / 2))
        else:
            self.image = None
            self.width = 34  # Fallback width
            self.height = 24 # Fallback height
            self.rect = pygame.Rect(0, 0, self.width, self.height)
            self.rect.center = (SCREEN_WIDTH / 4, SCREEN_HEIGHT / 2)

        self.x = self.rect.centerx # Keep x,y for non-image based movement if needed elsewhere
        self.y = self.rect.centery
        self.velocity = 0
        self.gravity = self.original_gravity
        self.lift = self.original_lift


    def update(self):
        self.velocity += self.gravity
        self.rect.centery += self.velocity

        # Prevent bird from moving above the screen
        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity = 0 # Optional: stop upward movement when hitting the top

        # self.x and self.y are not strictly needed if self.rect is always primary
        # but if other logic uses them, keep them updated
        self.x = self.rect.centerx
        self.y = self.rect.centery


    def flap(self):
        self.velocity = self.lift
        if flap_sound:
            flap_sound.play()

    def draw(self, surface):
        if self.image:
            surface.blit(self.image, self.rect)
        else:
            # Fallback drawing if image is missing
            pygame.draw.rect(surface, YELLOW, self.rect)


class Pipe:
    def __init__(self):
        self.x = SCREEN_WIDTH
        self.pipe_width = 50 # Used for rect dimensions if no image
        self.gap_height = 150
        self.pipe_speed = 2
        min_pipe_height = 50
        max_pipe_height = SCREEN_HEIGHT - self.gap_height - 50
        self.top_pipe_height = random.randint(min_pipe_height, max_pipe_height)
        self.bottom_pipe_y = self.top_pipe_height + self.gap_height
        self.passed = False

        if pipe_img:
            self.image = pipe_img
            self.flipped_image = pygame.transform.flip(self.image, False, True)
            # Adjust pipe_width if image is loaded, to match image width
            self.pipe_width = self.image.get_width()
        else:
            self.image = None
            self.flipped_image = None
            # self.pipe_width remains the default 50

        self.top_pipe_rect = pygame.Rect(self.x, 0, self.pipe_width, self.top_pipe_height)
        self.bottom_pipe_rect = pygame.Rect(self.x, self.bottom_pipe_y, self.pipe_width, SCREEN_HEIGHT - self.bottom_pipe_y)


    def update(self):
        self.x -= self.pipe_speed
        self.top_pipe_rect.x = self.x
        self.bottom_pipe_rect.x = self.x

    def draw(self, surface):
        if self.image and self.flipped_image:
            # Top pipe (flipped)
            # The rect's y is 0, rect's height is top_pipe_height.
            # We want to blit the image such that its bottom aligns with top_pipe_rect.bottom
            surface.blit(self.flipped_image, (self.top_pipe_rect.x, self.top_pipe_rect.bottom - self.flipped_image.get_height()))

            # Bottom pipe (normal)
            # The rect's y is bottom_pipe_y.
            # We want to blit the image such that its top aligns with bottom_pipe_rect.top
            surface.blit(self.image, (self.bottom_pipe_rect.x, self.bottom_pipe_rect.top))
        else:
            # Fallback drawing if images are missing
            pygame.draw.rect(surface, GREEN, self.top_pipe_rect)
            pygame.draw.rect(surface, GREEN, self.bottom_pipe_rect)

    def is_offscreen(self):
        return self.x + self.pipe_width < 0


# Create a bird instance
bird = Bird()

# Pipe management
pipes = []
pipe_frequency = 1500  # milliseconds
last_pipe_time = pygame.time.get_ticks()

# Pipe management
pipes = []
pipe_frequency = 1500  # milliseconds
last_pipe_time = pygame.time.get_ticks() # Will be reset by reset_game

# Font objects
score_font = pygame.font.Font(None, 36)
game_over_font = pygame.font.Font(None, 48)

# Initial placeholder/dummy initializations
bird = None
score = 0
game_over = False
# last_pipe_time is already initialized above, reset_game will update it

def reset_game():
    global bird, pipes, score, game_over, last_pipe_time
    bird = Bird()
    pipes = []
    score = 0
    game_over = False
    last_pipe_time = pygame.time.get_ticks()

# Call reset_game() to set the initial game state
reset_game()

# Game loop
running = True
while running:
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                bird.flap()
            if event.key == pygame.K_r and game_over:
                reset_game()

    if not game_over:
        # Pipe Generation
        if current_time - last_pipe_time > pipe_frequency:
            pipes.append(Pipe())
            last_pipe_time = current_time

        # Update game state
        bird.update()
        for pipe in pipes:
            pipe.update()

        # Scoring Logic
        for pipe in pipes:
            if not pipe.passed and bird.rect.left > pipe.top_pipe_rect.right:
                score += 1
                pipe.passed = True
                print(f"Score: {score}")
                if score_sound:
                    score_sound.play()

        # Collision with Pipes
        for pipe in pipes:
            if bird.rect.colliderect(pipe.top_pipe_rect) or \
               bird.rect.colliderect(pipe.bottom_pipe_rect):
                if not game_over: # Play sound only on first collision
                    print("Collision with pipe!")
                    if hit_sound:
                        hit_sound.play()
                game_over = True
                break

        # Collision with Ground (Bird)
        if bird.rect.bottom >= SCREEN_HEIGHT:
            if not game_over: # Play sound only on first collision
                print("Collision with ground!")
                if hit_sound:
                    hit_sound.play()
            game_over = True

        # Remove off-screen pipes
        pipes = [pipe for pipe in pipes if not pipe.is_offscreen()]

    # Draw everything
    if bg_img:
        screen.blit(bg_img, (0, 0))
    else:
        screen.fill(WHITE)  # Fill the screen with white

    bird.draw(screen)   # Draw the bird
    for pipe in pipes:
        pipe.draw(screen) # Draw the pipes

    # Display Score
    score_surface = score_font.render(f"Score: {score}", True, BLACK)
    score_rect = score_surface.get_rect(center=(SCREEN_WIDTH / 2, 50))
    screen.blit(score_surface, score_rect)

    if game_over:
        # Display Game Over message
        game_over_text_surface = game_over_font.render("Game Over", True, BLACK)
        game_over_text_rect = game_over_text_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50))
        screen.blit(game_over_text_surface, game_over_text_rect)

        restart_surface = score_font.render("Press R to Restart", True, BLACK)
        restart_rect = restart_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 10))
        screen.blit(restart_surface, restart_rect)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)  # 60 FPS

# Quit Pygame and exit
pygame.quit()
sys.exit()
