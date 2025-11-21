import pygame
import random

pygame.init()

# --- Window setup ---
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Shooter Game")
clock = pygame.time.Clock()
FPS = 60

# --- Assets ---
player_img = pygame.transform.scale(pygame.image.load("assets/images/player/player.png"), (120, 120))
bullet_img = pygame.image.load("assets/images/icons/bullet.png")
enemy_img = pygame.transform.scale(pygame.image.load("assets/images/enemy/enemy.png"), (120, 120))
gunshot = pygame.mixer.Sound("assets/sounds/gunshot.wav")
reload_sound = pygame.mixer.Sound("assets/sounds/reload.wav")
gunshot.set_volume(1.0)
reload_sound.set_volume(1.0)

# --- Player setup ---
player_x, player_y = 50, 150
player_speed = 10
player_health = 200
lives = 3

# --- Enemy setup ---
enemy_group = []         
enemy_speeds = []       
enemy_healths = []       
enemy_collision_cooldowns = []  

def spawn_wave():
    count = random.randint(3, 5)
    for i in range(count):
        attempts = 0
        y_pos = random.randint(50, HEIGHT - 150)
        while any(abs(y_pos - e[1]) < 180 for e in enemy_group) and attempts < 20:
            y_pos = random.randint(50, HEIGHT - 150)
            attempts += 1
        x_pos = WIDTH + i * 150
        enemy_group.append([x_pos, y_pos])

        speed = random.randint(3, 7)
        enemy_speeds.append(speed)
        if speed >= 6:
            health = 1
        elif speed >= 4:
            health = 2
        else:
            health = 3
        enemy_healths.append(health)
        enemy_collision_cooldowns.append(0)

spawn_wave()

# --- Shooting setup ---
ammo = 10
is_reloading = False
reload_start = 0
RELOAD_TIME = 1000
SHOT_COOLDOWN = 250
last_shot = 0
space_pressed = False
bullets = []
enemy_shooting = False


# --- Colors & Fonts ---
GREEN = (0, 150, 0)
font_small = pygame.font.SysFont(None, 36)
font_big = pygame.font.SysFont(None, 72)

# --- Game state ---
running = True
paused = False
score = 0

# --- Game loop ---
while running:
    current_time = pygame.time.get_ticks()
    dt = clock.get_time()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                paused = not paused
            elif event.key == pygame.K_r and not is_reloading and ammo < 10 and not paused:
                is_reloading = True
                reload_sound.play()
                reload_start = current_time
            elif event.key == pygame.K_SPACE and not space_pressed and not paused:
                space_pressed = True
                if ammo > 0 and not is_reloading and current_time - last_shot >= SHOT_COOLDOWN:
                    ammo -= 1
                    gunshot.play()
                    last_shot = current_time
                    bullets.append([player_x + 80, player_y - 10])
                    if ammo == 0:
                        is_reloading = True
                        reload_sound.play()
                        reload_start = current_time
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                space_pressed = False

    if paused:
        screen.fill(GREEN)
        pause_text = font_big.render("PAUSED", True, (255, 0, 0))
        screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2,
                                 HEIGHT//2 - pause_text.get_height()//2))
        pygame.display.flip()
        clock.tick(FPS)
        continue

    # --- Player movement ---
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        player_y = max(30, player_y - player_speed)
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        player_y = min(HEIGHT - 120, player_y + player_speed)

    player_rect = pygame.Rect(player_x, player_y, 120, 120)

    # --- Update enemies ---
    VIEW_LENGTH = 800 

    for i in range(len(enemy_group)-1, -1, -1):
        ex, ey = enemy_group[i]

        enemy_rect = pygame.Rect(ex, ey, 120, 120)

        view_rect = pygame.Rect(ex - VIEW_LENGTH, ey, VIEW_LENGTH, 120)

        # Player inside vision = stop
        if not view_rect.colliderect(player_rect):
            enemy_group[i][0] -= enemy_speeds[i]
            enemy_shooting = True

        # Remove enemy if fully off screen
        if enemy_group[i][0] < -120:
            enemy_group.pop(i)
            enemy_speeds.pop(i)
            enemy_healths.pop(i)
            enemy_collision_cooldowns.pop(i)

    # --- Bullet collision ---
    for i in range(len(enemy_group)-1, -1, -1):
        enemy_rect = pygame.Rect(enemy_group[i][0], enemy_group[i][1], 120, 120)
        for b in bullets[:]:
            bullet_rect = pygame.Rect(b[0], b[1], 20, 10)
            if enemy_rect.colliderect(bullet_rect):
                bullets.remove(b)
                enemy_healths[i] -= 1
                if enemy_healths[i] <= 0:
                    enemy_group.pop(i)
                    enemy_speeds.pop(i)
                    enemy_healths.pop(i)
                    enemy_collision_cooldowns.pop(i)
                    score += 1
                if bullet_rect.colliderect(player_rect):
                    player_health -= 10
                break

    # --- Next wave ---
    if len(enemy_group) == 0:
        spawn_wave()

    # --- Reload ---
    if is_reloading and current_time - reload_start >= RELOAD_TIME:
        ammo = 10
        is_reloading = False


    # --- Update bullets ---
    bullets = [[b[0] + 20, b[1]] for b in bullets if b[0] < WIDTH]

    # --- Draw everything ---
    screen.fill(GREEN)
    pygame.draw.line(screen, (200, 0, 0), (0, 40), (WIDTH, 40), 2)

    screen.blit(player_img, (player_x, player_y))
    for enemy in enemy_group:
        screen.blit(enemy_img, (enemy[0], enemy[1]))

    for b in bullets:
        screen.blit(bullet_img, b)

    pygame.draw.rect(screen, (255, 0, 0), (5, 5, 200, 25))
    pygame.draw.rect(screen, (0, 255, 0), (5, 5, 2 * player_health, 25))
    pygame.draw.rect(screen, (0, 0, 0), (5, 5, 200, 25), 2)

    screen.blit(font_small.render(f"Ammo: {ammo}", True, (255, 255, 255)), (300, 5))
    if is_reloading:
        screen.blit(font_small.render("Reloading...", True, (255, 255, 255)), (420, 5))
    score_text = font_small.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (WIDTH - score_text.get_width() - 10, 5))

    lives_text = font_small.render(f"Lives: {lives}", True, (255, 255, 255))
        

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
