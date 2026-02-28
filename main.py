import pygame
import math

pygame.init()

PI = 3.14159
HEIGHT = 600
WIDTH = 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
enemy_texture = pygame.image.load("enemy.png").convert_alpha()
running = True
speed = 1
WALL = (128,128,128)

class Player:
    x = 9.0
    y = 13.0
    a = 0
    fov = PI / 3
    speed = 0.1
    sensitivity = 0.1
    RAYDENSITY = 1
    RAYNUMBER = int(WIDTH / RAYDENSITY)
    max_health = 100
    health = 100
    hit_timer = 0
    def __init__(self, map: list[list]):
        self.map = map
    def is_wall(self, x, y):
        map_x = int(x)
        map_y = int(y)
        if map_x < 0 or map_y < 0 or map_y >= len(self.map) or map_x >= len(self.map[0]):
            return True
        return self.map[map_y][map_x] == 1
    def rayCollision(self, ray_dir_x, ray_dir_y, screen_x):
        map_x = int(self.x)
        map_y = int(self.y)

        delta_dist_x = abs(1 / ray_dir_x) if ray_dir_x != 0 else 1e30
        delta_dist_y = abs(1 / ray_dir_y) if ray_dir_y != 0 else 1e30

        if ray_dir_x < 0:
            step_x = -1
            side_dist_x = (self.x - map_x) * delta_dist_x
        else:
            step_x = 1
            side_dist_x = (map_x + 1.0 - self.x) * delta_dist_x

        if ray_dir_y < 0:
            step_y = -1
            side_dist_y = (self.y - map_y) * delta_dist_y
        else:
            step_y = 1
            side_dist_y = (map_y + 1.0 - self.y) * delta_dist_y

        hit = False
        side = 0
        depth = 0
        while not hit and depth < 64:
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1
            depth += 1
            if self.is_wall(map_x, map_y):
                hit = True

        if side == 0:
            perp_dist = side_dist_x - delta_dist_x
        else:
            perp_dist = side_dist_y - delta_dist_y
        if perp_dist < 0.0001:
            perp_dist = 0.0001

        wall_height = HEIGHT / perp_dist

        shade = max(0, min(255, int(255 - perp_dist * 25)))
        if side == 1:
            shade = int(shade * 0.7)
        color = (shade, shade, shade)

        self.drawRay(screen, wall_height, screen_x, color)
        self.z_buffer[int(screen_x)] = perp_dist

    def render(self):
        self.z_buffer = [float('inf')] * WIDTH
        dir_x = math.cos(self.a)
        dir_y = math.sin(self.a)
        plane_x = -dir_y * math.tan(self.fov / 2)
        plane_y =  dir_x * math.tan(self.fov / 2)

        for i in range(self.RAYNUMBER):
            camera_x = 2 * i / self.RAYNUMBER - 1
            ray_dir_x = dir_x + plane_x * camera_x
            ray_dir_y = dir_y + plane_y * camera_x
            screen_x = i * self.RAYDENSITY
            self.rayCollision(ray_dir_x, ray_dir_y, screen_x)

        for enemy in enemies:
            if enemy.alive:
                enemy.render(screen, self)

        cx, cy = WIDTH // 2, HEIGHT // 2
        pygame.draw.line(screen, (0, 255, 0), (cx - 10, cy), (cx + 10, cy), 2)
        pygame.draw.line(screen, (0, 255, 0), (cx, cy - 10), (cx, cy + 10), 2)

        # Health bar
        bar_w = 200
        bar_h = 20
        bar_x = 20
        bar_y = 20
        health_ratio = max(0, self.health / self.max_health)
        pygame.draw.rect(screen, (60, 0, 0), (bar_x, bar_y, bar_w, bar_h))
        bar_color = (0, 200, 0) if health_ratio > 0.5 else (200, 200, 0) if health_ratio > 0.25 else (200, 0, 0)
        pygame.draw.rect(screen, bar_color, (bar_x, bar_y, int(bar_w * health_ratio), bar_h))
        pygame.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, bar_w, bar_h), 2)
        hp_text = font_small.render(f"{self.health} / {self.max_health}", True, (255, 255, 255))
        screen.blit(hp_text, (bar_x + bar_w + 10, bar_y))

        # Damage flash
        if self.hit_timer > 0:
            flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash.fill((255, 0, 0, min(100, self.hit_timer * 20)))
            screen.blit(flash, (0, 0))

    def shoot(self):
        for enemy in enemies:
            if not enemy.alive:
                continue
            ex = enemy.x - self.x
            ey = enemy.y - self.y
            dist = math.sqrt(ex * ex + ey * ey)
            if dist < 0.1:
                continue

            dir_x = math.cos(self.a)
            dir_y = math.sin(self.a)
            plane_x = -dir_y * math.tan(self.fov / 2)
            plane_y =  dir_x * math.tan(self.fov / 2)

            inv_det = 1.0 / (plane_x * dir_y - dir_x * plane_y)
            tx = inv_det * (dir_y * ex - dir_x * ey)
            ty = inv_det * (-plane_y * ex + plane_x * ey)

            if ty <= 0:
                continue

            screen_x = int((WIDTH / 2) * (1 + tx / ty))
            sprite_h = int(HEIGHT / ty)
            half_w = sprite_h // 2

            
            if abs(screen_x - WIDTH // 2) < half_w:
            
                center_col = min(max(WIDTH // 2, 0), WIDTH - 1)
                if ty < self.z_buffer[center_col]:
                    enemy.take_damage(1)
                    return True
        return False

    def drawRay(self, screen, height, x, color):
        pygame.draw.rect(screen, color, (x, HEIGHT / 2 - height / 2, self.RAYDENSITY, height))
    def move(self, buttons):
        if buttons[pygame.K_LEFT]:
            self.a -= self.sensitivity
        if buttons[pygame.K_RIGHT]:
            self.a += self.sensitivity
        self.a %= 2 * PI

        dx = 0
        dy = 0
        if buttons[pygame.K_w]:
            dx += math.cos(self.a) * self.speed
            dy += math.sin(self.a) * self.speed
        if buttons[pygame.K_s]:
            dx -= math.cos(self.a) * self.speed
            dy -= math.sin(self.a) * self.speed
        if buttons[pygame.K_a]:
            dx += math.cos(self.a - PI / 2) * self.speed
            dy += math.sin(self.a - PI / 2) * self.speed
        if buttons[pygame.K_d]:
            dx += math.cos(self.a + PI / 2) * self.speed
            dy += math.sin(self.a + PI / 2) * self.speed

        margin = 0.15
        sign_x = 1 if dx > 0 else (-1 if dx < 0 else 0)
        sign_y = 1 if dy > 0 else (-1 if dy < 0 else 0)

        new_x = self.x + dx
        if not self.is_wall(new_x + sign_x * margin, self.y):
            self.x = new_x

        new_y = self.y + dy
        if not self.is_wall(self.x, new_y + sign_y * margin):
            self.y = new_y
class Enemy:
    def __init__(self, x, y, color=(255, 0, 0), health=3):
        self.x = x
        self.y = y
        self.color = color
        self.health = health
        self.alive = True
        self.hit_timer = 0
        self.attack_cooldown = 0

    def take_damage(self, amount):
        self.health -= amount
        self.hit_timer = 10 
        if self.health <= 0:
            self.alive = False

    def update(self):
        if self.hit_timer > 0:
            self.hit_timer -= 1
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        self.move(player)
        self.attack(player)
    def render(self, screen, player):
        if not self.alive:
            return
        ex = self.x - player.x
        ey = self.y - player.y
        dist = math.sqrt(ex * ex + ey * ey)
        if dist < 0.1:
            return

    
        dir_x = math.cos(player.a)
        dir_y = math.sin(player.a)
        plane_x = -dir_y * math.tan(player.fov / 2)
        plane_y =  dir_x * math.tan(player.fov / 2)

        inv_det = 1.0 / (plane_x * dir_y - dir_x * plane_y)
        tx = inv_det * (dir_y * ex - dir_x * ey)
        ty = inv_det * (-plane_y * ex + plane_x * ey)

        if ty <= 0.1:
            return 

        screen_x = int((WIDTH / 2) * (1 + tx / ty))
        sprite_h = int(HEIGHT / ty)
        sprite_w = sprite_h // 2

        draw_start_x = screen_x - sprite_w // 2
        draw_end_x = screen_x + sprite_w // 2
        draw_start_y = HEIGHT // 2 - sprite_h // 2

        tex_w = enemy_texture.get_width()
        tex_h = enemy_texture.get_height()
        scaled = pygame.transform.scale(enemy_texture, (sprite_w, sprite_h))

        shade = max(50, min(255, int(255 - dist * 20)))
        if self.hit_timer > 0:
            scaled.fill((255, 255, 255, 0), special_flags=pygame.BLEND_RGB_MAX)
        dark = pygame.Surface((sprite_w, sprite_h))
        dark.fill((shade, shade, shade))
        scaled.blit(dark, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

        for sx in range(max(0, draw_start_x), min(WIDTH, draw_end_x)):
            if ty < player.z_buffer[sx]:
                tex_col = sx - draw_start_x
                col_surface = scaled.subsurface((tex_col, 0, 1, sprite_h))
                screen.blit(col_surface, (sx, draw_start_y))
    def attack(self, player):
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 1.0 and self.attack_cooldown <= 0:
            player.health -= 10
            player.hit_timer = 5
            self.attack_cooldown = 60

    def move(self, player):
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 0.8:
            return
        speed = 0.03
        dx = dx / dist * speed
        dy = dy / dist * speed
        margin = 0.15
        sign_x = 1 if dx > 0 else (-1 if dx < 0 else 0)
        sign_y = 1 if dy > 0 else (-1 if dy < 0 else 0)
        new_x = self.x + dx
        if not player.is_wall(new_x + sign_x * margin, self.y):
            self.x = new_x
        new_y = self.y + dy
        if not player.is_wall(self.x, new_y + sign_y * margin):
            self.y = new_y

enemies = []

map = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,1,1,1,0,0,0,1,0,0,1,0,0,1],
    [1,0,0,1,0,0,0,0,0,1,0,0,1,0,0,1],
    [1,0,0,1,0,0,0,0,0,1,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,1,1,1,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,1,0,1,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,1,0,1,0,0,1,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1],
    [1,0,0,1,0,0,0,0,0,0,0,1,0,0,0,1],
    [1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,1,1,1,0,0,0,0,0,0,0,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]
player = Player(map)

enemies.append(Enemy(4.5, 4.5, (255, 0, 0), 3))
enemies.append(Enemy(12.5, 2.5, (0, 0, 255), 3))
enemies.append(Enemy(7.5, 8.5, (255, 128, 0), 5))

font_big = pygame.font.SysFont(None, 72)
font_med = pygame.font.SysFont(None, 40)
font_small = pygame.font.SysFont(None, 28)

STORY_LINES = [
    "Davno, u doba velikih kraljeva i hrabrih ratnika,",
    "kraljevstvo je bilo zasticeno od strane najjacih boraca.",
    "",
    "Ali tama je dosla iz dubina zemlje.",
    "Podzemni svet se probudio i progutao sve pred sobom.",
    "",
    "Kraljev najverniji ratnik — ti — poslat si u dubine,",
    "da se suocis sa demonima koji su progutali svetlost.",
    "",
    "Nema povratka. Samo borba.",
    "Samo prezivljavanje.",
    "",
    "Uzmi oruzje. Kreni napred.",
    "Kralj veruje u tebe.",
]

def show_story():
    global running
    clock = pygame.time.Clock()
    displayed_chars = 0
    total_chars = sum(len(line) for line in STORY_LINES)
    char_speed = 2

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if displayed_chars >= total_chars:
                        return True
                    else:
                        displayed_chars = total_chars
                if event.key == pygame.K_ESCAPE:
                    return False

        displayed_chars = min(displayed_chars + char_speed, total_chars)

        screen.fill((0, 0, 0))

        y = 60
        chars_left = displayed_chars
        for line in STORY_LINES:
            if chars_left <= 0:
                break
            show = line[:chars_left]
            chars_left -= len(line)
            text_surf = font_small.render(show, True, (200, 180, 140))
            screen.blit(text_surf, (WIDTH // 2 - text_surf.get_width() // 2, y))
            y += 32

        if displayed_chars >= total_chars:
            prompt = font_small.render("[ENTER] Nastavi", True, (255, 255, 100))
            screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT - 60))

        pygame.display.flip()
        clock.tick(60)
    return False

def show_menu():
    global running
    clock = pygame.time.Clock()
    selected = 0
    options = ["Igraj", "Izadji"]
    title_color_timer = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return -1
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    selected = (selected - 1) % len(options)
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    selected = (selected + 1) % len(options)
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return selected
                if event.key == pygame.K_ESCAPE:
                    return -1

        title_color_timer += 1
        screen.fill((0, 0, 0))

        border_shade = 40 + int(15 * math.sin(title_color_timer * 0.05))
        pygame.draw.rect(screen, (border_shade, border_shade, border_shade + 10), (20, 20, WIDTH - 40, HEIGHT - 40), 3)

        r = 180 + int(40 * math.sin(title_color_timer * 0.03))
        g = 50 + int(30 * math.sin(title_color_timer * 0.02))
        title_surf = font_big.render("PODZEMLJE KRALJA", True, (r, g, 30))
        screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 140))

        subtitle_surf = font_small.render("Borba u tami", True, (140, 120, 100))
        screen.blit(subtitle_surf, (WIDTH // 2 - subtitle_surf.get_width() // 2, 210))

        for i, opt in enumerate(options):
            if i == selected:
                color = (255, 255, 100)
                prefix = "> "
            else:
                color = (160, 160, 160)
                prefix = "  "
            opt_surf = font_med.render(prefix + opt, True, color)
            screen.blit(opt_surf, (WIDTH // 2 - opt_surf.get_width() // 2, 320 + i * 60))

        hint_surf = font_small.render("[W/S] Biraj   [ENTER] Potvrdi", True, (100, 100, 100))
        screen.blit(hint_surf, (WIDTH // 2 - hint_surf.get_width() // 2, HEIGHT - 50))

        pygame.display.flip()
        clock.tick(60)
    return -1

def reset_game():
    player.health = player.max_health
    player.x = 9.0
    player.y = 13.0
    player.a = 0
    player.hit_timer = 0
    enemies.clear()
    enemies.append(Enemy(4.5, 4.5, (255, 0, 0), 3))
    enemies.append(Enemy(12.5, 2.5, (0, 0, 255), 3))
    enemies.append(Enemy(7.5, 8.5, (255, 128, 0), 5))

def game_loop():
    global running
    clock = pygame.time.Clock()
    shoot_cooldown = 0
    print("Game started")
    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            return

        if shoot_cooldown > 0:
            shoot_cooldown -= 1
        if keys[pygame.K_SPACE] and shoot_cooldown == 0:
            player.shoot()
            shoot_cooldown = 15

        if player.hit_timer > 0:
            player.hit_timer -= 1

        player.move(keys)
        for enemy in enemies:
            enemy.update()
        player.render()

        # Win screen
        if all(not e.alive for e in enemies):
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 80, 0, 180))
            screen.blit(overlay, (0, 0))
            win_text = font_big.render("POBEDIO SI!", True, (50, 255, 50))
            screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2 - 50))
            hint_text = font_small.render("[ENTER] Nazad u meni", True, (200, 255, 200))
            screen.blit(hint_text, (WIDTH // 2 - hint_text.get_width() // 2, HEIGHT // 2 + 20))
            pygame.display.flip()
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        waiting = False
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        waiting = False
            return

        if player.health <= 0:
            # Death screen
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((150, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            dead_text = font_big.render("POGINUO SI", True, (255, 50, 50))
            screen.blit(dead_text, (WIDTH // 2 - dead_text.get_width() // 2, HEIGHT // 2 - 50))
            hint_text = font_small.render("[ENTER] Nazad u meni", True, (255, 200, 200))
            screen.blit(hint_text, (WIDTH // 2 - hint_text.get_width() // 2, HEIGHT // 2 + 20))
            pygame.display.flip()
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        waiting = False
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        waiting = False
            return

        pygame.display.flip()
        clock.tick(60)

def main():
    global running

    # Story intro
    if not show_story():
        pygame.quit()
        return

    # Main menu
    while running:
        choice = show_menu()
        if choice == 0:
            reset_game()
            game_loop()
        else:
            break

    pygame.quit()

main()
