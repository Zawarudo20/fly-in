from Hubs import Hub, Map
from time import sleep
from pygame_utils import Animation

class Drone:
    def __init__(self, name, start: Hub, end: Hub) -> None:
        self.start = start
        self.current_hub = start
        self.goal = end
        self.name = name
        self.pos = (start.position[0], start.position[1])
        self.path = []
        self.current_path = []
        self.next_hub: Hub = None
        self.last_visited = None
        self.image = Animation("Drone", "assets/Drone/", 0, 8, 3, 8)
        self.movement = None
        self.has_arrived = False
        self.speed = 0.1

    def move(self):
        self.movement.anim()
        self.pos = self.movement.start

    def update(self, condition):
        if self.current_hub.name != self.goal.name:
            if condition:
                if isinstance(self.current_hub, Hub) and self.current_hub.name != self.next_hub.name:
                    for line in self.current_hub.lines:
                        if self.next_hub in line.hubs:
                            line.visitors.remove(self)
                            break
                self.current_hub = self.next_hub
                self.current_path.pop(0)
            if self.current_hub.name != self.goal.name:
                self.next_hub = self.current_path[1]
                line = None
                if isinstance(self.current_hub, Hub):
                    for line in self.current_hub.lines:
                        if self.next_hub in line.hubs:
                            break
                        else:
                            line = None
                if ((self.next_hub.is_free()
                   or (not isinstance(self.current_hub, Hub)and self in self.next_hub.visitors))
                   and (not line or (line and line.is_free()))
                   and not (not isinstance(self.next_hub, Hub) and not self.current_path[2].is_free())):
                    self.current_hub.visitors.remove(self)
                    if not (isinstance(self.next_hub, Hub) and self.next_hub.zone == "restricted"):
                        self.next_hub.visitors.add(self)
                    if not isinstance(self.next_hub, Hub):
                        self.current_path[2].visitors.add(self)
                    if line:
                        line.visitors.add(self)
                elif condition:
                    self.path_finder()
                elif not condition:
                    self.next_hub = self.current_hub
                    self.current_path.insert(0, self.current_hub)
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
                    case "restricted":
                        g = current.g + 4
                    case "blocked":
                        continue
                    case "priority":
                        g = current.g + 1.5
                    case _:
                        g = current.g + 2
                if current.name == self.current_hub.name:
                    for line in current.lines:
                        if hub in line.hubs:
                            break
                    if not hub.is_free() or not line.is_free():
                        g += 2
                if not hub in visited and not hub in neighbors:
                    hub.path = current
                    hub.g = g
                    neighbors.append(hub)
                if hub in visited and (g < hub.g):
                    hub.path == current
            neighbors.remove(current)
            visited.append(current)
            current = neighbors[0]
            for neighbor in neighbors:
                if (neighbor.g < current.g):
                    current = neighbor
            if current == self.goal:
                break
        hub = self.goal
        self.current_path = []
        while hub:
            self.current_path.insert(0, hub)
            if hub.zone == "restricted" and hub.path:
                for line in hub.path.lines:
                    if hub in line.hubs:
                        self.current_path.insert(0, line)
                        break
            hub = hub.path
        self.update(False)

class map_solver:
    def __init__(self, data: Map) -> None:
        self.map = data
        self.drones: list[Drone] = []
        for i in range(data.drones):
            drone = Drone(f"D{i}", data.start_hub, data.end_hub)
            data.start_hub.visitors.add(drone)
            drone.path_finder()
            data.reset()
            drone.path.append(drone.next_hub)
            self.drones.append(drone)

    def solve(self):
        while True:
            is_all_arrived = True
            for drone in self.drones:
                drone.update(True)
                self.map.reset()
                if drone.current_hub.name != drone.goal.name:
                    drone.path.append(drone.next_hub)
                if drone.next_hub.name != drone.goal.name:
                    is_all_arrived = False
            if is_all_arrived:
                break

    def writer(self):
        i = 0
        for drone in self.drones:
            drone.last_visited = self.map.start_hub
        while True:
            all_writed = True
            for drone in self.drones:
                if i < len(drone.path) and drone.path[i].name != drone.last_visited.name:
                    print(f"{drone.name}-{drone.path[i].name} ", end="")
                    drone.last_visited = drone.path[i]
                    all_writed = False
            print("")
            if all_writed:
                break
            i += 1