import webcolors
import pydantic as pd


class Hub(pd.BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    name: str = pd.Field(min_length=1)
    position: tuple[int, int]
    color: str = pd.Field(min_length=1)
    size: int = pd.Field(ge=1)
    zone: str = pd.Field(min_length=1)
    connections: list[dict] = []
    lines: set = set()
    visitors: set = set()
    g: float = 1
    path: "Hub | None" = None

    @pd.model_validator(mode="after")
    def Validation(self) -> "Hub":
        colors = [color for color in webcolors.names("css3")]
        self.color = self.color.lower()
        if self.color not in colors:
            raise ValueError(f"color \'{self.color}\' in '{self.name}'"
                             f" is not supported, Use one of those {colors}")
        zones = ["normal", "blocked", "restricted", "priority"]
        self.zone = self.zone.lower()
        if self.zone not in zones:
            raise ValueError(f"Zone \'{self.zone}\' in '{self.name}' is"
                             f" not supported, Use one of those {zones}")
        for hub in self.connections:
            if hub["SIZE"] < 0:
                raise ValueError("Line size can't be negative")
        for net in self.connections:
            hub = net["HUB"]
            line = Line(self, hub, net["SIZE"])
            self.lines.add(line)
            hub.lines.add(line)
        return self

    def is_free(self) -> bool:
        if self.size != len(self.visitors):
            return True
        return False


class Line:
    def __init__(self, hub1: Hub, hub2: Hub, size: int) -> None:
        self.name = f"{hub1.name}-{hub2.name}"
        self.hubs = [hub1, hub2]
        self.size = size
        self.visitors: set = set()
        xa, ya = hub1.position
        xb, yb = hub2.position
        self.position = ((xa + xb) / 2, (ya + yb) / 2)

    def is_free(self) -> bool:
        if self.size != len(self.visitors):
            return True
        return False


class Map(pd.BaseModel):
    drones: int = pd.Field(ge=1)
    start_hub: Hub
    end_hub: Hub
    hubs: list[Hub]
    min_size: tuple[int, int] = (0, 0)
    max_size: tuple[int, int] = (0, 0)

    @pd.model_validator(mode="after")
    def validation(self) -> "Map":
        if not self.start_hub.connections:
            raise ValueError("There not connection to the start")
        if not self.end_hub.connections:
            raise ValueError("There not connection to the end")
        self.start_hub.size = self.drones
        self.end_hub.size = self.drones
        self.hubs.append(self.start_hub)
        self.hubs.append(self.end_hub)
        set_names = {hub.name for hub in self.hubs}
        if len(set_names) != len(self.hubs):
            raise ValueError("two or more Hubs share the same name")
        set_pos = {hub.position for hub in self.hubs}
        if len(set_pos) != len(self.hubs):
            raise ValueError("two or more Hubs share the same cordinate")
        xi, yi = self.start_hub.position
        xa, ya = self.start_hub.position
        for hub in self.hubs:
            xh, yh = hub.position
            xa = xh if xa < xh else xa
            ya = yh if ya < yh else ya
            xi = xh if xi > xh else xi
            yi = yh if yi > yh else yi
        self.min_size = (xi, yi)
        self.max_size = (xa, ya)
        self.hubs = sorted(self.hubs, key=lambda x: x.position[0])
        return self

    def reset(self) -> None:
        for hub in self.hubs:
            hub.path = None
            hub.g = 0
