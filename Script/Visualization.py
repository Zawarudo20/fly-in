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
        self.menu = pygame.Surface((500, 600), pygame.SRCALPHA)
        self.is_menu_active = False
        self.map = data
        self.drone = Drone(data.start_hub, data.end_hub)
        self.size = 32
        self.camera = [0, 0]
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
    def __draw_text(text: str, font) -> pygame.Font:
        font = pygame.font.Font(None, font)
        text = font.render(text, True, rgb("black"))
        return text

# -----------------------drawing the menu-------------------------
    def __draw_menu(self, name: str, pos: tuple[int, int],
                    zone: str, color: str, size: int) -> None:
        self.menu.fill(rgb("white"))
        self.menu.blit(self.__draw_text(f"name: {name}", 30), (200, 40))
        self.menu.blit(self.__draw_text(f"position: {pos}", 30), (200, 80))
        self.menu.blit(self.__draw_text(f"type: {zone}", 30), (200, 120))
        self.menu.blit(self.__draw_text(f"color: {color}", 30), (200, 160))
        self.menu.blit(self.__draw_text(f"size: {size}", 30), (200, 200))

# -----------------------drawing grid-------------------------
    def __draw_grid(self) -> None:
        width, height = self.map.size
        ground = pygame.image.load("assets/Ground/ground.png")
        ground = pygame.transform.scale(ground, (self.size, self.size))
        for h in range(height * SPACE):
            for w in range(width * SPACE):
                self.display.blit(ground, self.__draw_pos((w, h)))

# -----------------------drawing hub-------------------------
    def __draw_hub(self, hub: Hub) -> None:
# --------------------------DRAW BOX-----------------------------
        x, y = hub.position
        x, y = self.__draw_pos((x * SPACE, y * SPACE))
        box = pygame.image.load("assets/close_box/box0.png")
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
        if rect.collidepoint(xm, xy):
            self.display.blit(self.__draw_text(hub.name, self.size),
                              (x + self.size / 4, y - self.size / 2))
            mouse = pygame.mouse.get_just_pressed()
            if mouse[0]:
                self.__draw_menu(hub.name, hub.position, hub.zone,
                                 hub.color, hub.size)
                self.is_menu_active = True

# -----------------------drawing drone---------------------------
    def __draw_drone(self) -> None:
        drone = pygame.image.load(self.drone.image.get_image())
        drone = pygame.transform.scale(drone, (self.size, self.size))
        x, y = self.__draw_pos((self.drone.x * SPACE, self.drone.y * SPACE))
        nx, ny = self.drone.next_hub.position
        self.display.blit(drone, (x, y - self.size / 2))
        if (
            self.drone.dis > 0.5
            and self.drone.current_hub.name != self.drone.goal.name
           ):
            self.drone.set_angle((nx, ny))
            self.drone.dis -= self.drone.go_step()
        elif self.drone.current_hub.name != self.drone.goal.name:
            self.drone.set_current_hub()
            self.drone.set_next_hub()

    def __check_buttons(self, x: pygame.Rect) -> None:
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
                if self.is_menu_active and x.collidepoint(self.camera_pos):
                    self.is_menu_active = False
            elif event.type == pygame.MOUSEBUTTONUP:
                self.isdragging = False
            if event.type == pygame.MOUSEMOTION and self.isdragging:
                self.camera[0] += event.pos[0] - self.camera_pos[0]
                self.camera[1] += event.pos[1] - self.camera_pos[1]
                self.camera_pos = event.pos

    def game(self) -> None:
        while True:
            self.display.fill(rgb("orange"))
            self.__draw_grid()
            for hub in self.map.hubs:
                self.__draw_hub(hub)
            quit = pygame.Surface((50, 50), pygame.SRCALPHA)
            if self.is_menu_active:
                quit.fill(rgb("red"))
                quit.blit(self.__draw_text(' X', 60), (0, 0))
                self.menu.blit(quit, (0, 0))
                self.display.blit(self.menu, (780, 0))
            self.__draw_drone()
            self.__check_buttons(quit.get_rect(topleft=(780, 0)))
            self.screen.blit(self.display, (0, 0))
            self.clock.tick(120)
            pygame.display.update()
