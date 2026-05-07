from Hubs import Hub
from copy import deepcopy
from pygame import time
from Image import Image
import math


class Drone:
    def __init__(self, start: Hub, end: Hub) -> None:
        self.current_hub = start
        self.goal = end
        self.x = start.position[0]
        self.y = start.position[1]
        self.angle = 0
        self.path = self.bfs()
        self.next_hub: Hub = self.path[1]
        self.dis = self.__distance(self.current_hub.position, self.next_hub.position)
        self.image = Image("Drone", "assets/Drone/", 7, True)

    @staticmethod
    def __distance(vector_1: tuple[int, int], vector_2: tuple[int, int]) -> float:
        xa, ya = vector_1
        xb, yb = vector_2
        distance = math.sqrt(math.pow(xb - xa, 2) + math.pow(yb - ya, 2))
        return distance

    def set_angle(self, vector: tuple[int, int]) -> float:
        xb, yb = vector
        tita = math.atan2(yb - self.y, xb - self.x)
        self.angle = tita

    def go_step(self) -> float:
        x = self.x
        y = self.y
        dt = time.Clock().tick(60)
        self.x += math.cos(self.angle) * 0.5
        self.y += math.sin(self.angle) * 0.5
        return self.__distance((x, y), (self.x, self.y))

    def set_current_hub(self) -> None:
        self.current_hub = self.path[1]
        self.path.pop(0)
        self.x, self.y = self.current_hub.position

    def set_next_hub(self) -> None:
        if len(self.path) > 1:
            self.next_hub = self.path[1]
            nx, ny = self.next_hub.position
            self.dis = self.__distance((self.x, self.y), (nx, ny))
            return
        self.next_hub = self.current_hub
        self.dis = 0

    def bfs(self) -> list[Hub]:
        paths = [[self.current_hub]]
        self.current_hub.visited = True
        while True:
            new_paths = []
            for path in paths:
                last_hub = path[len(path) - 1]
                for net in last_hub.connections:
                    next = net["HUB"]
                    if not next.visited:
                        new_path = deepcopy(path)
                        next.visited = True
                        new_path.append(next)
                        new_paths.append(new_path)
                        if next.name == self.goal.name:
                            return new_path
            paths = new_paths
