from webcolors import name_to_rgb as rgb
from Drones import Drone, Map_solver
from Hubs import Map
from pygame_utils import Button, Movement, Animation
from Fly_in_utils import Deck, Menu
from Parsing import Parser
import sys
import pygame


class Main_Menu:
    def __init__(self, parser: Parser, solver: Map_solver) -> None:
        pygame.display.set_caption("fly_in")
        pygame.mixer.set_num_channels(2)
        self.song = pygame.Sound("assets/sounds/menu_song.mp3")
        pygame.mixer.Channel(0).play(self.song, -1)
        self.parser = parser
        self.solver = solver
        self.display = pygame.display.set_mode((1200, 700))
        self.menu_logo = pygame.image.load("assets/main_menu/menu_logo.png")
        self.menu_logo = pygame.transform.scale(self.menu_logo, (400, 400))
        self.logo = pygame.image.load("assets/main_menu/logo.png")
        self.menu = pygame.image.load("assets/main_menu/menu.png")
        self.drone = Animation("Drone", "assets/Drone/", 0, 8, 10, 8)
        self.start = Button("assets/main_menu/start.png", (250, 350))
        self.music = Button("assets/main_menu/music.png", (250, 430))
        self.exit = Button("assets/main_menu/exit.png", (250, 510))
        pygame.display.set_icon(self.logo)

    @staticmethod
    def __draw_text(text: str, size: int, color: str) -> pygame.Surface:
        font = pygame.font.Font("assets/font/Minecraft.ttf", size)
        r, g, b = rgb(color)
        result = font.render(text, True, (r, g, b), (0, 0, 0, 0))
        return result

    def error(self, text: str) -> None:
        self.display.fill((0, 0, 0))
        error_line = self.__draw_text(text, 20, "red")
        size = error_line.size[0]
        pos = ((1200 - size) // 2, 200)
        self.display.blit(error_line, pos)
        self.exit.change_pos((550, 400))
        self.exit.blit(self.display)
        sound = pygame.Sound("assets/sounds/error.mp3")
        pygame.Channel(1).play(sound)
        while True:
            if self.exit.is_just_pressed():
                pygame.quit()
                sys.exit(1)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit(0)
            pygame.display.update()

    def visual(self) -> None:
        data = None
        while True:
            if self.drone.start == 8:
                self.drone.start = 0
            self.display.fill((125, 255, 255))
            self.display.blit(self.menu, (0, 0))
            self.display.blit(self.menu_logo, (710, 160))
            self.display.blit(self.logo, (150, 40))
            self.start.blit(self.display)
            self.exit.blit(self.display)
            self.music.blit(self.display)
            image = self.drone.anim()
            image = pygame.transform.scale(image, (100, 100))
            self.display.blit(image, (860, 310))
            if self.exit.is_just_pressed():
                pygame.quit()
                exit(0)
            if self.music.is_just_pressed():
                if pygame.mixer.Channel(0).get_busy():
                    self.music.image = pygame.image.load(
                        "assets/main_menu/music_off.png")
                    pygame.mixer.Channel(0).stop()
                else:
                    self.music.image = pygame.image.load(
                        "assets/main_menu/music.png")
                    pygame.mixer.Channel(0).play(self.song, -1)
            if self.start.is_just_pressed():
                if not data:
                    try:
                        data = self.parser.get_map()
                        self.solver.solve(data)
                    except Exception as err:
                        pygame.Channel(0).stop()
                        self.error(err.__str__())
                        return
                game = Game(data, self.solver)
                game.visual(self.display)
                if pygame.mixer.Channel(0).get_busy():
                    self.music.image = pygame.image.load(
                        "assets/main_menu/music.png")
                    pygame.mixer.Channel(0).play(self.song, -1)
                else:
                    self.music.image = pygame.image.load(
                        "assets/""main_menu/music_off.png")
                self.music.blit(self.display)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit(0)
            pygame.display.update()


class Game:
    def __init__(self, data: Map, solver: Map_solver) -> None:
        self.display = pygame.surface.Surface((1200, 700))
        self.deck = Deck()
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
                        "menu_down": Button("assets/menu/down.png",
                                            (0, 368)),
                        "menu_up": Button("assets/menu/up.png",
                                          (0, 568)),
                        "remove": Button("assets/menu/remove.png",
                                         (0, 0))}
        self.channels = {"music": pygame.mixer.Channel(0),
                         "sfx": pygame.mixer.Channel(1)}
        self.sounds = {"song": pygame.Sound("assets/sounds/song.mp3"),
                       "draw_card": pygame.Sound(
                           "assets/sounds/draw_card.mp3"),
                       "move": pygame.Sound("assets/sounds/move.mp3")}
        self.menu = Menu()
        self.map = data
        self.solver = solver
        self.drones: list[Drone] = solver.drones
        for drone in self.drones:
            drone.current_hub = drone.path[0]
            drone.next_hub = drone.path[1]
            drone.movement = Movement(drone.start.position,
                                      drone.next_hub.position, drone.speed)
        self.size = 32
        self.camera = [600, 60]
        self.camera_pos = (0, 0)
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
        r, g, b = rgb(color)
        result = font.render(text, True, (r, g, b, 10))
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
        for key in self.buttons:
            if key == "resume" and pause:
                self.buttons[key].blit(self.display)
            elif key == "pause" and not pause:
                self.buttons[key].blit(self.display)
            elif key == "remove" or key == "menu_down" or key == "menu_up":
                ...
            else:
                self.buttons[key].blit(self.display)

# -----------------------drawing the menu-------------------------
    def __draw_menu(self) -> None:
        self.deck.animation.anim()
        self.deck.pos = self.deck.animation.start
        if self.deck.cards:
            y = self.deck.pos[1]
            for i in range(len(self.deck.cards)):
                pos = (200 * i + 168, y - 30)
                self.buttons["remove"].change_pos(pos)
                self.buttons["remove"].blit(self.display)
                if self.buttons["remove"].is_just_pressed():
                    self.deck.remove_card(self.deck.cards[i])
            if not self.deck.animation.is_animating():
                if y <= 400:
                    if self.buttons["menu_down"].is_just_pressed():
                        self.deck.down()
                    self.buttons["menu_down"].blit(self.display)
                elif y >= 600:
                    if self.buttons["menu_up"].is_just_pressed():
                        self.deck.up()
                    self.buttons["menu_up"].blit(self.display)
            self.display.blit(self.deck.display, self.deck.pos)
            self.deck.fill_menu()

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
                   blocked: pygame.Surface,
                   start_end: pygame.Surface) -> None:
        normal = pygame.transform.scale(normal,
                                        (self.size,
                                         self.size)).convert_alpha()
        priority = pygame.transform.scale(priority,
                                          (self.size,
                                           self.size)).convert_alpha()
        restricted = pygame.transform.scale(restricted,
                                            (self.size,
                                             self.size)).convert_alpha()
        blocked = pygame.transform.scale(blocked,
                                         (self.size,
                                          self.size)).convert_alpha()
        start_end = pygame.transform.scale(start_end,
                                           (self.size * 2,
                                            self.size * 2)).convert_alpha()
        for hub in self.map.hubs:
            x = float(hub.position[0])
            y = float(hub.position[1])
            x, y = self.__draw_pos((x * 5, y * 5))
            if (hub.name == self.map.start_hub.name or
               hub.name == self.map.end_hub.name):
                box = start_end
                self.display.blit(box, (x - self.size / 2, y - self.size))
                self.display.set_at((x, y), rgb("white"))
            else:
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
                                                   self.size // 2,
                                                   "black"),
                                  (x + self.size / 4, y - self.size / 2))
                if mouse[0] and len(self.deck.cards) <= 5:
                    self.deck.add_card(hub, box)
                    self.channels["sfx"].play(self.sounds["draw_card"])

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

    def __check_keys(self, screen: pygame.Surface) -> bool:
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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return self.menu.visual(screen, self.sounds["song"])
        return False

    def __check_buttons(self) -> dict:
        buttons = {"pause": False, "reset": False}
        if self.buttons["pause"].is_just_pressed():
            buttons["pause"] = True
        if self.buttons["reset"].is_just_pressed():
            buttons["reset"] = True
        if self.buttons["write"].is_just_pressed():
            self.solver.writer()
        if self.buttons["speed_down"].is_just_pressed():
            for drone in self.drones:
                if drone.movement and drone.speed >= 0.02:
                    drone.speed -= 0.01
                    drone.movement = Movement(drone.pos,
                                              drone.next_hub.position,
                                              drone.speed)
        elif self.buttons["speed_up"].is_just_pressed():
            for drone in self.drones:
                if drone.movement:
                    drone.speed += 0.01
                    drone.movement = Movement(drone.pos,
                                              drone.next_hub.position,
                                              drone.speed)
        if self.buttons["zoom_in"].is_pressed():
            self.size += 1
        elif self.buttons["zoom_out"].is_pressed() and self.size > 28:
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

    def visual(self, screen: pygame.Surface) -> None:
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
        start_end = pygame.image.load("assets/box/start_end.png")
        pause = True
        index = 1
        if self.channels["music"].get_busy():
            self.channels["music"].play(self.sounds["song"], -1)
        while True:
            self.display.fill((125, 255, 255))
            self.__draw_grid(ground, borders, water)
            self.__draw_line()
            self.__draw_hub(normal, priority, restricted, blocked, start_end)
            all_arrived = True
            for drone in self.drones:
                self.__draw_drone(drone, pause)
                if not drone.has_arrived:
                    all_arrived = False
            if all_arrived and not pause and index < len(drone.path):
                self.channels["sfx"].play(self.sounds["move"])
                index += 1
                for drone in self.drones:
                    drone.has_arrived = False
                    drone.current_hub = drone.next_hub
                    if drone.current_hub.name != drone.goal.name:
                        drone.next_hub = drone.path[index]
                    drone.movement = Movement(drone.current_hub.position,
                                              drone.next_hub.position,
                                              drone.speed)
            tunrs = self.__draw_text(f"Turns: {index - 1}", 15, "black")
            self.display.blit(tunrs, (10, 10))
            self.__draw_menu()
            if self.__check_keys(screen):
                for drone in self.drones:
                    drone.pos = self.map.start_hub.position
                    drone.current_hub = drone.path[0]
                    drone.next_hub = drone.path[1]
                    drone.movement = Movement(drone.start.position,
                                              drone.next_hub.position,
                                              drone.speed)
                break
            self.__draw_buttons(pause)
            check_buttons = self.__check_buttons()
            if check_buttons["pause"]:
                pause = not pause
            if check_buttons["reset"]:
                self.reset()
                pause = True
                index = 1
            pygame.display.update()
            screen.blit(self.display, (0, 0))
