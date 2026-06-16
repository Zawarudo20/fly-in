import pygame
from pygame_utils import Movement, Button
from Hubs import Hub
from sys import exit
from webcolors import name_to_rgb as rgb


class Menu:
    def __init__(self) -> None:
        self.music = Button("assets/main_menu/music.png",
                            (520, 300))
        self.exit = Button("assets/main_menu/exit.png",
                           (520, 450))
        self.resume = Button("assets/main_menu/resume.png",
                             (520, 220))
        self.display = pygame.Surface((1200, 700))
        self.menu = pygame.image.load("assets/main_menu"
                                      "/game_menu.png").convert()
        self.display.fill((0, 0, 0))
        self.display.blit(self.menu, (420, 100))
        self.reblit()

    def reblit(self) -> None:
        self.music.blit(self.display)
        self.exit.blit(self.display)
        self.resume.blit(self.display)

    def visual(self, screen: pygame.Surface, song: pygame.Sound) -> bool:
        if pygame.mixer.Channel(0).get_busy():
            self.music.image = pygame.image.load(
                "assets/main_menu/music.png").convert()
        else:
            self.music.image = pygame.image.load(
                "assets/""main_menu/music_off.png").convert()
        self.reblit()
        while True:
            if self.resume.is_just_pressed():
                return False
            if self.music.is_just_pressed():
                if pygame.mixer.Channel(0).get_busy():
                    self.music.image = pygame.image.load(
                        "assets/""main_menu/music_off.png").convert()
                    pygame.mixer.Channel(0).stop()
                else:
                    self.music.image = pygame.image.load(
                        "assets/main_menu/music.png").convert()
                    pygame.mixer.Channel(0).play(song, -1)
                self.reblit()
            if self.exit.is_just_pressed():
                return True
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit(0)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        return False
            screen.blit(self.display, (0, 0))
            pygame.display.update()


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


class Deck:
    def __init__(self) -> None:
        self.display = pygame.Surface((1200, 300), pygame.SRCALPHA)
        self.card = pygame.image.load("assets/menu/card.png").convert()
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
        for card in self.cards:
            if card.name == hub.name:
                return
        card = Card(hub, self.card.copy(), image)
        self.cards.append(card)

    def remove_card(self, card: Card) -> None:
        self.cards.remove(card)
