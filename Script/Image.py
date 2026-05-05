class Image:
    def __init__(self, name: str, path: str, frames: int) -> None:
        self.name = name
        self.path = path
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
            self.frame = 0
        return f"{self.path}{self.name}{self.frame}.png"
