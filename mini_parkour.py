import pygame
import random
import sys

# Mini Parkour: a simple run-and-jump platform game.
# Install Pygame with: python -m pip install pygame
# Run with: python mini_parkour.py

pygame.init()

WIDTH, HEIGHT = 1000, 600
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini Parkour")
clock = pygame.time.Clock()

# Colors
SKY = (135, 206, 235)
WHITE = (255, 255, 255)
BLACK = (25, 25, 35)
GREEN = (55, 190, 95)
DARK_GREEN = (35, 145, 70)
RED = (235, 75, 75)
GOLD = (255, 210, 65)
BLUE = (60, 110, 230)
GRAY = (100, 105, 120)

font = pygame.font.SysFont("arial", 24, bold=True)
small_font = pygame.font.SysFont("arial", 18)
big_font = pygame.font.SysFont("arial", 48, bold=True)

PLAYER_W, PLAYER_H = 34, 48
GRAVITY = 0.65
JUMP_SPEED = -13.5
MOVE_SPEED = 5

platforms = [
    pygame.Rect(0, 540, 260, 60),
    pygame.Rect(330, 485, 130, 22),
    pygame.Rect(520, 425, 120, 22),
    pygame.Rect(700, 360, 130, 22),
    pygame.Rect(900, 300, 150, 22),
    pygame.Rect(1100, 365, 120, 22),
    pygame.Rect(1290, 430, 140, 22),
    pygame.Rect(1510, 370, 140, 22),
    pygame.Rect(1730, 310, 150, 22),
    pygame.Rect(1960, 390, 170, 22),
    pygame.Rect(2200, 460, 180, 22),
    pygame.Rect(2450, 400, 150, 22),
    pygame.Rect(2670, 330, 180, 22),
    pygame.Rect(2950, 270, 210, 22),
    pygame.Rect(3260, 350, 200, 22),
    pygame.Rect(3560, 430, 220, 22),
    pygame.Rect(3890, 370, 180, 22),
    pygame.Rect(4200, 300, 250, 22),
]
world_end = 4450

player = pygame.Rect(70, 492, PLAYER_W, PLAYER_H)
player_x = float(player.x)
player_y = float(player.y)
vel_y = 0
on_ground = False
camera_x = 0
checkpoint_x = 70
deaths = 0
won = False

# A few moving hazards add a little parkour challenge.
hazards = [
    pygame.Rect(570, 393, 30, 32),
    pygame.Rect(1515, 338, 30, 32),
    pygame.Rect(2710, 298, 30, 32),
]
hazard_origins = [h.x for h in hazards]
hazard_offsets = [0, 1.8, 1.2]

def draw_text(text, x, y, color=BLACK, use_font=font):
    image = use_font.render(text, True, color)
    screen.blit(image, (x, y))

def reset_player():
    global player_x, player_y, vel_y, on_ground, deaths, won
    player_x = float(checkpoint_x)
    player_y = 492.0 if checkpoint_x == 70 else 280.0
    vel_y = 0
    on_ground = False
    deaths += 1
    won = False

def draw_background():
    screen.fill(SKY)
    # Simple clouds
    for cx, cy in [(120, 90), (380, 140), (690, 80), (900, 160)]:
        x = int((cx - camera_x * 0.25) % (WIDTH + 180)) - 90
        pygame.draw.circle(screen, WHITE, (x, cy), 22)
        pygame.draw.circle(screen, WHITE, (x + 25, cy - 8), 27)
        pygame.draw.circle(screen, WHITE, (x + 52, cy), 20)
    # Distant hills
    for i in range(-1, 7):
        hx = i * 240 - int(camera_x * 0.15)
        pygame.draw.ellipse(screen, (105, 190, 140), (hx, 465, 340, 180))

def draw_player():
    px = int(player_x - camera_x)
    py = int(player_y)
    # Character body and head
    pygame.draw.rect(screen, BLUE, (px, py + 13, PLAYER_W, PLAYER_H - 13), border_radius=7)
    pygame.draw.circle(screen, (255, 210, 170), (px + PLAYER_W // 2, py + 9), 12)
    pygame.draw.circle(screen, BLACK, (px + 10, py + 7), 2)
    pygame.draw.circle(screen, BLACK, (px + 23, py + 7), 2)

def draw_world():
    for p in platforms:
        r = pygame.Rect(p.x - camera_x, p.y, p.width, p.height)
        if r.right >= 0 and r.left <= WIDTH:
            pygame.draw.rect(screen, DARK_GREEN, (r.x, r.y + 7, r.width, r.height), border_radius=5)
            pygame.draw.rect(screen, GREEN, r, border_radius=5)
            pygame.draw.line(screen, (130, 240, 150), (r.x + 5, r.y + 3), (r.right - 5, r.y + 3), 3)
    for h in hazards:
        r = pygame.Rect(h.x - camera_x, h.y, h.width, h.height)
        if -50 < r.x < WIDTH + 50:
            pygame.draw.rect(screen, RED, r, border_radius=5)
            pygame.draw.circle(screen, WHITE, (r.x + 9, r.y + 10), 3)
            pygame.draw.circle(screen, WHITE, (r.x + 21, r.y + 10), 3)

def update_hazards():
    for i, h in enumerate(hazards):
        h.x = hazard_origins[i] + int(55 * pygame.math.Vector2(1, 0).x * __import__("math").sin(pygame.time.get_ticks() / 500 + i))

def main():
    global player, player_x, player_y, vel_y, on_ground, camera_x, checkpoint_x, won
    running = True
    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w) and on_ground and not won:
                    vel_y = JUMP_SPEED
                    on_ground = False
                if event.key == pygame.K_r:
                    player_x, player_y, vel_y = 70.0, 492.0, 0
                    checkpoint_x = 70
                    won = False

        keys = pygame.key.get_pressed()
        if not won:
            move = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                move -= MOVE_SPEED
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                move += MOVE_SPEED
            player_x += move

            # Horizontal bounds
            player_x = max(0, min(player_x, world_end - PLAYER_W))

            # Vertical physics
            previous_bottom = player_y + PLAYER_H
            vel_y += GRAVITY
            player_y += vel_y
            on_ground = False

            player_rect = pygame.Rect(round(player_x), round(player_y), PLAYER_W, PLAYER_H)
            for p in platforms:
                if player_rect.colliderect(p) and vel_y >= 0 and previous_bottom <= p.top + 8:
                    player_y = p.top - PLAYER_H
                    vel_y = 0
                    on_ground = True
                    player_rect.y = round(player_y)

            # Checkpoints on selected platforms
            if player_x > 1960 and checkpoint_x < 1960 and on_ground:
                checkpoint_x = 1980
            if player_x > 3260 and checkpoint_x < 3260 and on_ground:
                checkpoint_x = 3280

            # Hazards
            for h in hazards:
                if player_rect.colliderect(h):
                    reset_player()
                    break

            if player_y > HEIGHT + 120:
                reset_player()

            if player_x >= world_end - 100 and on_ground:
                won = True

        camera_x = max(0, min(player_x - WIDTH * 0.32, world_end - WIDTH))
        draw_background()
        draw_world()
        draw_player()

        # HUD
        draw_text("MINI PARKOUR", 20, 18, BLACK)
        draw_text("Move: A/D or ←/→    Jump: SPACE / W / ↑", 20, 52, BLACK, small_font)
        draw_text(f"Falls: {deaths}", 20, 80, BLACK, small_font)
        if checkpoint_x > 70:
            draw_text("Checkpoint saved!", WIDTH - 230, 20, GOLD, small_font)

        if won:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((15, 20, 35, 170))
            screen.blit(overlay, (0, 0))
            title = big_font.render("YOU FINISHED!", True, GOLD)
            subtitle = font.render("Press R to play again", True, WHITE)
            screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 25)))
            screen.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30)))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
