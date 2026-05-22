from Hubs import Hub
from time import sleep
from Animation import Movement, Animation
import math

def distance(victor1, victor2):
    xa, ya = victor1
    xb, yb = victor2
    return math.sqrt(math.pow(xb - xa, 2) + math.pow(yb - ya, 2))

class Drone:
    def __init__(self, name, start: Hub, end: Hub) -> None:
        self.start = start
        self.current_hub = start
        self.goal = end
        self.name = name
        self.x = start.position[0]
        self.y = start.position[1]
        self.path = []
        self.next_hub: Hub = None
        self.image = Animation("Drone", "assets/Drone/", 0, 8, 3, 8)
        self.movement = None
        self.has_arrived = False

    def move(self):
        self.movement.anim()
        self.x, self.y = self.movement.start

    def update(self):
        if self.current_hub.name != self.goal.name:
            if isinstance(self.current_hub, Hub) and self.current_hub.name != self.next_hub.name:
                for line in self.current_hub.lines:
                    if self.next_hub in line.hubs:
                        line.visitors.remove(self)
                        break
            self.current_hub = self.next_hub
            self.path.pop(0)
            if self.current_hub.name != self.goal.name:
                self.next_hub = self.path[1]
                line = None
                if isinstance(self.current_hub, Hub):
                    for line in self.current_hub.lines:
                        if self.next_hub in line.hubs:
                            break
                        else:
                            line = None
                if (self.next_hub.is_free() or (not isinstance(self.current_hub, Hub) and self in self.next_hub.visitors)) and (not line or (line and line.is_free())):
                    if not (not isinstance(self.next_hub, Hub) and not self.path[2].is_free()):
                        self.current_hub.visitors.remove(self)
                        if not (isinstance(self.next_hub, Hub) and self.next_hub.zone == "restricted"):
                            self.next_hub.visitors.add(self)
                        if not isinstance(self.next_hub, Hub):
                            self.path[2].visitors.add(self)
                        if line:
                            line.visitors.add(self)
                        self.movement = Movement(self.current_hub.position, self.next_hub.position, 0.1)
                    else:
                        self.path_finder()
                else:
                    self.path_finder()
        else:
            self.next_hub = self.current_hub

    def path_finder(self):
        neighbors = [self.current_hub]
        visited = []
        current = self.current_hub
        while True:
            for net in current.connections:
                hub = net["HUB"]
                match hub.zone:
                    case "normal":
                        g = current.g + 2
                    case "restricted":
                        g = current.g + 4
                    case "priority":
                        g = current.g + 1.5
                    case "blocked":
                        continue
                for line in current.lines:
                    if hub in line.hubs:
                        break
                if not hub.is_free() or not line.is_free():
                    g += 2
                h = distance(self.goal.position, hub.position)
                if not hub in visited and not hub in neighbors:
                    hub.path = current
                    hub.g = g
                    hub.h = h
                    neighbors.append(hub)
                if hub in visited and (h + g < hub.g + hub.h or (h + g == hub.g + hub.h and h < hub.h)):
                    hub.path == current
            neighbors.remove(current)
            visited.append(current)
            current = neighbors[0]
            for neighbor in neighbors:
                if ((neighbor.g + neighbor.h) < (current.g + current.h) 
                    or ((neighbor.g + neighbor.h) == (current.g + current.h) and neighbor.h < current.h)):
                    current = neighbor
            if current == self.goal:
                break
        hub = self.goal
        self.path = []
        while hub:
            self.path.insert(0, hub)
            if hub.zone == "restricted" and hub.path:
                for line in hub.path.lines:
                    if hub in line.hubs:
                        self.path.insert(0, line)
                        break
            hub = hub.path
        self.next_hub = self.path[1]
        line = None
        if isinstance(self.current_hub, Hub):
            for line in self.current_hub.lines:
                if self.next_hub in line.hubs:
                    break
                else:
                    line = None
        if self.next_hub.is_free() and (not line or (line and line.is_free())):
            if not (not isinstance(self.next_hub, Hub) and not self.path[2].is_free()):
                self.current_hub.visitors.remove(self)
                if not (isinstance(self.next_hub, Hub) and self.next_hub.zone == "restricted"):
                    self.next_hub.visitors.add(self)
                if not isinstance(self.next_hub, Hub):
                    self.path[2].visitors.add(self)
                if line:
                    line.visitors.add(self)
            else:
                self.next_hub = self.current_hub
                self.path.insert(0, self.current_hub)
        else:
            self.next_hub = self.current_hub
            self.path.insert(0, self.current_hub)
        self.movement = Movement(self.current_hub.position, self.next_hub.position, 0.1)