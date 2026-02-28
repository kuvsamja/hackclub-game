import pygame

pygame.init()

PI = 3.14159
HEIGHT = 600
WIDTH = 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
running = True
speed = 1
WALL = (255,255,255)
class Player:
    x = 0
    y = 0
    a = 0
    fov = 2 * PI / 3
    RAYDENSITY = 1
    RAYNUMBER = int(WIDTH / RAYDENSITY)
    def __init__(self, map: list[list]):
        self.map = map
    def rayCollision(self, ray_angle):
        pass
    def render(self):
        for ray_num in range(-self.RAYNUMBER / 2, self.RAYNUMBER / 2):
            ray_angle = self.a + self.fov * self.RAYNUMBER / ray_num
            self.rayCollision(ray_angle)
    def drawRay(self, screen, height, x):
        pygame.draw.rect(screen, WALL, (x, HEIGHT/2-height/2, 1 / self.RAYDENSITY, height))


map = [
    [0, 0, 0],
    [0, 0, 0],
    [0, 0, 1],
]
player = Player()
def main():
    
    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.px -= speed
        if keys[pygame.K_RIGHT]:
            px += speed
        if keys[pygame.K_UP]:
            py -= speed
        if keys[pygame.K_DOWN]:
            py += speed
        pygame.draw.rect(screen, (0,0,255), (px,py,20,20))

        pygame.display.flip()
    pygame.quit()
