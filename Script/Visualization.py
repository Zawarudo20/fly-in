from webcolors import name_to_rgb as rgb
from Drones import Drone
from Hubs import Map, Hub
from Animation import Movement
import sys
from time import sleep
import pygame


SPACE = 5
class Visualizor:
    def __init__(self, data: Map) -> None:
        pygame.init()
        pygame.display.set_caption("fly_in")
        self.screen = pygame.display.set_mode((1200, 700))
        self.display = pygame.Surface((1200, 700), pygame.SRCALPHA)
        self.menu = pygame.Surface((1200, 300), pygame.SRCALPHA)
        self.menus = []
        self.animations = {"menu": Movement((0, 400), (0, 400), 20)}
        self.map = data
        self.drones: list[Drone] = []
        for i in range(data.drones):
            drone = Drone(f"D{i}", data.start_hub, data.end_hub)
            self.map.start_hub.visitors.add(drone)
            drone.path_finder()
            data.reset()
            self.drones.append(drone)
        self.size = 32
        self.camera = [600, 60]
        self.camera_pos = (0, 0)
        self.clock = pygame.time.Clock()
        self.isdragging = False


# ---------------------Get position for drawing-------------------
    def __draw_pos(self, vector : tuple[int, int]) -> tuple[int, int]:
        xv, yv = vector
        x = xv * self.size / 2 - yv * self.size / 2 + self.camera[0]
        y = xv * self.size / 4 + yv * self.size / 4 + self.camera[1]
        return (x, y)

# -----------------------drawing the text-------------------------
    @staticmethod
    def __draw_text(text: str, size, color) -> pygame.Font:
        font = pygame.font.Font("assets/font/Minecraft.ttf", size)
        text = font.render(text, True, rgb(color))
        return text

# -----------------------drawing grid-------------------------
    def __draw_grid(self, ground, water) -> None:
        width, height = self.map.size
        ground = pygame.transform.scale(ground, (self.size, self.size))
        water = pygame.transform.scale(water, (self.size, self.size))
        for h in range(-width * SPACE, height * SPACE + width * SPACE):
            for w in range(-height* SPACE, width * SPACE + height * SPACE):
                pos = self.__draw_pos((w, h))
                if pos[0] < -self.size  or pos[1] < -self.size:
                    continue
                if pos[0] > 1200 or pos[1] > 700:
                    break
                if 0 <= w < width * SPACE and 0 <= h < height * SPACE:
                    self.display.blit(ground, pos)
                else:
                    self.display.blit(water, pos)
# -----------------------drawing the menu-------------------------
    def __draw_menu(self) -> None:
        self.menu.fill((0,0,0,0))
        if self.menus:
            mx, my = pygame.mouse.get_pos()
            y = self.animations["menu"].start[1]
            if y <= 400:
                box = pygame.image.load("assets/menu/down.png")
            elif y >= 600:
                box = pygame.image.load("assets/menu/up.png")
            mouse = pygame.mouse.get_just_pressed()
            remove = []
            for i in range(len(self.menus)):
                rect = pygame.Rect(200 * i + 74, y, 53, 19)
                self.menu.blit(self.menus[i], (i * 200, 0))
                if rect.collidepoint(mx, my) and mouse[0]:
                    remove.append(i)
            if not self.animations["menu"].is_animating():
                if box.get_rect(topleft=(0,y)).collidepoint(mx, my) and mouse[0]:
                    if y <= 400:
                        self.animations["menu"].start = (0, 400)
                        self.animations["menu"].end = (0, 600)
                    elif y >= 600:
                        self.animations["menu"].start = (0, 600)
                        self.animations["menu"].end = (0, 400)
                    self.animations["menu"].update_distance()
                self.menu.blit(box, (0,0))
            if remove:
                self.menus.pop(remove[0])
            self.display.blit(self.menu, (0,y))
            y = self.animations["menu"].anim()



# -----------------------drawing hub-------------------------
    def __draw_hub(self, hub: Hub) -> None:
# --------------------------DRAW BOX-----------------------------
        x, y = hub.position
        x, y = self.__draw_pos((x * SPACE, y * SPACE))
        box = hub.image
        box = pygame.transform.scale(box, (self.size, self.size))
        self.display.blit(box, (x, y - self.size / 4))
        for net in hub.connections:
            xh, yh = net["HUB"].position
            xh, yh = self.__draw_pos((xh * SPACE, yh * SPACE))
            pygame.draw.line(self.display,
                             rgb("cyan"),
                             (x + self.size / 2, y + self.size / 4),
                             (xh + self.size / 2, yh + self.size / 4))
# --------------------CHECK MOUSE POSITION------------------------
        xm, xy = pygame.mouse.get_pos()
        rect = box.get_rect(topleft=(x, y))
        mouse = pygame.mouse.get_just_pressed()
        if rect.collidepoint(xm, xy):
            self.display.blit(self.__draw_text(hub.name, self.size, "black"),
                              (x + self.size / 4, y - self.size / 2))
            if mouse[0]:
                if hub.menu not in self.menus:
                    hub.update_menu()
                    self.menus.append(hub.menu)
# -----------------------drawing drone---------------------------
    def __draw_drone(self, drone: Drone, pause) -> None:
        image = drone.image.anim()
        image = pygame.transform.scale(image, (self.size, self.size))
        if drone.image.start == 8:
            drone.image.start = 0
        x, y = self.__draw_pos((drone.x * SPACE, drone.y * SPACE))
        self.display.blit(image, (x, y - self.size / 2))
        if drone.movement.is_animating() and not pause:
            drone.move()
        elif not drone.movement.is_animating():
            drone.has_arrived = True

    def __check_buttons(self) -> None:
        key = pygame.key.get_pressed()
        x, y = self.map.size
        if key[pygame.K_1]:
            self.size += 1
        elif key[pygame.K_2] and self.size > 28:
            self.size -= 1
        if key[pygame.K_SPACE]:
            for drone in self.drones:
                drone.x, drone.y = self.map.start_hub.position
                drone.current_hub = self.map.start_hub
                drone.path_finder()
                self.map.reset()
                drone.has_arrived = False
            for hub in drone.path:
                print(hub.name)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.isdragging = True
                self.camera_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                self.isdragging = False
            if event.type == pygame.MOUSEMOTION and self.isdragging:
                xc = event.pos[0] - self.camera_pos[0]
                yc = event.pos[1] - self.camera_pos[1]
                if (y + 5) * SPACE * (self.size / 2) > self.camera[0] + xc > 1200 - (x + 5) * SPACE * (self.size / 2):
                    self.camera[0] += xc
                if (10 * SPACE) * (self.size / 4) > self.camera[1] + yc > 700 - (x + y + 10) * SPACE * (self.size / 4):
                    self.camera[1] += yc
                self.camera_pos = event.pos
        if (y + 5) * SPACE * (self.size / 2) < self.camera[0]:
            self.camera[0] = (y + 5) * SPACE * (self.size / 2)
        if 1200 - (x + 5) * SPACE * (self.size / 2) > self.camera[0]:
            self.camera[0] = 1200 - (x + 5) * SPACE * (self.size / 2)
        if (10 * SPACE) * (self.size / 4) < self.camera[1]:
            self.camera[1] = (10 * SPACE) * (self.size / 4)
        if 700 - (x + y + 10) * SPACE * (self.size / 4) > self.camera[1]:
            self.camera[1] = 700 - (x + y + 10) * SPACE * (self.size / 4)

    def game(self) -> None:
        ground = pygame.image.load("assets/Ground/ground.png")
        water = pygame.image.load("assets/Ground/water.png")
        can_go = False
        pause = False
        count = 0
        while True:
            self.display.fill(rgb("white"))
            self.__draw_grid(ground, water)
            key = pygame.key.get_pressed()
            if key[pygame.K_e]:
                can_go = True
            if key[pygame.K_a]:
                pause = not pause
            for hub in self.map.hubs:
                self.__draw_hub(hub)
            all_arrived = True
            all_in_goal = True
            if can_go:
                for drone in self.drones:
                    self.__draw_drone(drone, pause)
                    if not drone.has_arrived:
                        all_arrived = False
            if can_go and all_arrived:
                for drone in self.drones:
                    if drone.current_hub.name != drone.next_hub.name:
                        print(f"{drone.name}-{drone.next_hub.name}", end=" ")
                    drone.update()
                    self.map.reset()
                    drone.has_arrived = False
                    if drone.current_hub.name != self.map.end_hub.name:
                        all_in_goal = False
                print("")
                if not all_in_goal:
                    count += 1
            text = self.__draw_text(f"count: {count}", 30, "black")
            self.display.blit(text, (0,0))
            self.__draw_menu()
            self.__check_buttons()
            self.screen.blit(self.display, (0, 0))
            self.clock.tick(120)
            pygame.display.update()
