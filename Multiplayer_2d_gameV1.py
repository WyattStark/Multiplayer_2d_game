import pygame
import math
import random
import time

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Stickman Shooter")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)

# Player settings
player_pos = [WIDTH // 2, HEIGHT // 2]
player_radius = 20
player_speed = 5
player_health = 100

# Weapon settings
weapons = {
    'ar': {'fire_rate': 0.15, 'damage': 10, 'bullet_speed': 10, 'color': BLUE},
    'pistol': {'fire_rate': 0.5, 'damage': 25, 'bullet_speed': 12, 'color': RED}
}
current_weapon = 'ar'
last_shot = 0

# Bullet and enemy settings
bullets = []
enemies = []
enemy_spawn_rate = 2  # Seconds
last_spawn = 0
enemy_speed = 2
enemy_radius = 15
enemy_health = 50
enemy_damage = 10

# Game state
score = 0
game_over = False
font = pygame.font.SysFont('arial', 24)

# Bullet class
class Bullet:
    def __init__(self, x, y, angle, speed, damage, color):
        self.x = x
        self.y = y
        self.speed = speed
        self.damage = damage
        self.color = color
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
        self.radius = 5

    def move(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

# Enemy class
class Enemy:
    def __init__(self, x, y, health):
        self.x = x
        self.y = y
        self.health = health
        self.radius = enemy_radius

    def move_toward_player(self):
        angle = math.atan2(player_pos[1] - self.y, player_pos[0] - self.x)
        self.x += math.cos(angle) * enemy_speed
        self.y += math.sin(angle) * enemy_speed

    def draw(self):
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius)

# Main game loop
clock = pygame.time.Clock()
running = True
while running:
    screen.fill(GRAY)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q and not game_over:
                current_weapon = 'pistol' if current_weapon == 'ar' else 'ar'
            if event.key == pygame.K_r and game_over:
                # Reset game
                player_pos = [WIDTH // 2, HEIGHT // 2]
                player_health = 100
                bullets = []
                enemies = []
                score = 0
                game_over = False
                last_spawn = time.time()
                last_shot = 0

    if not game_over:
        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and player_pos[1] > player_radius:
            player_pos[1] -= player_speed
        if keys[pygame.K_s] and player_pos[1] < HEIGHT - player_radius:
            player_pos[1] += player_speed
        if keys[pygame.K_a] and player_pos[0] > player_radius:
            player_pos[0] -= player_speed
        if keys[pygame.K_d] and player_pos[0] < WIDTH - player_radius:
            player_pos[0] += player_speed

        # Aiming and shooting
        mouse_pos = pygame.mouse.get_pos()
        angle = math.atan2(mouse_pos[1] - player_pos[1], mouse_pos[0] - player_pos[0])
        current_time = time.time()
        if pygame.mouse.get_pressed()[0] and current_time - last_shot >= weapons[current_weapon]['fire_rate']:
            bullet = Bullet(
                player_pos[0], player_pos[1], angle,
                weapons[current_weapon]['bullet_speed'],
                weapons[current_weapon]['damage'],
                weapons[current_weapon]['color']
            )
            bullets.append(bullet)
            last_shot = current_time

        # Spawn enemies
        if current_time - last_spawn >= enemy_spawn_rate:
            side = random.choice(['top', 'bottom', 'left', 'right'])
            if side == 'top':
                x, y = random.randint(0, WIDTH), 0
            elif side == 'bottom':
                x, y = random.randint(0, WIDTH), HEIGHT
            elif side == 'left':
                x, y = 0, random.randint(0, HEIGHT)
            else:
                x, y = WIDTH, random.randint(0, HEIGHT)
            enemies.append(Enemy(x, y, enemy_health))
            last_spawn = current_time

        # Update bullets
        for bullet in bullets[:]:
            bullet.move()
            if bullet.x < 0 or bullet.x > WIDTH or bullet.y < 0 or bullet.y > HEIGHT:
                bullets.remove(bullet)
                continue
            # Check bullet-enemy collisions
            for enemy in enemies[:]:
                distance = math.hypot(bullet.x - enemy.x, bullet.y - enemy.y)
                if distance < bullet.radius + enemy.radius:
                    enemy.health -= bullet.damage
                    bullets.remove(bullet)
                    if enemy.health <= 0:
                        enemies.remove(enemy)
                        score += 10
                    break

        # Update enemies
        for enemy in enemies[:]:
            enemy.move_toward_player()
            distance = math.hypot(player_pos[0] - enemy.x, player_pos[1] - enemy.y)
            if distance < player_radius + enemy.radius:
                player_health -= enemy_damage
                enemies.remove(enemy)
                if player_health <= 0:
                    game_over = True

        # Draw player
        pygame.draw.circle(screen, BLACK, (int(player_pos[0]), int(player_pos[1])), player_radius)
        # Draw gun barrel
        barrel_length = 30
        gun_x = player_pos[0] + math.cos(angle) * barrel_length
        gun_y = player_pos[1] + math.sin(angle) * barrel_length
        pygame.draw.line(screen, BLACK, player_pos, (gun_x, gun_y), 5)

        # Draw bullets and enemies
        for bullet in bullets:
            bullet.draw()
        for enemy in enemies:
            enemy.draw()

        # Draw HUD
        health_text = font.render(f'Health: {player_health}', True, BLACK)
        score_text = font.render(f'Score: {score}', True, BLACK)
        weapon_text = font.render(f'Weapon: {current_weapon.upper()}', True, BLACK)
        screen.blit(health_text, (10, 10))
        screen.blit(score_text, (10, 40))
        screen.blit(weapon_text, (10, 70))

    if game_over:
        game_over_text = font.render('Game Over! Press R to Restart', True, BLACK)
        screen.blit(game_over_text, (WIDTH // 2 - 150, HEIGHT // 2))

    # Draw controls info
    controls_text = font.render('WASD: Move | Mouse: Aim | Click: Shoot | Q: Switch Weapon', True, BLACK)
    screen.blit(controls_text, (10, HEIGHT - 30))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
