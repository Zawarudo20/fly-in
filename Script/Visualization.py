from webcolors import name_to_rgb as rgb
from Drones import Drone, map_solver
from Hubs import Map, Hub
from pygame_utils import Button, Movement, Sound
import sys
import pygame


class Card:
    def __init__(self,
                 hub: Hub,
                 image: pygame.Surface,
                 box: pygame.Surface) -> None:
        self.name = hub.name
        self.color = hub.color
        self.x = hub.position[0]
        self.y = hub.position[1]
        self.zone = hub.zone
        self.size = hub.size
        self.image = image
        self.box = box
        self.fill_card()

    @staticmethod
    def __draw_text(text: str, size: int, color: str) -> pygame.Surface:
        font = pygame.font.Font("assets/font/Minecraft.ttf", size)
        result = font.render(text, True, rgb(color))
        return result

    def fill_card(self) -> None:
        width, height = self.image.get_size()
        for h in range(height):
            for w in range(width):
                color = self.image.get_at((w, h))
                if color == (255, 0, 0):
                    self.image.set_at((w, h), rgb(self.color))
        name = self.__draw_text(f"{self.name}", 15, "black")
        self.image.blit(name, (21 + (159 - name.size[0]) // 2,
                               144 + (17 - name.size[1]) // 2))
        self.image.blit(self.__draw_text(f"{self.x}", 20, "red"),
                        (40, 270))
        self.image.blit(self.__draw_text(f"{self.y}", 20, "green"),
                        (70, 270))
        zone = self.__draw_text(f"{self.zone}", 20, "black")
        self.image.blit(zone, (25 + (149 - zone.size[0]) // 2,
                               186 + (88 - zone.size[1]) // 2))
        size = self.__draw_text(f"{self.size}", 15, "black")
        self.image.blit(size, (150 + (25 - size.size[0]) // 2,
                               23 + (18 - size.size[1]) // 2))
        box = pygame.transform.scale(self.box, (125, 125))
        self.image.blit(box, (40, 8))


class Menu:
    def __init__(self) -> None:
        self.display = pygame.Surface((1200, 300), pygame.SRCALPHA)
        self.card = pygame.image.load("assets/menu/card.png")
        self.cards: list[Card] = []
        self.animation = Movement((0, 400), (0, 400), 20)
        self.pos = (0.0, 400.0)

    def down(self) -> None:
        self.animation.start = (0, 400)
        self.animation.end = (0, 600)
        self.animation.update_distance()

    def up(self) -> None:
        self.animation.start = (0, 600)
        self.animation.end = (0, 400)
        self.animation.update_distance()

    def fill_menu(self) -> None:
        self.display.fill((0, 0, 0, 0))
        for i in range(len(self.cards)):
            self.display.blit(self.cards[i].image, (i * 200, 0))

    def add_card(self, hub: Hub, image: pygame.Surface) -> None:
        if len(self.cards) > 5:
            return
        for card in self.cards:
            if card.name == hub.name:
                return
        card = Card(hub, self.card.copy(), image)
        self.cards.append(card)

    def remove_card(self, card: Card) -> None:
        self.cards.remove(card)


class Visualizer:
    def __init__(self, data: Map, solver: map_solver) -> None:
        pygame.display.set_caption("fly_in")
        self.screen = pygame.display.set_mode((1200, 700))
        self.display = pygame.Surface((1200, 700), pygame.SRCALPHA)
        self.menu = Menu()
        self.buttons = {"pause": Button("assets/menu/pause.png",
                                        (1168, 0)),
                        "resume": Button("assets/menu/resume.png",
                                         (1168, 0)),
                        "reset": Button("assets/menu/reset.png",
                                        (1136, 0)),
                        "zoom_in": Button("assets/menu/zoom_in.png",
                                          (1168, 32)),
                        "zoom_out": Button("assets/menu/zoom_out.png",
                                           (1136, 32)),
                        "speed_up": Button("assets/menu/speed_up.png",
                                           (1168, 64)),
                        "speed_down": Button("assets/menu/speed_down.png",
                                             (1136, 64)),
                        "write": Button("assets/menu/write.png",
                                        (1104, 0)),
                        "song": Button("assets/menu/song.png",
                                       (1072, 0)),
                        "menu_down": Button("assets/menu/down.png",
                                            (0, 368)),
                        "menu_up": Button("assets/menu/up.png",
                                          (0, 568)),
                        "remove": Button("assets/menu/remove.png",
                                         (0, 0))}
        self.sounds = {"song": Sound("assets/sounds/song.mp3"),
                       "click": Sound("assets/sounds/click.mp3")}
        self.map = data
        self.solver = solver
        solver.solve()
        self.drones: list[Drone] = solver.drones
        for drone in self.drones:
            drone.current_hub = data.start_hub
            drone.next_hub = drone.path[1]
            drone.movement = Movement(drone.start.position,
                                      drone.next_hub.position, drone.speed)
        self.size = 32
        self.camera = [600, 60]
        self.camera_pos = (0, 0)
        self.clock = pygame.time.Clock()
        self.isdragging = False

# ---------------------Get position for drawing-------------------
    def __draw_pos(self,
                   vector: tuple[float, float]) -> tuple[float, float]:
        xv, yv = vector
        x = xv * self.size / 2 - yv * self.size / 2 + self.camera[0]
        y = xv * self.size / 4 + yv * self.size / 4 + self.camera[1]
        return (x, y)

# -----------------------drawing the text-------------------------
    @staticmethod
    def __draw_text(text: str, size: int, color: str) -> pygame.Surface:
        font = pygame.font.Font("assets/font/Minecraft.ttf", size)
        result = font.render(text, True, rgb(color))
        return result

# -----------------------drawing grid-------------------------
    def __draw_grid(self,
                    ground: pygame.Surface,
                    borders: dict[str, pygame.Surface],
                    water: dict[str, pygame.Surface]) -> None:
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
        for h in range(minh * 5 - 5, maxh * 5):
            for w in range(minw * 5 - 5, maxw * 5):
                pos = self.__draw_pos((w, h))
                if pos[0] < -self.size or pos[1] < -self.size:
                    continue
                if pos[0] > 1200 or pos[1] > 700:
                    break
                if w == minw * 5 - 5 and h == minh * 5 - 5:
                    self.display.blit(gxy, pos)
                elif w == minw * 5 - 5:
                    self.display.blit(gx, pos)
                elif h == minh * 5 - 5:
                    self.display.blit(gy, pos)
                else:
                    self.display.blit(ground, pos)
                if h == maxh * 5 - 1:
                    pos = self.__draw_pos((w, h + 1))
                    if w == minw * 5 - 5:
                        self.display.blit(wx0, pos)
                    else:
                        self.display.blit(wy, pos)
            pos = self.__draw_pos((w + 1, h))
            if h == minh * 5 - 5:
                self.display.blit(wy0, pos)
            else:
                self.display.blit(wx, pos)
            if w == maxw * 5 - 1 and h == maxh * 5 - 1:
                pos = self.__draw_pos((w + 1, h + 1))
                self.display.blit(wxy, pos)

    def __draw_buttons(self, pause: bool) -> None:
        if pause:
            self.buttons["resume"].built(self.display)
        else:
            self.buttons["pause"].built(self.display)
        self.buttons["reset"].built(self.display)
        self.buttons["write"].built(self.display)
        self.buttons["song"].built(self.display)
        self.buttons["speed_up"].built(self.display)
        self.buttons["speed_down"].built(self.display)
        self.buttons["zoom_in"].built(self.display)
        self.buttons["zoom_out"].built(self.display)

# -----------------------drawing the menu-------------------------
    def __draw_menu(self) -> None:
        self.menu.animation.anim()
        self.menu.pos = self.menu.animation.start
        if self.menu.cards:
            y = self.menu.pos[1]
            for i in range(len(self.menu.cards)):
                pos = (200 * i + 168, y - 30)
                self.buttons["remove"].change_pos(pos)
                self.buttons["remove"].built(self.display)
                if self.buttons["remove"].is_just_pressed():
                    self.menu.remove_card(self.menu.cards[i])
            if not self.menu.animation.is_animating():
                if y <= 400:
                    if self.buttons["menu_down"].is_just_pressed():
                        self.menu.down()
                    self.buttons["menu_down"].built(self.display)
                elif y >= 600:
                    if self.buttons["menu_up"].is_just_pressed():
                        self.menu.up()
                    self.buttons["menu_up"].built(self.display)
            self.display.blit(self.menu.display, self.menu.pos)
            self.menu.fill_menu()

    def __draw_line(self) -> None:
        for hub in self.map.hubs:
            x = float(hub.position[0])
            y = float(hub.position[1])
            x, y = self.__draw_pos((x * 5, y * 5))
            for net in hub.connections:
                xh, yh = net["HUB"].position
                xh, yh = self.__draw_pos((xh * 5, yh * 5))
                pygame.draw.line(self.display, rgb("brown"),
                                 (x + self.size / 2, y + self.size / 2),
                                 (xh + + self.size / 2, yh + + self.size / 2),
                                 5)

# -----------------------drawing hub-------------------------
    def __draw_hub(self,
                   normal: pygame.Surface,
                   priority: pygame.Surface,
                   restricted: pygame.Surface,
                   blocked: pygame.Surface) -> None:
        normal = pygame.transform.scale(normal, (self.size, self.size))
        priority = pygame.transform.scale(priority, (self.size, self.size))
        restricted = pygame.transform.scale(restricted, (self.size, self.size))
        blocked = pygame.transform.scale(blocked, (self.size, self.size))
        for hub in self.map.hubs:
            x = float(hub.position[0])
            y = float(hub.position[1])
            x, y = self.__draw_pos((x * 5, y * 5))
            if hub.zone == "normal":
                box = normal.copy()
            elif hub.zone == "priority":
                box = priority.copy()
            elif hub.zone == "restricted":
                box = restricted.copy()
            elif hub.zone == "blocked":
                box = blocked.copy()
            width, height = box.get_size()
            for h in range(height):
                for w in range(width):
                    color = box.get_at((w, h))
                    if color == (255, 255, 255):
                        box.set_at((w, h),
                                   rgb(hub.color))
            self.display.blit(box, (x, y - self.size / 4))
    # --------------------CHECK MOUSE POSITION------------------------
            xm, xy = pygame.mouse.get_pos()
            rect = box.get_rect(topleft=(x, y))
            mouse = pygame.mouse.get_just_pressed()
            if rect.collidepoint(xm, xy):
                self.display.blit(self.__draw_text(hub.name,
                                                   self.size,
                                                   "black"),
                                  (x + self.size / 4, y - self.size / 2))
                if mouse[0]:
                    self.menu.add_card(hub, box)

# -----------------------drawing drone---------------------------
    def __draw_drone(self, drone: Drone, pause: bool) -> None:
        image = drone.image.anim()
        image = pygame.transform.scale(image, (self.size, self.size))
        if drone.image.start == 8:
            drone.image.start = 0
        x, y = self.__draw_pos((drone.pos[0] * 5, drone.pos[1] * 5))
        self.display.blit(image, (x, y - self.size / 2))
        if drone.movement:
            if drone.movement.is_animating() and not pause:
                drone.move()
            elif not drone.movement.is_animating():
                drone.has_arrived = True

    def __check_buttons(self) -> None:
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

    def check_click(self) -> dict:
        buttons = {"pause": False, "reset": False, "music": False}
        if self.buttons["pause"].is_just_pressed():
            self.sounds["click"].play()
            buttons["pause"] = True
        if self.buttons["reset"].is_just_pressed():
            self.sounds["click"].play()
            buttons["reset"] = True
        if self.buttons["write"].is_just_pressed():
            self.sounds["click"].play()
            self.solver.writer()
        if self.buttons["speed_down"].is_just_pressed():
            self.sounds["click"].play()
            for drone in self.drones:
                if drone.movement:
                    drone.speed -= 0.01
                    drone.movement = Movement(drone.pos,
                                              drone.next_hub.position,
                                              drone.speed)
        elif self.buttons["speed_up"].is_just_pressed():
            self.sounds["click"].play()
            for drone in self.drones:
                if drone.movement:
                    drone.speed += 0.01
                    drone.movement = Movement(drone.pos,
                                              drone.next_hub.position,
                                              drone.speed)
        if self.buttons["song"].is_just_pressed():
            self.sounds["click"].play()
            buttons["music"] = True
        if self.buttons["zoom_in"].is_pressed():
            self.sounds["click"].play()
            self.size += 1
        elif self.buttons["zoom_out"].is_pressed() and self.size > 28:
            self.sounds["click"].play()
            self.size -= 1
        return buttons

    def reset(self) -> None:
        for drone in self.drones:
            drone.pos = self.map.start_hub.position
            drone.current_hub = self.map.start_hub
            drone.next_hub = drone.path[1]
            drone.has_arrived = False
            drone.movement = Movement(drone.current_hub.position,
                                      drone.next_hub.position,
                                      drone.speed)

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
        normal = pygame.image.load("assets/box/box_normal.png")
        priority = pygame.image.load("assets/box/box_priority.png")
        restricted = pygame.image.load("assets/box/box_restricted.png")
        blocked = pygame.image.load("assets/box/box_blocked.png")
        pause = True
        music = True
        index = 0
        self.sounds["song"].play()
        while True:
            if music and not self.sounds["song"].is_playing():
                self.sounds["song"].play()
            elif not music and self.sounds["song"].is_playing():
                self.sounds["song"].stop()
            self.display.fill((125, 255, 255))
            self.__draw_grid(ground, borders, water)
            self.__draw_line()
            self.__draw_hub(normal, priority, restricted, blocked)
            all_arrived = True
            for drone in self.drones:
                self.__draw_drone(drone, pause)
                if not drone.has_arrived:
                    all_arrived = False
            if all_arrived and not pause:
                index += 1
                for drone in self.drones:
                    drone.has_arrived = False
                    drone.current_hub = drone.next_hub
                    if drone.current_hub.name != drone.goal.name:
                        drone.next_hub = drone.path[index]
                    drone.movement = Movement(drone.current_hub.position,
                                              drone.next_hub.position,
                                              drone.speed)
            self.__draw_menu()
            self.__check_buttons()
            self.__draw_buttons(pause)
            check_buttons = self.check_click()
            if check_buttons["pause"]:
                pause = not pause
            if check_buttons["reset"]:
                self.reset()
                pause = True
                index = 0
            if check_buttons["music"]:
                music = not music
            self.screen.blit(self.display, (0, 0))
            self.clock.tick(120)
            pygame.display.update()
