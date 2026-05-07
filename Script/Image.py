class Image:
    def __init__(self, name: str, path: str, frames: int, loop: bool) -> None:
        self.name = name
        self.path = path
        self.loop = loop
        self.frames = frames
        self.frame = 0
        self.frame_timer = 2
        self.frame_time = 0

    def get_image(self) -> str:
        if self.frame_time > self.frame_timer:
            self.frame_time = 0
            self.frame += 1
        else:
            self.frame_time += 1
        if self.frame > self.frames:
            if self.loop:
                self.frame = 0
            else:
                self.frame = self.frames
        return f"{self.path}{self.name}{self.frame}.png"

    def get_reverse(self) -> str:
        if self.frame_time > self.frame_timer:
            self.frame_time = 0
            self.frame -= 1
        else:
            self.frame_time += 1
        if self.frame < 0:
            if self.loop:
                self.frame = self.frames
            else:
                self.frame = 0
        return f"{self.path}{self.name}{self.frame}.png"

    def get_current_frame(self) -> str:
        return f"{self.path}{self.name}{self.frame}.png"

    def is_animating(self) -> bool:
        if self.loop:
            return True
        if self.frame == 0 or self.frame == self.frames:
            return False
        return True