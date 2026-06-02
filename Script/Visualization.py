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
        self.buttons = {"pause": pygame.image.load("assets/menu/pause.png"),
                        "resume": pygame.image.load("assets/menu/resume.png"),
                        "reset": pygame.image.load("assets/menu/reset.png"),
                        "zoom_in": pygame.image.load("assets/menu/zoom_in.png"),
                        "zoom_out": pygame.image.load("assets/menu/zoom_out.png"),
                        "speed_up": pygame.image.load("assets/menu/speed_up.png"),
                        "speed_down": pygame.image.load("assets/menu/speed_down.png")}
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
    def __draw_grid(self, ground, borders, water) -> None:
        minw, minh = self.map.min_size
        maxw, maxh = self.map.max_size
        maxh += 1
        maxw += 1
        gx = borders["x"]
        gy = borders["y"]
        gxy = borders["xy"]
        wx = water["x"]
        wy = water["y"]
        wx0 = water["x0"]
        wy0 = water["y0"]
        wxy = water["xy"]
        ground = pygame.transform.scale(ground, (self.size, self.size))
        gx = pygame.transform.scale(gx, (self.size, self.size))
        gy = pygame.transform.scale(gy, (self.size, self.size))
        gxy = pygame.transform.scale(gxy, (self.size, self.size))
        wx = pygame.transform.scale(wx, (self.size, self.size))
        wy = pygame.transform.scale(wy, (self.size, self.size))
        wx0 = pygame.transform.scale(wx0, (self.size, self.size))
        wy0 = pygame.transform.scale(wy0, (self.size, self.size))
        wxy = pygame.transform.scale(wxy, (self.size, self.size))
        for h in range(minh * SPACE - SPACE, maxh * SPACE):
            for w in range(minw * SPACE - SPACE, maxw * SPACE):
                pos = self.__draw_pos((w, h))
                if pos[0] < -self.size  or pos[1] < -self.size:
                    continue
                if pos[0] > 1200 or pos[1] > 700:
                    break
                if w == minw * SPACE - SPACE and h == minh * SPACE - SPACE:
                    self.display.blit(gxy, pos)
                elif w == minw * SPACE - SPACE:
                    self.display.blit(gx, pos)
                elif h == minh * SPACE - SPACE:
                    self.display.blit(gy, pos)
                else:
                    self.display.blit(ground, pos)
                if h == maxh * SPACE - 1:
                    pos = self.__draw_pos((w,h + 1))
                    if w == minw * SPACE - SPACE:
                        self.display.blit(wx0, pos)
                    else:
                        self.display.blit(wy, pos)
            pos = self.__draw_pos((w + 1,h))
            if h == minh * SPACE - SPACE:
                self.display.blit(wy0, pos)
            else:
                self.display.blit(wx, pos)
            if w == maxw * SPACE - 1 and h == maxh * SPACE - 1:
                pos = self.__draw_pos((w + 1, h + 1))
                self.display.blit(wxy, pos)

# -----------------------drawing the menu-------------------------
    def __draw_menu(self, x) -> None:
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
                pos = (200 * i + 168, y - 30)
                rect = x.get_rect(topleft=pos)
                self.menu.blit(self.menus[i], (i * 200, 0))
                self.display.blit(x, pos)
                if rect.collidepoint(mx, my) and mouse[0]:
                    remove.append(i)
            if not self.animations["menu"].is_animating():
                if box.get_rect(topleft=(0,y - 30)).collidepoint(mx, my) and mouse[0]:
                    if y <= 400:
                        self.animations["menu"].start = (0, 400)
                        self.animations["menu"].end = (0, 600)
                    elif y >= 600:
                        self.animations["menu"].start = (0, 600)
                        self.animations["menu"].end = (0, 400)
                    self.animations["menu"].update_distance()
                self.display.blit(box, (0,y - 30))
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
        x, y = self.map.max_size
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

    def check_click(self):
        key = pygame.mouse.get_just_pressed()
        pos = pygame.mouse.get_pos()
        buttons = {"pause": False, "reset": False}
        if key[0]:
            pause_rect = self.buttons["pause"].get_rect(topleft=(1168, 0))
            reset_rect = self.buttons["reset"].get_rect(topleft=(1136, 0))
            speed_up_rect = self.buttons["speed_up"].get_rect(topleft=(1168, 32))
            speed_down_rect = self.buttons["speed_down"].get_rect(topleft=(1136, 32))
            if pause_rect.collidepoint(pos):
                buttons["pause"] = True
            if reset_rect.collidepoint(pos):
                buttons["reset"] = True
            if speed_down_rect.collidepoint(pos):
                for drone in self.drones:
                    if drone.speed < 0.02:
                        print("hhh", drone.speed)
                        break
                    drone.speed -= 0.01
                    drone.movement = Movement((drone.x, drone.y), drone.next_hub.position, drone.speed)
            elif speed_up_rect.collidepoint(pos):
                for drone in self.drones:
                    drone.speed += 0.01
                    drone.movement = Movement((drone.x, drone.y), drone.next_hub.position, drone.speed)
        key = pygame.mouse.get_pressed()
        if key[0]:
            zoom_in_rect = self.buttons["reset"].get_rect(topleft=(1168, 304))
            zoom_out_rect = self.buttons["reset"].get_rect(topleft=(1168, 368))
            if zoom_in_rect.collidepoint(pos):
                self.size += 1
            elif zoom_out_rect.collidepoint(pos) and self.size > 28:
                self.size -= 1
        return buttons

    def reset(self):
        for hub in self.map.hubs:
            hub.visitors = set()
            for line in hub.lines:
                line.visitors = set()
        for drone in self.drones:
            self.map.start_hub.visitors.add(drone)
            drone.x, drone.y = self.map.start_hub.position
            drone.current_hub = self.map.start_hub
            drone.path_finder()
            self.map.reset()
            drone.has_arrived = False

    def game(self) -> None:
        ground = pygame.image.load("assets/Ground/ground.png")
        borders = {"x": pygame.image.load("assets/Ground/ground_x.png"),
                   "y": pygame.image.load("assets/Ground/ground_y.png"),
                   "xy": pygame.image.load("assets/Ground/ground_xy.png")}
        water = {"x": pygame.image.load("assets/Ground/water_x.png"),
                   "y": pygame.image.load("assets/Ground/water_y.png"),
                   "xy": pygame.image.load("assets/Ground/water_xy.png"),
                   "x0": pygame.image.load("assets/Ground/water_x0.png"),
                   "y0": pygame.image.load("assets/Ground/water_y0.png")}
        remove = pygame.image.load("assets/menu/remove.png")
        pause = True
        count = 0
        while True:
            self.display.fill((125, 255, 255))
            self.__draw_grid(ground, borders, water)
            for hub in self.map.hubs:
                self.__draw_hub(hub)
            all_arrived = True
            all_in_goal = True
            for drone in self.drones:
                self.__draw_drone(drone, pause)
                if not drone.has_arrived:
                    all_arrived = False
            if all_arrived and not pause:
                for drone in self.drones:
                    if drone.current_hub.name != drone.next_hub.name:
                        print(f"{drone.name}-{drone.next_hub.name}", end=" ", flush=True)
                    drone.update()
                    self.map.reset()
                    drone.has_arrived = False
                    if drone.current_hub.name != self.map.end_hub.name:
                        all_in_goal = False
                if not all_in_goal:
                    print("")
                    count += 1
            text = self.__draw_text(f"count: {count}", 30, "black")
            self.display.blit(text, (0,0))
            if pause:
                self.display.blit(self.buttons["resume"], (1168, 0))
            else:
                self.display.blit(self.buttons["pause"], (1168, 0))
            self.display.blit(self.buttons["reset"], (1136, 0))
            self.display.blit(self.buttons["speed_up"], (1168, 32))
            self.display.blit(self.buttons["speed_down"], (1136, 32))
            self.display.blit(self.buttons["zoom_in"], (1168, 304))
            self.display.blit(self.buttons["zoom_out"], (1168, 368))
            self.__draw_menu(remove)
            self.__check_buttons()
            check_buttons = self.check_click()
            if check_buttons["pause"]:
                pause = not pause
            if check_buttons["reset"]:
                self.reset()
                pause = True
            self.screen.blit(self.display, (0, 0))
            self.clock.tick(120)
            pygame.display.update()
