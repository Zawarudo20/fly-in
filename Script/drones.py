from parsing import get_values, Hub, Fly_in
from webcolors import name_to_rgb as rgb
import math
from time import sleep
from copy import deepcopy
from random import choice
import sys
import pygame

data = get_values()

pygame.init()
pygame.display.set_caption("fly_in")
screen = pygame.display.set_mode((1200, 700))
display = pygame.Surface((1200, 700), pygame.SRCALPHA)
menu = pygame.Surface((500,600), pygame.SRCALPHA)
ground = pygame.image.load("assets/Ground/ground.png")
drone_img = pygame.image.load("assets/Drone/tile_040.png")
frame = 0
frame_time = 3
frame_timer = 0
dr = drone_img
img = ground
camera = [0, 0]

start = data.start_hub
end = data.end_hub

def distance(vector_1: tuple[int, int], vector_2: tuple[int, int]):
    xa, ya = vector_1
    xb, yb = vector_2
    distance = math.sqrt(math.pow(xb - xa, 2) + math.pow(yb - ya, 2))
    return distance

def bfs():
    paths = [[start]]
    start.visited = True
    while True:
        new_paths = []
        for path in paths:
            last_hub = path[len(path) - 1]
            for net in last_hub.connections:
                next = net["HUB"]
                if not next.visited:
                    new_path = deepcopy(path)
                    next.visited = True
                    new_path.append(next)
                    new_paths.append(new_path)
                    if next.name == end.name:
                        data.reset()
                        return new_path
        paths = new_paths

class Drone:
    def __init__(self, hub: Hub) -> None:
        x, y = hub.position
        self.current_hub = hub
        self.path = bfs()
        self.x = x
        self.y = y
        self.tita = 0

    def set_angle(self, vector):
        xb, yb = vector
        tita = math.atan2(yb - self.y, xb - self.x)
        self.tita = tita

    def set_next(self):
        x = self.x
        y = self.y
        self.x += math.cos(self.tita)
        self.y += math.sin(self.tita)
        return distance((x, y) ,(self.x, self.y))

    def set_next_hub(self):
        self.current_hub = self.path[1]
        self.path.pop(0)
        self.x = self.current_hub.position[0]
        self.y = self.current_hub.position[1]

    def get_next_hub(self) -> Hub:
        if len(self.path) > 1:
            return self.path[1]
        return self.current_hub

def draw_pos(vector):
    xv, yv = vector
    x = xv * (xs / 2) - yv * (ys / 2) + camera[0]
    y = xv * (xs / 4) + yv * (ys / 4) + camera[1]
    return (x, y)

drone = Drone(start)
clock = pygame.time.Clock()
next_hub = drone.get_next_hub()
dis = distance((drone.x, drone.y), (next_hub.position[0], next_hub.position[1]))

SPACE = 2

def draw_text(text: str, font):
    font = pygame.font.Font(None, font)
    text = font.render(text, True, rgb("black"))
    return text

def draw_menu(name, pos, zone, color, size):
    menu.fill(rgb("white"))
    menu.blit(draw_text(f"name: {name}", 30), (200, 40))
    menu.blit(draw_text(f"position: {pos}", 30), (200, 80))
    menu.blit(draw_text(f"type: {zone}", 30), (200, 120))
    menu.blit(draw_text(f"color: {color}", 30), (200, 160))
    menu.blit(draw_text(f"size: {size}", 30), (200, 200))

is_menu_acitve = False
while True:
    display.fill(rgb("orange"))
    xs, ys = img.get_size()
    width, height = data.size
    for h in range(height * SPACE):
        for w in range(width * SPACE):
            display.blit(img, draw_pos((w, h)))
    for hub in data.hubs:
        x, y = hub.position
        x, y = draw_pos((x * SPACE, y * SPACE))
        image = pygame.image.load("assets/Ground/box.png")
        box = pygame.transform.scale(image, (xs + 1, ys + 1))
        xm, xy = pygame.mouse.get_pos()
        display.blit(box, (x, y - (ys / 4)))
        for net in hub.connections:
            xh, yh = net["HUB"].position
            xh, yh = draw_pos((xh * SPACE, yh * SPACE))
            pygame.draw.line(display, rgb("cyan"), (x + (ys / 2), y + (ys / 4)), (xh + (ys / 2), yh + (ys / 4)))
        rect = box.get_rect(topleft=(x, y))
        if rect.collidepoint(xm, xy):
            display.blit(draw_text(hub.name, xs), (x + xs / 4, y - ys / 2))
            mouse = pygame.mouse.get_just_pressed()
            if mouse[0]:
                draw_menu(hub.name, hub.position, hub.zone, hub.color, hub.size)
                is_menu_acitve = True
    if is_menu_acitve:
        quit = pygame.Surface((50,50), pygame.SRCALPHA)
        quit.fill(rgb("red"))
        quit.blit(draw_text(' X', 60), (0 , 0))
        menu.blit(quit, (0, 0))
        display.blit(menu,(780,0))
    xd, yd = draw_pos((drone.x * SPACE, drone.y * SPACE))
    xn = next_hub.position[0]
    yn = next_hub.position[1]
    display.blit(dr, (xd, yd - ys / 2))
    if dis > 0.5 and drone.current_hub.name != end.name:
        drone.set_angle((xn, yn))
        dis -= drone.set_next()
    elif drone.current_hub.name != end.name:
        drone.set_next_hub()
        next_hub = drone.get_next_hub()
        dis = distance((drone.x, drone.y), (next_hub.position[0], next_hub.position[1]))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    if frame_timer > frame_time:
        frame += 1
        frame_timer = 0
    else:
        frame_timer += 1
    if frame > 7:
        frame = 0
    drone_img = pygame.image.load(f"assets/Drone/tile_04{frame}.png")
    dr = pygame.transform.scale(drone_img, (xs, ys))
    key = pygame.key.get_pressed()
    mouse = pygame.mouse.get_just_pressed()
    if mouse[0]:
        mpos = pygame.mouse.get_pos()
        if is_menu_acitve and quit.get_rect(topleft=(780,0)).collidepoint(mpos):
            is_menu_acitve = False
    mouse = pygame.mouse.get_pressed()
    if mouse[0]:
        npos = pygame.mouse.get_pos()
        if mpos[0] + 70 < npos[0]:
            camera[0] += 10
        elif mpos[0] - 70 > npos[0]:
            camera[0] -= 10
        if mpos[1] + 70 < npos[1]:
            camera[1] += 10
        elif mpos[1] - 70 > npos[1]:
            camera[1] -= 10
    if key[pygame.K_1]:
        img = pygame.transform.scale(ground, (xs + 1, ys + 1))
        dr = pygame.transform.scale(drone_img, (xs + 1, ys + 1))
    elif key[pygame.K_2] and xs > 0:
        img = pygame.transform.scale(ground, (xs - 1, ys - 1))
        dr = pygame.transform.scale(drone_img, (xs - 1, ys - 1))
    if key[pygame.K_SPACE]:
        drone.x = start.position[0]
        drone.y = start.position[1]
        drone.current_hub = start
        drone.path = bfs()
        next_hub = drone.get_next_hub()
        dis = distance((drone.x, drone.y), (next_hub.position[0], next_hub.position[1]))
    screen.blit(display, (0,0))
    clock.tick(120)
    pygame.display.update()