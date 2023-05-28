import pygame
import sys
from pygame.locals import QUIT, KEYDOWN, MOUSEBUTTONDOWN, USEREVENT
from random import randint
import os
import math
import pygame.mixer

# Constants
BG_COLOR = (0, 0, 0)
PL_COLOR = (75, 23, 49)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GOLD = (255, 215, 0)
PL_SPEED = 7
EN_SPEED = 15
SPAWN_INTERVAL = 150
BULLET_SPEED = 500
WIDTH = 1000
HEIGHT = 600

pygame.mixer.init()
slide_sound = pygame.mixer.Sound("./cartoon-slide.mp3")
slide_sound.set_volume(0.1)

# Initialize pygame
pygame.init()
DISPLAYSURF = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Hello World!')

# Load images
player_img = pygame.image.load(os.path.join("./ecco.png")).convert_alpha()
player_img = pygame.transform.scale(player_img, (50, 50))

bullet_img = pygame.image.load(os.path.join("./e.jpg")).convert_alpha()
bullet_img = pygame.transform.scale(bullet_img, (25, 25))

enemie_img = pygame.image.load(os.path.join("./pepe.png")).convert_alpha()
enemie_img = pygame.transform.scale(enemie_img, (25, 25))

enemie2_img = pygame.image.load(os.path.join("./pepe1.png")).convert_alpha()
enemie2_img = pygame.transform.scale(enemie2_img, (25, 25))

bg_image = pygame.image.load(os.path.join("./version_2.png")).convert_alpha()
bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))

# Fonts
font = pygame.font.Font('freesansbold.ttf', 32)

# Game variables
score = 0

# Rectangles
score_text = font.render(str(score), True, WHITE).get_rect()
score_text.top = 25
score_text.left = 25

# Classes

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 50)
        self.image = player_img
        self.bullets = []
        self.direction = 0

    def fire_bullet(self):
        x, y = self.rect.left, self.rect.top

        cursor_pos = pygame.mouse.get_pos()
        dx = cursor_pos[0] - x
        dy = cursor_pos[1] - y
        angle = math.atan2(dy, dx) * 180 / math.pi
        rad_angle = math.radians(angle)
        direction = [math.cos(rad_angle), math.sin(rad_angle)]

        bullet = Bullet(x, y, direction)
        bullet.fired = True
        self.bullets.append(bullet)

    def move(self, keys, dt):
        _direction = self.direction
        if keys[pygame.K_d]:
            self.rect.x += (PL_SPEED )
            self.direction = -1
        if keys[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= (PL_SPEED)
            self.direction = 1

        if self.direction != _direction:
            slide_sound.stop()
            slide_sound.play(loops=0)



class Enemie:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 50)
        self.spez = 0 if randint(0, 10) < 7 else 1
        self.image = enemie2_img if self.spez else enemie_img


class Bullet:
    def __init__(self, x, y, direction):
        self.rect = pygame.Rect(x, y, 10, 10)
        self.image = bullet_img
        self.direction = direction
        self.fired = False


# Game states
class GameState:
    def __init__(self):
        self.state = "start"

    def start(self):
        self.state = "start"
        self.reset()

    def play(self):
        self.state = "play"
        self.reset()

    def game_over(self):
        self.state = "game_over"

    def reset(self):
        self.player = Player(150, HEIGHT - 65)
        self.bullets = []
        self.enemies = []
        self.score = 0

    def update(self, frame, DT):
        if self.state == "start":
            self.update_start()
        elif self.state == "play":
            self.update_play(frame, dt)
        elif self.state == "game_over":
            self.update_game_over()

    def update_start(self):
        pygame.draw.rect(DISPLAYSURF, BG_COLOR,
                         pygame.Rect(0, 0, WIDTH, HEIGHT))

        start_text = font.render("Press Enter to Start", True, WHITE)
        start_rect = start_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        DISPLAYSURF.blit(start_text, start_rect)

        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.play()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            elif event.type == QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.flip()

    def update_play(self, frame, dt):
        DISPLAYSURF.blit(bg_image, pygame.Rect(0, 0, WIDTH, HEIGHT))

        for enemie in self.enemies:
            enemie.rect.top += EN_SPEED / 2
            DISPLAYSURF.blit(enemie.image, enemie.rect)

            if enemie.rect.colliderect(self.player.rect):
                self.game_over()

            if enemie.spez:
                for bullet in self.player.bullets:
                    if bullet.rect.colliderect(enemie.rect):
                        self.enemies.remove(enemie)
                        self.score += 10

            if enemie.rect.top > HEIGHT:
                self.enemies.remove(enemie)
                self.score += 1

        for bullet in self.player.bullets:
            bullet.rect.x += bullet.direction[0] * BULLET_SPEED * dt
            bullet.rect.y += bullet.direction[1] * BULLET_SPEED * dt
            DISPLAYSURF.blit(bullet.image, bullet.rect)

        DISPLAYSURF.blit(self.player.image, self.player.rect)

        text = font.render(str(self.score), True, WHITE)
        DISPLAYSURF.blit(text, score_text)

        keys = pygame.key.get_pressed()
        self.player.move(keys, dt)

        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            elif event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                self.player.fire_bullet()
            elif event.type == SPAWN_EVENT:
                self.enemies.append(Enemie(randint(0, WIDTH), -50))

        pygame.display.flip()

    def update_game_over(self):
        pygame.draw.rect(DISPLAYSURF, BG_COLOR,
                         pygame.Rect(0, 0, WIDTH, HEIGHT))


        game_over_text = font.render("Game Over", True, WHITE)
        game_over_rect = game_over_text.get_rect(
            center=(WIDTH // 2, HEIGHT // 2 - 50))
        DISPLAYSURF.blit(game_over_text, game_over_rect)

        restart_text = font.render("Press enter to restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        DISPLAYSURF.blit(restart_text, restart_rect)

        score_text = font.render(f"Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        DISPLAYSURF.blit(score_text, score_rect)

        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_RETURN:
                    self.start()
            elif event.type == QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.flip()


game_state = GameState()
SPAWN_EVENT = USEREVENT + 1

pygame.time.set_timer(SPAWN_EVENT, SPAWN_INTERVAL)

clock = pygame.time.Clock()
frame = 0
while True:
    dt = clock.tick(60) / 1000.0  # Get delta time in seconds
    game_state.update(frame, dt)
    frame += 1

