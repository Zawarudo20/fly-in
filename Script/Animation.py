import math

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
