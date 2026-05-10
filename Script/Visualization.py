from webcolors import name_to_rgb as rgb
from Drones import Drone
from Hubs import Map, Hub
from Animation import Movement
import sys
import pygame


SPACE = 2
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
        self.drone = Drone(data.start_hub, data.end_hub)
        self.size = 32
        self.camera = [600, 60]
        self.camera_pos = (0, 0)
        self.clock = pygame.time.Clock()
        self.isdragging = False
        self.open_box = False


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
    def __draw_hub(self, hub: Hub, has_drone_arrived: bool) -> None:
# --------------------------DRAW BOX-----------------------------
        x, y = hub.position
        x, y = self.__draw_pos((x * SPACE, y * SPACE))
        box = hub.image.anim()
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
    def __draw_drone(self) -> None:
        drone = self.drone.image.anim()
        drone = pygame.transform.scale(drone, (self.size, self.size))
        if self.drone.image.start == 8:
            self.drone.image.start = 0
        x, y = self.__draw_pos((self.drone.x * SPACE, self.drone.y * SPACE))
        self.display.blit(drone, (x, y - self.size / 2))
        if self.drone.movement.is_animating():
            self.drone.move()
        else:
            return True
        return False

    def __check_buttons(self) -> None:
        key = pygame.key.get_pressed()
        x, y = self.map.size
        if key[pygame.K_1]:
            self.size += 1
        elif key[pygame.K_2] and self.size > 28:
            self.size -= 1
        if key[pygame.K_SPACE]:
            self.map.reset()
            self.drone.reset(self.map.start_hub)
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
        has_arrived = False
        can_go = False
        ground = pygame.image.load("assets/Ground/ground.png")
        water = pygame.image.load("assets/Ground/water.png")
        while True:
            self.display.fill(rgb("black"))
            self.__draw_grid(ground, water)
            key = pygame.key.get_pressed()
            if key[pygame.K_e]:
                can_go = True
            if key[pygame.K_a]:
                can_go = False
            if key[pygame.K_SPACE]:
                has_arrived = False
            for hub in self.map.hubs:
                self.__draw_hub(hub, has_arrived)
            if can_go and not has_arrived and not self.drone.current_hub.image.is_animating():
                has_arrived = self.__draw_drone()
                self.open_box = False
            if has_arrived:
                self.drone.next_hub.image.end = 6
                if not self.drone.next_hub.image.is_animating() and len(self.drone.path) > 2:
                    has_arrived = False
                    self.drone.next_hub.image.end = 0
                    self.drone.update()
            self.__draw_menu()
            self.__check_buttons()
            self.screen.blit(self.display, (0, 0))
            self.clock.tick(120)
            pygame.display.update()
