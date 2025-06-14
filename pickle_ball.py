import pygame
import sys
import random
import math
import time
import os

# Initialize pygame
pygame.init()

# Try to initialize mixer for sound, but continue if it fails
try:
    pygame.mixer.init()
    sounds_enabled = True
except:
    print("Could not initialize sound system. Game will run without audio.")
    sounds_enabled = False

# Constants
WIDTH, HEIGHT = 800, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 15, 100
BALL_SIZE = 15
PADDLE_SPEED = 8
BALL_SPEED = 5
MAX_SCORE = 20
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
LIGHT_BLUE = (173, 216, 230)
GRAY = (128, 128, 128)

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pickle Ball - 3D Enhanced")

# Clock for controlling game speed
clock = pygame.time.Clock()

# Create directory for sounds if it doesn't exist
sounds_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")
os.makedirs(sounds_dir, exist_ok=True)

# Generate sound files if they don't exist
def generate_sound_files():
    # Paddle hit sound (simple beep)
    if not os.path.exists(os.path.join(sounds_dir, "paddle_hit.wav")):
        pygame.mixer.Sound(bytes(bytearray([0] * 10 + [127] * 100 + [0] * 10))).save(os.path.join(sounds_dir, "paddle_hit.wav"))

    # Wall hit sound (lower beep)
    if not os.path.exists(os.path.join(sounds_dir, "wall_hit.wav")):
        pygame.mixer.Sound(bytes(bytearray([0] * 10 + [80] * 100 + [0] * 10))).save(os.path.join(sounds_dir, "wall_hit.wav"))

    # Score sound (higher beep)
    if not os.path.exists(os.path.join(sounds_dir, "score.wav")):
        pygame.mixer.Sound(bytes(bytearray([0] * 10 + [200] * 300 + [0] * 10))).save(os.path.join(sounds_dir, "score.wav"))

    # Win sound (victory tune)
    if not os.path.exists(os.path.join(sounds_dir, "win.wav")):
        pygame.mixer.Sound(bytes(bytearray([0] * 10 + [150] * 100 + [0] * 10 + [200] * 100 + [0] * 10 + [250] * 200 + [0] * 10))).save(os.path.join(sounds_dir, "win.wav"))

    # Lose sound (sad tune)
    if not os.path.exists(os.path.join(sounds_dir, "lose.wav")):
        pygame.mixer.Sound(bytes(bytearray([0] * 10 + [200] * 100 + [0] * 10 + [150] * 100 + [0] * 10 + [100] * 200 + [0] * 10))).save(os.path.join(sounds_dir, "lose.wav"))

# Try to generate sound files
try:
    generate_sound_files()

    # Load sounds
    paddle_hit_sound = pygame.mixer.Sound(os.path.join(sounds_dir, "paddle_hit.wav"))
    wall_hit_sound = pygame.mixer.Sound(os.path.join(sounds_dir, "wall_hit.wav"))
    score_sound = pygame.mixer.Sound(os.path.join(sounds_dir, "score.wav"))
    win_sound = pygame.mixer.Sound(os.path.join(sounds_dir, "win.wav"))
    lose_sound = pygame.mixer.Sound(os.path.join(sounds_dir, "lose.wav"))

    # Set volume
    paddle_hit_sound.set_volume(0.4)
    wall_hit_sound.set_volume(0.3)
    score_sound.set_volume(0.5)
    win_sound.set_volume(0.7)
    lose_sound.set_volume(0.7)

    sounds_enabled = True
except:
    print("Could not initialize sounds. Game will run without audio.")
    sounds_enabled = False

# Game objects
class Paddle:
    def __init__(self, x, y, width, height, color, speed, is_ai=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.speed = speed
        self.score = 0
        self.is_ai = is_ai
        # 3D effect attributes
        self.shadow_depth = 8
        self.shadow_color = self.darken_color(color, 0.5)

    def darken_color(self, color, factor):
        r, g, b = color
        return (min(255, int(r * factor)), min(255, int(g * factor)), min(255, int(b * factor)))

    def reset_score(self):
        self.score = 0

    def move(self, up=False, down=False):
        if up and self.rect.top > 0:
            self.rect.y -= self.speed
        if down and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed

    def ai_move(self, ball, difficulty):
        # AI logic to track the ball
        if self.is_ai:
            # Predict where the ball will be
            if ball.speed_x > 0:  # Only move if the ball is coming towards the AI
                # Add some imperfection to the AI based on difficulty
                if random.random() < difficulty / 10:
                    # Calculate target y position with some randomness
                    # Higher difficulties have less randomness
                    random_factor = int(40 - (difficulty * 3))
                    target_y = ball.rect.y - (self.rect.height / 2) + random.randint(-random_factor, random_factor)

                    # Move towards the target
                    if self.rect.y < target_y:
                        self.move(down=True)
                    elif self.rect.y > target_y:
                        self.move(up=True)
            else:
                # When ball is moving away, move towards center with some randomness
                center_y = HEIGHT / 2 - self.rect.height / 2
                if abs(self.rect.y - center_y) > self.speed:
                    if self.rect.y > center_y:
                        self.move(up=True)
                    else:
                        self.move(down=True)

    def draw(self):
        # Draw shadow (3D effect)
        shadow_rect = pygame.Rect(
            self.rect.x + self.shadow_depth,
            self.rect.y + self.shadow_depth,
            self.rect.width,
            self.rect.height
        )
        pygame.draw.rect(screen, self.shadow_color, shadow_rect)

        # Draw paddle
        pygame.draw.rect(screen, self.color, self.rect)

        # Draw highlight (3D effect)
        highlight_rect = pygame.Rect(
            self.rect.x + 2,
            self.rect.y + 2,
            self.rect.width - 4,
            self.rect.height - 4
        )
        pygame.draw.rect(screen, self.darken_color(self.color, 1.2), highlight_rect)

class Ball:
    def __init__(self, x, y, size, color, speed):
        self.rect = pygame.Rect(x, y, size, size)
        self.color = color
        self.speed_x = speed
        self.speed_y = speed
        self.reset()
        # 3D effect attributes
        self.shadow_depth = 5
        self.shadow_color = self.darken_color(color, 0.5)
        self.highlight_color = self.lighten_color(color, 1.3)
        self.z_position = 0  # For 3D effect
        self.z_speed = 0.2
        self.max_z = 10

    def darken_color(self, color, factor):
        r, g, b = color
        return (min(255, int(r * factor)), min(255, int(g * factor)), min(255, int(b * factor)))

    def lighten_color(self, color, factor):
        r, g, b = color
        return (min(255, int(r * factor)), min(255, int(g * factor)), min(255, int(b * factor)))

    def reset(self):
        # Determine who scored last to decide where to start the ball
        if hasattr(self, 'last_scorer') and self.last_scorer == 'ai':
            # Start from AI side (right)
            self.rect.x = WIDTH - 100 - BALL_SIZE // 2
            self.rect.y = HEIGHT // 2 - BALL_SIZE // 2
            self.speed_x = -BALL_SPEED  # Always move toward player first
        elif hasattr(self, 'last_scorer') and self.last_scorer == 'player':
            # Start from player side (left)
            self.rect.x = 100 - BALL_SIZE // 2
            self.rect.y = HEIGHT // 2 - BALL_SIZE // 2
            self.speed_x = BALL_SPEED  # Always move toward AI first
        else:
            # First serve of the game, randomly choose a side
            if random.choice([True, False]):
                # Start from AI side
                self.rect.x = WIDTH - 100 - BALL_SIZE // 2
                self.rect.y = HEIGHT // 2 - BALL_SIZE // 2
                self.speed_x = -BALL_SPEED
            else:
                # Start from player side
                self.rect.x = 100 - BALL_SIZE // 2
                self.rect.y = HEIGHT // 2 - BALL_SIZE // 2
                self.speed_x = BALL_SPEED

        # Randomize y direction
        self.speed_y = BALL_SPEED * random.choice([-0.7, -0.3, 0.3, 0.7])
        self.z_position = 0

    def move(self, player_paddle, ai_paddle):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # 3D effect - ball moves in z-axis
        self.z_position += self.z_speed
        if self.z_position > self.max_z or self.z_position < 0:
            self.z_speed *= -1

        # Bounce off top and bottom
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.speed_y *= -1
            if sounds_enabled:
                wall_hit_sound.play()

        # Score points and reset if ball goes out of bounds
        if self.rect.left <= 0:
            ai_paddle.score += 1
            if sounds_enabled:
                score_sound.play()
            self.last_scorer = 'ai'
            self.reset()
            return True
        elif self.rect.right >= WIDTH:
            player_paddle.score += 1
            if sounds_enabled:
                score_sound.play()
            self.last_scorer = 'player'
            self.reset()
            return True
        return False

    def collide(self, paddle):
        if self.rect.colliderect(paddle.rect):
            # Play sound
            if sounds_enabled:
                paddle_hit_sound.play()

            # Calculate bounce angle based on where the ball hits the paddle
            relative_intersect_y = (paddle.rect.y + paddle.rect.height / 2) - (self.rect.y + self.rect.height / 2)
            normalized_relative_intersect_y = relative_intersect_y / (paddle.rect.height / 2)
            bounce_angle = normalized_relative_intersect_y * (math.pi / 4)  # Max 45 degrees

            # Reverse x direction and adjust y based on bounce angle
            if self.rect.x < WIDTH // 2:  # Left paddle
                self.speed_x = abs(self.speed_x)
                self.speed_y = -BALL_SPEED * math.sin(bounce_angle)
            else:  # Right paddle
                self.speed_x = -abs(self.speed_x)
                self.speed_y = -BALL_SPEED * math.sin(bounce_angle)

            # Slightly increase speed to make game progressively harder
            self.speed_x *= 1.05
            if abs(self.speed_x) > 15:
                self.speed_x = 15 if self.speed_x > 0 else -15

            # Change z-direction for 3D effect
            self.z_speed *= -1

    def draw(self):
        # Calculate size based on z-position for 3D effect
        size_factor = 1 + (self.z_position / 50)
        current_size = int(BALL_SIZE * size_factor)

        # Adjust position to keep ball centered with new size
        x_offset = (current_size - BALL_SIZE) // 2
        y_offset = (current_size - BALL_SIZE) // 2

        # Draw shadow (3D effect)
        shadow_rect = pygame.Rect(
            self.rect.x + self.shadow_depth - x_offset,
            self.rect.y + self.shadow_depth - y_offset,
            current_size,
            current_size
        )
        pygame.draw.ellipse(screen, self.shadow_color, shadow_rect)

        # Draw ball
        ball_rect = pygame.Rect(
            self.rect.x - x_offset,
            self.rect.y - y_offset,
            current_size,
            current_size
        )
        pygame.draw.ellipse(screen, self.color, ball_rect)

        # Draw highlight (3D effect)
        highlight_size = int(current_size * 0.5)
        highlight_rect = pygame.Rect(
            self.rect.x - x_offset + int(current_size * 0.25),
            self.rect.y - y_offset + int(current_size * 0.25),
            highlight_size,
            highlight_size
        )
        pygame.draw.ellipse(screen, self.highlight_color, highlight_rect)

class Court:
    def __init__(self):
        self.color = LIGHT_BLUE
        self.line_color = WHITE
        self.shadow_color = GRAY
        self.shadow_depth = 15

    def draw(self):
        # Draw court shadow (3D effect)
        shadow_rect = pygame.Rect(
            self.shadow_depth,
            self.shadow_depth,
            WIDTH - (2 * self.shadow_depth),
            HEIGHT - (2 * self.shadow_depth)
        )
        pygame.draw.rect(screen, self.shadow_color, shadow_rect)

        # Draw court
        court_rect = pygame.Rect(0, 0, WIDTH, HEIGHT)
        pygame.draw.rect(screen, self.color, court_rect)

        # Draw court lines
        pygame.draw.rect(screen, self.line_color, court_rect, 5)

        # Draw net with 3D effect
        net_shadow_x = WIDTH // 2 + 2
        for y in range(0, HEIGHT, 30):
            # Draw net shadow
            pygame.draw.rect(screen, GRAY, (net_shadow_x, y + 5, 4, 15))
            # Draw net
            pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 2, y, 4, 15))

def show_message(message, size=36, y_offset=0, color=WHITE, wait_time=0):
    font = pygame.font.Font(None, size)
    text = font.render(message, True, color)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset))

    # Add shadow for 3D text effect
    shadow_text = font.render(message, True, (50, 50, 50))
    shadow_rect = shadow_text.get_rect(center=(WIDTH // 2 + 3, HEIGHT // 2 + y_offset + 3))
    screen.blit(shadow_text, shadow_rect)

    screen.blit(text, text_rect)
    pygame.display.flip()
    if wait_time > 0:
        time.sleep(wait_time)

def show_difficulty_screen(difficulty):
    # Create gradient background
    for y in range(HEIGHT):
        color_value = int(255 * (1 - y / HEIGHT))
        color = (0, 0, color_value)
        pygame.draw.line(screen, color, (0, y), (WIDTH, y))

    # Draw 3D title
    font_large = pygame.font.Font(None, 72)
    title_text = "PICKLE BALL 3D"

    # Draw multiple layers for 3D effect
    for i in range(5, 0, -1):
        title_shadow = font_large.render(title_text, True, (i*20, i*20, i*50))
        title_rect = title_shadow.get_rect(center=(WIDTH // 2, 100 + i*2))
        screen.blit(title_shadow, title_rect)

    title = font_large.render(title_text, True, YELLOW)
    title_rect = title.get_rect(center=(WIDTH // 2, 100))
    screen.blit(title, title_rect)

    # Draw difficulty with 3D effect
    show_message(f"DIFFICULTY LEVEL: {difficulty}", 48, -50, YELLOW)
    show_message("First to score 20 points wins!", 36, 0)
    show_message("Use UP and DOWN arrow keys to move", 30, 50)
    show_message("Press SPACE to start", 30, 100)

    # Draw 3D ball animation
    ball_pos = [WIDTH // 2, HEIGHT - 100]
    ball_size = 30
    ball_shadow = 8

    # Animate the ball
    for i in range(20):
        # Clear previous ball
        pygame.draw.rect(screen, BLACK, (ball_pos[0] - ball_size - 10, ball_pos[1] - ball_size - 10, ball_size * 2 + 20, ball_size * 2 + 20))

        # Update position with bouncing effect
        ball_pos[1] = HEIGHT - 100 + int(20 * math.sin(i * 0.3))

        # Draw ball shadow
        pygame.draw.ellipse(screen, GRAY, (ball_pos[0] - ball_size + ball_shadow, ball_pos[1] - ball_size + ball_shadow, ball_size * 2, ball_size * 2))

        # Draw ball
        pygame.draw.ellipse(screen, GREEN, (ball_pos[0] - ball_size, ball_pos[1] - ball_size, ball_size * 2, ball_size * 2))

        # Draw highlight
        pygame.draw.ellipse(screen, (200, 255, 200), (ball_pos[0] - ball_size//2, ball_pos[1] - ball_size//2, ball_size, ball_size))

        pygame.display.flip()
        pygame.time.delay(50)

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

def show_game_over(player_score, ai_score, difficulty):
    # Create gradient background
    for y in range(HEIGHT):
        if player_score >= MAX_SCORE:
            # Victory gradient (blue to green)
            color_value_b = int(255 * (1 - y / HEIGHT))
            color_value_g = int(200 * (y / HEIGHT))
            color = (0, color_value_g, color_value_b)
        else:
            # Defeat gradient (blue to red)
            color_value_b = int(255 * (1 - y / HEIGHT))
            color_value_r = int(200 * (y / HEIGHT))
            color = (color_value_r, 0, color_value_b)
        pygame.draw.line(screen, color, (0, y), (WIDTH, y))

    if player_score >= MAX_SCORE:
        if sounds_enabled:
            win_sound.play()
        show_message("YOU WIN!", 64, -50, GREEN)
        if difficulty < 10:
            show_message(f"Advancing to difficulty level {difficulty + 1}", 36, 20)
            show_message("Press SPACE to continue", 30, 80)
        else:
            show_message("Congratulations! You beat the highest difficulty!", 36, 20)
            show_message("Press SPACE to play again", 30, 80)
    else:
        if sounds_enabled:
            lose_sound.play()
        show_message("GAME OVER", 64, -50, RED)
        show_message(f"AI wins with {ai_score} points", 36, 20)
        show_message("Press SPACE to try again", 30, 80)

    # Draw 3D trophy or sad face
    if player_score >= MAX_SCORE:
        # Draw trophy
        pygame.draw.polygon(screen, YELLOW, [
            (WIDTH//2 - 40, HEIGHT - 150),
            (WIDTH//2 + 40, HEIGHT - 150),
            (WIDTH//2 + 30, HEIGHT - 100),
            (WIDTH//2 - 30, HEIGHT - 100)
        ])
        pygame.draw.rect(screen, YELLOW, (WIDTH//2 - 10, HEIGHT - 100, 20, 50))
        pygame.draw.rect(screen, YELLOW, (WIDTH//2 - 50, HEIGHT - 50, 100, 10))
    else:
        # Draw sad face
        pygame.draw.circle(screen, RED, (WIDTH//2, HEIGHT - 120), 40)
        pygame.draw.circle(screen, BLACK, (WIDTH//2 - 15, HEIGHT - 130), 5)
        pygame.draw.circle(screen, BLACK, (WIDTH//2 + 15, HEIGHT - 130), 5)
        pygame.draw.arc(screen, BLACK, (WIDTH//2 - 20, HEIGHT - 110, 40, 30), math.pi, 2*math.pi, 3)

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

def main():
    difficulty = 1  # Start at difficulty level 1
    court = Court()

    while True:
        # Create game objects
        player_paddle = Paddle(20, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT, BLUE, PADDLE_SPEED)
        ai_paddle = Paddle(WIDTH - 20 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT, RED, PADDLE_SPEED, is_ai=True)
        ball = Ball(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, GREEN, BALL_SPEED)

        # Show difficulty screen
        show_difficulty_screen(difficulty)

        # Font for score display
        font = pygame.font.Font(None, 36)

        # Main game loop
        running = True
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Get keyboard state
            keys = pygame.key.get_pressed()

            # Player controls (Arrow Up, Arrow Down)
            player_paddle.move(up=keys[pygame.K_UP], down=keys[pygame.K_DOWN])

            # AI movement with current difficulty
            ai_paddle.ai_move(ball, difficulty)

            # Move the ball
            point_scored = ball.move(player_paddle, ai_paddle)

            # Check for collisions
            ball.collide(player_paddle)
            ball.collide(ai_paddle)

            # Check for game over
            if player_paddle.score >= MAX_SCORE or ai_paddle.score >= MAX_SCORE:
                running = False

            # Draw everything
            screen.fill(BLACK)

            # Draw the court with 3D effect
            court.draw()

            # Draw paddles and ball
            player_paddle.draw()
            ai_paddle.draw()
            ball.draw()

            # Draw scores with shadow for 3D effect
            score_font = pygame.font.Font(None, 48)

            # Player score
            player_score_shadow = score_font.render(str(player_paddle.score), True, (50, 50, 50))
            player_score_text = score_font.render(str(player_paddle.score), True, WHITE)
            screen.blit(player_score_shadow, (WIDTH // 4 + 2, 22))
            screen.blit(player_score_text, (WIDTH // 4, 20))

            # AI score
            ai_score_shadow = score_font.render(str(ai_paddle.score), True, (50, 50, 50))
            ai_score_text = score_font.render(str(ai_paddle.score), True, WHITE)
            screen.blit(ai_score_shadow, (3 * WIDTH // 4 + 2, 22))
            screen.blit(ai_score_text, (3 * WIDTH // 4, 20))

            # Draw player labels with 3D effect
            label_font = pygame.font.Font(None, 36)

            # Player label
            player_label_shadow = label_font.render("YOU", True, (50, 50, 50))
            player_label = label_font.render("YOU", True, BLUE)
            screen.blit(player_label_shadow, (WIDTH // 4 - 18, 52))
            screen.blit(player_label, (WIDTH // 4 - 20, 50))

            # AI label
            ai_label_shadow = label_font.render("AI", True, (50, 50, 50))
            ai_label = label_font.render("AI", True, RED)
            screen.blit(ai_label_shadow, (3 * WIDTH // 4 - 8, 52))
            screen.blit(ai_label, (3 * WIDTH // 4 - 10, 50))

            # Level indicator in center
            level_shadow = label_font.render(f"LEVEL {difficulty}", True, (50, 50, 50))
            level_text = label_font.render(f"LEVEL {difficulty}", True, YELLOW)
            screen.blit(level_shadow, (WIDTH // 2 - level_text.get_width() // 2 + 2, 52))
            screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, 50))

            # Update the display
            pygame.display.flip()

            # Cap the frame rate
            clock.tick(60)

        # Game over, show results
        show_game_over(player_paddle.score, ai_paddle.score, difficulty)

        # If player won, increase difficulty for next level
        if player_paddle.score >= MAX_SCORE:
            if difficulty < 10:
                difficulty += 1

if __name__ == "__main__":
    main()