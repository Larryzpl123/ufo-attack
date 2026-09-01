import pygame
import random
import math
import os

# import libraries

HIGHSCORE_FILE = "highscore.txt"

# load high score from highscore txt
def load_high_score():
    if os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE, "r") as f:
            try:
                return int(f.read())
            except:
                return 0
    return 0

# save highscore to highscore txt
def save_high_score(score):
    with open(HIGHSCORE_FILE, "w") as f:
        f.write(str(score))

# constants

high_score = load_high_score()

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

FPS = 60
PLAYER_SPEED = 10
BULLET_SPEED = 20
PLAYER_SHOOT_COOLDOWN = 10

UFO_SPEED_MIN = 2.5
UFO_SPEED_MAX = 10
UFO_EDGE_OFFSET = 20
UFO_VSPEED_MIN = 0.5
UFO_VSPEED_MAX = 2.0
UFO_VERTICAL_EDGE = 30

UFO_BULLET_SPEED = 5
UFO_ROCKET_SPEED = 20
UFO_BLADE_SPEED_MIN = 8
UFO_BLADE_SPEED_MAX = 32
UFO_BLADE_ANGLE_MIN = 225
UFO_BLADE_ANGLE_MAX = 315

MAX_DIFFICULTY = 35
DIFFICULTY_INTERVAL = 90
HIT_SCORE = 100

DOUBLE_SHOT_DURATION = 10 * FPS
POWERUP_SPEED = 2
POWERUP_DROP_CHANCE = 10
UFO_MAX_Y = HEIGHT // 2 # so ufo don't go too low

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("UFO Attack")
clock = pygame.time.Clock()

# try loading image assets

try:
    player_img = pygame.image.load("assets/player.png").convert_alpha()
    player_img = pygame.transform.scale(player_img, (50, 60))
    ufo_img = pygame.image.load("assets/ufo.png").convert_alpha()
    ufo_img = pygame.transform.scale(ufo_img, (70, 50))
    bullet_img = pygame.image.load("assets/player_bullet.png").convert_alpha()
    bullet_img = pygame.transform.scale(bullet_img, (8, 16))
    ufo_bullet_img = pygame.image.load("assets/ufo_bullet.png").convert_alpha()
    ufo_bullet_img = pygame.transform.scale(ufo_bullet_img, (10, 20))
    rocket_img = pygame.image.load("assets/ufo_rocket.png").convert_alpha()
    rocket_img = pygame.transform.scale(rocket_img, (12, 30))
    blade_img = pygame.image.load("assets/ufo_blade.png").convert_alpha()
    blade_img = pygame.transform.scale(blade_img, (16, 16))
except pygame.error:
    player_img = ufo_img = bullet_img = ufo_bullet_img = rocket_img = blade_img = None

# try loading sound effects

try:
    shoot_sound = pygame.mixer.Sound("assets/player_bullet.wav")
    hit_sound = pygame.mixer.Sound("assets/hit_ufo.wav")
except:
    shoot_sound = hit_sound = None

# font

font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 72)

# initial variables

player_x = player_y = 0
player_bullets = []
ufo_bullets = []
ufo_rockets = []
ufo_blades = []
powerups = []
ufo_x = ufo_y = 0
ufo_hspeed = 0
ufo_direction = 1
ufo_vy = 0
score = 0
difficulty = 0
frame_count = 0
can_shoot = True
shoot_timer = 0
game_over = False
double_shot = False
double_shot_timer = 0
ufo_alarm0 = ufo_alarm1 = ufo_alarm2 = ufo_alarm3 = 0
player_rect = pygame.Rect(0,0,50,60)

# helper functions

def draw_text(text, x, y, color=WHITE, font_obj=font):
    surf = font_obj.render(text, True, color)
    screen.blit(surf, (x, y))

def lengthdir_x(length, angle_deg):
    return length * math.cos(math.radians(angle_deg))

def lengthdir_y(length, angle_deg):
    return length * math.sin(math.radians(angle_deg))

def random_range(a, b):
    return random.uniform(a, b)

def random_int(a, b):
    return random.randint(a, b)

# initialize game

def reset_game():
    global player_x, player_y, player_bullets, ufo_bullets, ufo_rockets, ufo_blades
    global ufo_x, ufo_y, ufo_hspeed, ufo_direction, ufo_vy
    global score, difficulty, frame_count
    global can_shoot, shoot_timer, game_over
    global ufo_alarm0, ufo_alarm1, ufo_alarm2, ufo_alarm3
    global player_rect
    global powerups, double_shot, double_shot_timer

    player_x = WIDTH // 2 - 25
    player_y = HEIGHT - 100
    player_rect = pygame.Rect(player_x, player_y, 50, 60)
    can_shoot = True
    shoot_timer = 0
    player_bullets = []

    ufo_x = WIDTH // 2 - 35
    ufo_y = 50
    ufo_hspeed = 8
    ufo_direction = 1
    ufo_vy = random.uniform(UFO_VSPEED_MIN, UFO_VSPEED_MAX) * random.choice([-1, 1])

    ufo_bullets = []
    ufo_rockets = []
    ufo_blades = []

    ufo_alarm0 = 60
    ufo_alarm1 = 90
    ufo_alarm2 = 120
    ufo_alarm3 = DIFFICULTY_INTERVAL

    score = 0
    difficulty = 0
    frame_count = 0

    powerups = []
    double_shot = False
    double_shot_timer = 0

    game_over = False

reset_game()

# main loop when running 

running = True
while running:
    clock.tick(FPS)
    frame_count += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if game_over and event.key == pygame.K_r:
                reset_game()
                
    # when player living
    
    if not game_over:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and player_x < WIDTH - 50:
            player_x += PLAYER_SPEED
        if keys[pygame.K_UP] and player_y > 0:
            player_y -= PLAYER_SPEED
        if keys[pygame.K_DOWN] and player_y < HEIGHT - 60:
            player_y += PLAYER_SPEED
        player_rect.topleft = (player_x, player_y)

        # double shot power up

        if double_shot:
            double_shot_timer -= 1
            if double_shot_timer <= 0:
                double_shot = False

        # key board controls

        if keys[pygame.K_SPACE] and can_shoot:
            if double_shot:
                bx1 = player_x + 25 - 4 - 10
                bx2 = player_x + 25 - 4 + 10
                player_bullets.append([bx1, player_y - 10, 0, -BULLET_SPEED])
                player_bullets.append([bx2, player_y - 10, 0, -BULLET_SPEED])
            else:
                bx = player_x + 25 - 4
                player_bullets.append([bx, player_y - 10, 0, -BULLET_SPEED])
            can_shoot = False
            shoot_timer = PLAYER_SHOOT_COOLDOWN
            if shoot_sound:
                shoot_sound.play()

        # cooldown for shooting bullets

        if not can_shoot:
            shoot_timer -= 1
            if shoot_timer <= 0:
                can_shoot = True

        # ufo locaton and moving

        ufo_x += ufo_hspeed * ufo_direction
        ufo_y += ufo_vy

        if ufo_x <= UFO_EDGE_OFFSET or ufo_x + 70 >= WIDTH - UFO_EDGE_OFFSET:
            ufo_direction *= -1
            ufo_hspeed = random.uniform(UFO_SPEED_MIN, UFO_SPEED_MAX)
            ufo_x = max(UFO_EDGE_OFFSET, min(WIDTH - 70 - UFO_EDGE_OFFSET, ufo_x))

        if ufo_y <= UFO_VERTICAL_EDGE or ufo_y + 50 >= UFO_MAX_Y + UFO_VERTICAL_EDGE:
            ufo_vy *= -1
            ufo_vy = random.uniform(UFO_VSPEED_MIN, UFO_VSPEED_MAX) * (1 if ufo_vy > 0 else -1)
            ufo_y = max(UFO_VERTICAL_EDGE, min(HEIGHT - 50 - UFO_VERTICAL_EDGE, ufo_y))

        # ufo alarms for events of firing bullet, rocker and blades

        ufo_alarm0 -= 1
        if ufo_alarm0 <= 0:
            bx = ufo_x + 35 - 5
            by = ufo_y + 50
            ufo_bullets.append([bx, by, 0, UFO_BULLET_SPEED])
            countdown = random_int(40, 80) - difficulty
            ufo_alarm0 = max(10, countdown)

        ufo_alarm1 -= 1
        if ufo_alarm1 <= 0:
            rx = ufo_x + 35 - 6
            ry = ufo_y + 50
            # Rocket fires straight backward (opposite to UFO's horizontal direction)
            backward = -ufo_direction
            vx = backward * (UFO_ROCKET_SPEED * 0.5)  # half speed horizontally
            vy = UFO_ROCKET_SPEED
            ufo_rockets.append([rx, ry, vx, vy])
            countdown = random_int(60, 90) - difficulty
            ufo_alarm1 = max(10, countdown)

        ufo_alarm2 -= 1
        if ufo_alarm2 <= 0:
            angle = random_range(UFO_BLADE_ANGLE_MIN, UFO_BLADE_ANGLE_MAX)
            speed = random_range(UFO_BLADE_SPEED_MIN, UFO_BLADE_SPEED_MAX)
            vx = lengthdir_x(speed, angle)
            vy = lengthdir_y(speed, angle)
            bx = ufo_x + 35 - 8
            by = ufo_y + 50
            ufo_blades.append([bx, by, vx, vy])
            countdown = random_int(80, 120) - difficulty
            ufo_alarm2 = max(10, countdown)

        ufo_alarm3 -= 1
        if ufo_alarm3 <= 0:
            if difficulty < MAX_DIFFICULTY:
                difficulty += 1
            ufo_alarm3 = DIFFICULTY_INTERVAL

        for b in player_bullets[:]:
            b[0] += b[2]
            b[1] += b[3]
            if b[1] < 0 or b[0] < 0 or b[0] > WIDTH:
                player_bullets.remove(b)

        for b in ufo_bullets[:]:
            b[0] += b[2]
            b[1] += b[3]
            if b[1] > HEIGHT or b[0] < 0 or b[0] > WIDTH:
                ufo_bullets.remove(b)

        for r in ufo_rockets[:]:
            r[0] += r[2]
            r[1] += r[3]
            if r[1] > HEIGHT or r[0] < 0 or r[0] > WIDTH:
                ufo_rockets.remove(r)

        for b in ufo_blades[:]:
            b[0] += b[2]
            b[1] += b[3]
            if b[1] > HEIGHT or b[0] < 0 or b[0] > WIDTH:
                ufo_blades.remove(b)

        for p in powerups[:]:
            p[1] += POWERUP_SPEED
            if p[1] > HEIGHT:
                powerups.remove(p)

        # ufo rect of collision

        ufo_rect = pygame.Rect(ufo_x, ufo_y, 70, 50)
        for b in player_bullets[:]:
            bullet_rect = pygame.Rect(b[0], b[1], 8, 16)
            if bullet_rect.colliderect(ufo_rect):
                player_bullets.remove(b)
                score += HIT_SCORE
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)
                if random.randint(1, 100) <= POWERUP_DROP_CHANCE:
                    powerups.append([ufo_x + 35 - 15, ufo_y + 25])
                if hit_sound:
                    hit_sound.play()
                break

        # ufo bullet and game over
        
        for b in ufo_bullets[:]:
            if pygame.Rect(b[0], b[1], 10, 20).colliderect(player_rect):
                game_over = True
                break
        if not game_over:
            for r in ufo_rockets[:]:
                if pygame.Rect(r[0], r[1], 12, 30).colliderect(player_rect):
                    game_over = True
                    break
        if not game_over:
            for b in ufo_blades[:]:
                if pygame.Rect(b[0], b[1], 16, 16).colliderect(player_rect):
                    game_over = True
                    break

        if not game_over and ufo_rect.colliderect(player_rect):
            game_over = True

        #power up
            
        for p in powerups[:]:
            power_rect = pygame.Rect(p[0]-15, p[1]-15, 30, 30)
            if power_rect.colliderect(player_rect):
                powerups.remove(p)
                double_shot = True
                double_shot_timer = DOUBLE_SHOT_DURATION

    # fill black background for screen
    
    screen.fill(BLACK)

    # incase with no images, game could still play
    
    if player_img:
        screen.blit(player_img, (player_x, player_y))
    else:
        pygame.draw.rect(screen, GREEN, (player_x, player_y, 50, 60))

    if ufo_img:
        screen.blit(ufo_img, (ufo_x, ufo_y))
    else:
        pygame.draw.rect(screen, RED, (ufo_x, ufo_y, 70, 50))

    for b in player_bullets:
        if bullet_img:
            screen.blit(bullet_img, (b[0], b[1]))
        else:
            pygame.draw.rect(screen, YELLOW, (b[0], b[1], 8, 16))

    for b in ufo_bullets:
        if ufo_bullet_img:
            screen.blit(ufo_bullet_img, (b[0], b[1]))
        else:
            pygame.draw.rect(screen, (255, 100, 100), (b[0], b[1], 10, 20))

    for r in ufo_rockets:
        if rocket_img:
            screen.blit(rocket_img, (r[0], r[1]))
        else:
            pygame.draw.rect(screen, (255, 150, 0), (r[0], r[1], 12, 30))

    for b in ufo_blades:
        if blade_img:
            screen.blit(blade_img, (b[0], b[1]))
        else:
            pts = [(b[0]+8, b[1]), (b[0], b[1]+16), (b[0]+16, b[1]+16)]
            pygame.draw.polygon(screen, (200, 200, 255), pts)

    for p in powerups:
        pygame.draw.circle(screen, GREEN, (int(p[0]), int(p[1])), 15)
        pygame.draw.circle(screen, YELLOW, (int(p[0]), int(p[1])), 10)

    # draw text on top left of screen to display current score and difficult
    # and past high score
    
    draw_text(f"Score: {score}", 10, 10)
    draw_text(f"High Score: {high_score}", 10, 50)
    draw_text(f"Difficulty: {difficulty}", 10, 90)

    # double shot power up text

    if double_shot:
        draw_text("DOUBLE SHOT", WIDTH//2 - 60, 130, GREEN)

    # game over, draw text of Final score and how to restart

    if game_over:
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        screen.blit(s, (0, 0))
        draw_text("GAME OVER", WIDTH//2 - 150, HEIGHT//2 - 50, RED, big_font)
        draw_text(f"Final Score: {score}", WIDTH//2 - 80, HEIGHT//2 + 20)
        draw_text("Press 'R' to restart", WIDTH//2 - 100, HEIGHT//2 + 80)

    pygame.display.flip()

pygame.quit()
