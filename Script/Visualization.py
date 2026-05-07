from webcolors import name_to_rgb as rgb
from Drones import Drone
from Hubs import Map, Hub
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
        self.map = data
        self.drone = Drone(data.start_hub, data.end_hub)
        self.size = 32
        self.camera = [0, 0]
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

# -----------------------drawing the menu-------------------------
    def __draw_menu(self, name: str, pos: tuple[int, int],
                    zone: str, color: str, size: int, img) -> None:
        menu = pygame.image.load("assets/menu/card.png")
        name = self.__draw_text(f"{name}", 20, "yellow")
        menu.blit(name, (6 + (187 - name.size[0]) // 2, 6 + (43 - name.size[1]) // 2))
        menu.blit(self.__draw_text(f"{pos[0]} , {pos[1]}", 20, "yellow"), (10, 250))
        menu.blit(self.__draw_text(f"{zone}", 20, "yellow"), (110, 250))
        menu.blit(self.__draw_text(f"{color}", 20, color), (110, 200))
        menu.blit(self.__draw_text(f"{size}", 20, "yellow"), (10, 200))
        box = pygame.transform.scale(img, (125, 125))
        menu.blit(box, (40, 56))
        self.menu.blit(menu, (self.menus * 200, 0))

# -----------------------drawing grid-------------------------
    def __draw_grid(self) -> None:
        width, height = self.map.size
        ground = pygame.image.load("assets/Ground/ground.png")
        ground = pygame.transform.scale(ground, (self.size, self.size))
        for h in range(height * SPACE):
            for w in range(width * SPACE):
                self.display.blit(ground, self.__draw_pos((w, h)))

# -----------------------drawing hub-------------------------
    def __draw_hub(self, hub: Hub, has_drone_arrived: bool) -> None:
# --------------------------DRAW BOX-----------------------------
        x, y = hub.position
        x, y = self.__draw_pos((x * SPACE, y * SPACE))
        if has_drone_arrived and hub.name == self.drone.next_hub.name and not self.open_box:
            box = pygame.image.load(hub.image.get_image())
        else:
            box = pygame.image.load(hub.image.get_reverse())
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
        drone = pygame.image.load(self.drone.image.get_image())
        drone = pygame.transform.scale(drone, (self.size, self.size))
        x, y = self.__draw_pos((self.drone.x * SPACE, self.drone.y * SPACE))
        nx, ny = self.drone.next_hub.position
        self.display.blit(drone, (x, y - self.size / 2))
        if (
            self.drone.dis > 0
            and self.drone.current_hub.name != self.drone.goal.name
           ):
            self.drone.set_angle((nx, ny))
            self.drone.dis -= self.drone.go_step()
            return False
        elif self.drone.current_hub.name != self.drone.goal.name:
            return True

    def __check_buttons(self) -> None:
        key = pygame.key.get_pressed()
        if key[pygame.K_1]:
            self.size += 1
        elif key[pygame.K_2] and self.size > 0:
            self.size -= 1
        if key[pygame.K_SPACE]:
            self.map.reset()
            self.drone.x = self.map.start_hub.position[0]
            self.drone.y = self.map.start_hub.position[1]
            self.drone.current_hub = self.map.start_hub
            self.drone.path = self.drone.bfs()
            self.drone.set_next_hub()
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
                self.camera[0] += event.pos[0] - self.camera_pos[0]
                self.camera[1] += event.pos[1] - self.camera_pos[1]
                self.camera_pos = event.pos


    def game(self) -> None:
        has_arrived = False
        can_go = False
        while True:
            self.display.fill(rgb("orange"))
            self.__draw_grid()
            key = pygame.key.get_pressed()
            if key[pygame.K_e]:
                can_go = True
            if key[pygame.K_a]:
                can_go = False
            if key[pygame.K_SPACE]:
                has_arrived = False
            for hub in self.map.hubs:
                self.__draw_hub(hub, has_arrived)
            if not has_arrived and can_go:
                has_arrived = self.__draw_drone()
                self.open_box = False
            self.menu.fill((0,0,0,0))
            mx, my = pygame.mouse.get_pos()
            mouse = pygame.mouse.get_just_pressed()
            remove = []
            for i in range(len(self.menus)):
                rect = pygame.Rect(200 * i + 74, 400, 53, 19)
                self.menu.blit(self.menus[i], (i * 200, 0))
                if rect.collidepoint(mx, my) and mouse[0]:
                    remove.append(i)
            if remove:
                self.menus.pop(remove[0])
            self.display.blit(self.menu, (0,400))
            self.__check_buttons()
            self.screen.blit(self.display, (0, 0))
            self.clock.tick(120)
            pygame.display.update()
