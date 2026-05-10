from Hubs import Hub
from copy import deepcopy
from Animation import Movement, Animation
import math

class Drone:
    def __init__(self, start: Hub, end: Hub) -> None:
        self.current_hub = start
        self.goal = end
        self.x = start.position[0]
        self.y = start.position[1]
        self.path = self.bfs()
        self.next_hub: Hub = self.path[1]
        self.image = Animation("Drone", "assets/Drone/", 0, 8, 3, 8)
        self.movement = Movement((self.x, self.y), (self.next_hub.position[0], self.next_hub.position[1]), 0.5)

    def move(self):
        self.movement.anim()
        self.x, self.y = self.movement.start

    def update(self):
        self.path.pop(0)
        self.current_hub = self.path[0]
        self.next_hub = self.path[1]
        self.movement.start = (self.x, self.y)
        self.movement.end = (self.next_hub.position[0], self.next_hub.position[1])
        self.movement.distance = math.sqrt(math.pow(self.next_hub.position[0] - self.x, 2) + math.pow(self.next_hub.position[1] - self.y, 2))

    def reset(self, start):
        self.x, self.y = start.position
        self.current_hub = start
        self.path = self.bfs()
        self.next_hub = self.path[1]
        self.movement.start = (self.x, self.y)
        self.movement.end = (self.next_hub.position[0], self.next_hub.position[1])
        self.movement.distance = math.sqrt(math.pow(self.next_hub.position[0] - self.x, 2) + math.pow(self.next_hub.position[1] - self.y, 2))

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
                        new_path = path.copy()
                        next.visited = True
                        new_path.append(next)
                        new_paths.append(new_path)
                        if next.name == self.goal.name:
                            return new_path
            paths = new_paths
