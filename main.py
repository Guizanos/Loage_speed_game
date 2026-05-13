import pygame
import random
import sys

pygame.init()

# ---------------- SCREEN ----------------
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Louage Run 🇹🇳")

clock = pygame.time.Clock()
font       = pygame.font.SysFont("arial", 28, bold=True)
font_large = pygame.font.SysFont("arial", 56, bold=True)
font_med   = pygame.font.SysFont("arial", 36, bold=True)

# ---------------- LOAD IMAGES ----------------
def load_img(path, size):
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(img, size)

louage      = load_img("CatV0.2.png",    (220, 130))
police_car  = load_img("CarPolicV2.png", (240, 140))
police_moto = load_img("PolicV1.png",    (200, 120))
dinar       = load_img("DinarV2.png",    (60, 60))

# ---------------- GAME STATE ----------------
# States: "menu"  "playing"  "game_over"  "win"
state = "menu"

WIN_SCORE = 50  # coins needed to win

# ---------------- PLAYER ----------------
player_x     = 120
player_y     = HEIGHT // 2
player_speed = 6

# ---------------- GAME DATA ----------------
coins     = []
obstacles = []
score     = 0
game_over = False

# Police chase
police_x         = -300
police_y         = float(HEIGHT // 2)
police_active    = False
police_timer     = 0.0
last_chase_score = 0       # score at last police activation

# ---------------- HELPERS ----------------
def draw_text(text, x, y, color=(0, 0, 0), fnt=None):
    if fnt is None:
        fnt = font
    img = fnt.render(text, True, color)
    screen.blit(img, (x, y))

def draw_text_center(text, cy, color=(0, 0, 0), fnt=None):
    if fnt is None:
        fnt = font
    img = fnt.render(text, True, color)
    screen.blit(img, (WIDTH // 2 - img.get_width() // 2, cy))

def make_button(text, cx, cy, w=280, h=55, fnt=None):
    """Draw a button, return its Rect."""
    if fnt is None:
        fnt = font_med
    rect = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    pygame.draw.rect(screen, (30, 30, 80), rect, border_radius=12)
    pygame.draw.rect(screen, (100, 160, 255), rect, 3, border_radius=12)
    label = fnt.render(text, True, (255, 255, 255))
    screen.blit(label, (rect.centerx - label.get_width() // 2,
                         rect.centery - label.get_height() // 2))
    return rect

def spawn_coin():
    return pygame.Rect(WIDTH, random.randint(50, HEIGHT - 80), 40, 40)

def spawn_obstacle():
    y    = random.randint(50, HEIGHT - 100)
    kind = random.choice(["car", "moto"])
    rect = pygame.Rect(WIDTH, y, 120, 70)
    return {"rect": rect, "type": kind}

def reset_game():
    global coins, obstacles, score, game_over
    global police_x, police_y, police_active, police_timer, last_chase_score
    global player_x, player_y, state
    coins             = []
    obstacles         = []
    score             = 0
    game_over         = False
    police_x          = -300
    police_y          = float(HEIGHT // 2)
    police_active     = False
    police_timer      = 0.0
    last_chase_score  = 0
    player_x          = 120
    player_y          = HEIGHT // 2
    state             = "playing"

# ---------------- MAIN MENU ----------------
def draw_menu(mouse_pos):
    screen.fill((15, 20, 45))
    # Title
    draw_text_center("🇹🇳  LOUAGE RUN  🇹🇳", HEIGHT // 2 - 130,
                     color=(255, 220, 60), fnt=font_large)
    draw_text_center("Collect 20 coins to win the round!", HEIGHT // 2 - 50,
                     color=(200, 200, 200))
    draw_text_center("Use Arrow Keys or WASD to move", HEIGHT // 2 - 10,
                     color=(170, 170, 170))
    draw_text_center("Avoid obstacles & police cars", HEIGHT // 2 + 30,
                     color=(170, 170, 170))

    play_btn = make_button("▶  Play", WIDTH // 2, HEIGHT // 2 + 110)
    quit_btn = make_button("✕  Quit", WIDTH // 2, HEIGHT // 2 + 180)
    return play_btn, quit_btn

# ---------------- WIN SCREEN ----------------
def draw_win_screen(mouse_pos):
    # Overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((10, 40, 10, 210))
    screen.blit(overlay, (0, 0))

    draw_text_center("🏆  YOU WIN!  🏆", HEIGHT // 2 - 130,
                     color=(255, 230, 50), fnt=font_large)
    draw_text_center(f"Score: {score}", HEIGHT // 2 - 50,
                     color=(255, 255, 255), fnt=font_med)
    draw_text_center("You collected 20 coins!", HEIGHT // 2,
                     color=(180, 255, 180))

    restart_btn  = make_button("🔄  Restart Round", WIDTH // 2, HEIGHT // 2 + 90)
    menu_btn     = make_button("🏠  Main Menu",     WIDTH // 2, HEIGHT // 2 + 160)
    return restart_btn, menu_btn

# ---------------- GAME OVER SCREEN ----------------
def draw_game_over_screen():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((40, 10, 10, 210))
    screen.blit(overlay, (0, 0))

    draw_text_center("💀  GAME OVER  💀", HEIGHT // 2 - 120,
                     color=(220, 50, 50), fnt=font_large)
    draw_text_center(f"Score: {score}", HEIGHT // 2 - 40,
                     color=(255, 255, 255), fnt=font_med)

    restart_btn = make_button("🔄  Restart Round", WIDTH // 2, HEIGHT // 2 + 50)
    menu_btn    = make_button("🏠  Main Menu",     WIDTH // 2, HEIGHT // 2 + 120)
    return restart_btn, menu_btn

# ============================================================
# GAME LOOP
# ============================================================
running = True
while running:
    dt = clock.tick(60)   # ms since last frame

    mouse_pos     = pygame.mouse.get_pos()
    mouse_clicked = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_clicked = True

    # ======================== MENU ========================
    if state == "menu":
        play_btn, quit_btn = draw_menu(mouse_pos)
        if mouse_clicked:
            if play_btn.collidepoint(mouse_pos):
                reset_game()   # sets state = "playing"
            elif quit_btn.collidepoint(mouse_pos):
                running = False

    # ======================== PLAYING ========================
    elif state == "playing":
        screen.fill((135, 206, 235))

        keys = pygame.key.get_pressed()

        # -------- PLAYER MOVEMENT --------
        if keys[pygame.K_UP]    or keys[pygame.K_w]: player_y -= player_speed
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: player_y += player_speed
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: player_x -= player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: player_x += player_speed

        player_y = max(0, min(player_y, HEIGHT - 80))
        player_x = max(0, min(player_x, WIDTH - 130))
        player_rect = pygame.Rect(player_x, player_y, 130, 75)

        # -------- SPAWN --------
        if random.randint(1, 60) == 1:
            coins.append(spawn_coin())
        if random.randint(1, 80) == 1:
            obstacles.append(spawn_obstacle())

        # -------- COINS --------
        for coin in coins[:]:
            coin.x -= 5
            screen.blit(dinar, coin)
            if player_rect.colliderect(coin):
                score += 1
                coins.remove(coin)
            elif coin.x < -50:
                coins.remove(coin)

        # -------- OBSTACLES --------
        for obs in obstacles[:]:
            obs["rect"].x -= 6
            if obs["type"] == "car":
                screen.blit(police_car, obs["rect"])
            else:
                screen.blit(police_moto, obs["rect"])
            if player_rect.colliderect(obs["rect"]):
                state = "game_over"
            elif obs["rect"].x < -150:
                obstacles.remove(obs)

        # -------- POLICE CHASE CONTROL --------
        # Activate every +10 coins (threshold: 10, 20, 30, 40…)
        if not police_active:
            if score >= 10 and (score // 10) > (last_chase_score // 10):
                police_active    = True
                police_timer     = 0.0
                last_chase_score = score
                police_x         = -300          # enter from left
                police_y         = float(player_y)

        if police_active:
            # Move toward player
            police_x   += 5
            police_y   += (player_y - police_y) * 0.1
            police_rect = pygame.Rect(int(police_x), int(police_y), 140, 80)

            # Police car is destroyed if it hits an obstacle
            for obs in obstacles[:]:
                if police_rect.colliderect(obs["rect"]):
                    police_active = False
                    police_x      = -300   # move off-screen
                    break

            # Draw police chaser
            screen.blit(police_car, (int(police_x), int(police_y)))

            # Collision with player → game over
            if police_rect.colliderect(player_rect):
                state = "game_over"

            # Timer (seconds)
            police_timer += dt / 1000.0
            if police_timer >= 5:
                police_active = False
                police_x      = -300

        # -------- DRAW PLAYER --------
        screen.blit(louage, (player_x, player_y))

        # -------- UI --------
        draw_text(f"Score: {score} / {WIN_SCORE}", 20, 20, color=(0, 0, 0))
        if police_active:
            draw_text("⚠ POLICE CHASE ⚠", WIDTH // 2 - 130, 20, color=(200, 0, 0))

        # -------- WIN CHECK --------
        if score >= WIN_SCORE:
            state = "win"

    # ======================== WIN ========================
    elif state == "win":
        # Keep the game world visible behind overlay
        screen.fill((135, 206, 235))
        restart_btn, menu_btn = draw_win_screen(mouse_pos)
        if mouse_clicked:
            if restart_btn.collidepoint(mouse_pos):
                reset_game()
            elif menu_btn.collidepoint(mouse_pos):
                state = "menu"

    # ======================== GAME OVER ========================
    elif state == "game_over":
        screen.fill((135, 206, 235))
        restart_btn, menu_btn = draw_game_over_screen()
        if mouse_clicked:
            if restart_btn.collidepoint(mouse_pos):
                reset_game()
            elif menu_btn.collidepoint(mouse_pos):
                state = "menu"

    pygame.display.update()

pygame.quit()
sys.exit()