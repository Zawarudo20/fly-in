import math
import pygame

class Movement:
    def __init__(self, start, end, speed) -> None:
        self.start = start
        self.end = end
        self.speed = speed
        xa, ya = start
        xb, yb = end
        self.distance = math.sqrt(math.pow(xb - xa, 2) + math.pow(yb - ya, 2))

    def anim(self):
        if self.distance > 0:
            xa, ya = self.start
            xb, yb = self.end
            angle = math.atan2(yb - ya, xb - xa)
            x, y = self.start
            x += math.cos(angle) * self.speed
            y += math.sin(angle) * self.speed
            self.distance -= math.sqrt(math.pow(x - xa, 2) + math.pow(y - ya, 2))
            if self.distance < 0:
                x = xb
                y = yb
            self.start = (x, y)

    def update_distance(self):
        xa, ya = self.start
        xb, yb = self.end
        self.distance = math.sqrt(math.pow(xb - xa, 2) + math.pow(yb - ya, 2))

    def is_animating(self):
        if self.distance > 0:
            return True
        return False

class Animation:
    def __init__(self, name, path, start, end, delay, frames) -> None:
        self.name = name
        self.path = path
        self.start = start
        self.end = end
        self.timer = delay
        self.time = 0
        self.frames = []
        for i in range(frames):
            frame = pygame.image.load(f"{path}{name}{i}.png")
            self.frames.append(frame)

    def anim(self):
        frame = self.frames[self.start]
        if self.start != self.end and self.time >= self.timer:
            if self.start < self.end:
                self.start += 1
            else:
                self.start -= 1
            self.time = 0
        if self.time < self.timer:
            self.time += 1
        return frame
    def is_animating(self):
        if self.start != self.end:
            return True
        return False

class Button:
    def __init__(self, path: str, pos) -> None:
        self.image = pygame.image.load(path)
        self.pos = pos
        self.rect = self.image.get_rect(topleft=pos)

    def change_pos(self, pos):
        self.pos = pos
        self.rect = self.image.get_rect(topleft=pos)

    def is_just_pressed(self) -> bool:
        mouse = pygame.mouse.get_just_pressed()
        if mouse[0] and self.rect.collidepoint(pygame.mouse.get_pos()):
                return True
        return False

    def is_pressed(self) -> bool:
        mouse = pygame.mouse.get_pressed()
        if mouse[0] and self.rect.collidepoint(pygame.mouse.get_pos()):
                return True
        return False

    def built(self, display) -> None:
        display.blit(self.image, self.pos)

class Sound:
    def __init__(self, path: str) -> None:
        self.song = pygame.mixer.Sound(path)
        self.event = None

    def is_playing(self):
        if self.event and self.event.get_busy():
            return True
        return False

    def play(self):
        self.event = self.song.play()

    def stop(self):
        self.song.stop()