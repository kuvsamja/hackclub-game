import pygame
import math

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
    speed = 0.1
    sensitivity = 0.1
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
    def move(self, buttons):
        if buttons[pygame.K_LEFT]:
            self.a -= self.sensitivity
        if buttons[pygame.K_RIGHT]:
            self.a += self.sensitivity
        self.a %= 2*PI

        if buttons[pygame.K_w]:
            self.x += math.cos(self.a)
            self.y += math.sin(self.a)
        if buttons[pygame.K_s]:
            self.x -= math.cos(self.a)
            self.y -= math.sin(self.a)
        
        if buttons[pygame.K_a]:
            self.x -= math.cos(self.a)
            self.y += math.sin(self.a)
        if buttons[pygame.K_d]:
            self.x += math.cos(self.a)
            self.y -= math.sin(self.a)
        

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

        pygame.display.flip()
    pygame.quit()
