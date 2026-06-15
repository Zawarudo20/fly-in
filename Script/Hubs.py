import webcolors
import pydantic as pd


class Hub(pd.BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    name: str = pd.Field(min_length=1)
    position: tuple[int, int]
    color: str | None = pd.Field(min_length=1)
    size: int | None = pd.Field(ge=1)
    zone: str | None = pd.Field(min_length=1)
    connections: list[dict] = []
    lines: set = set()
    visitors: set = set()
    g: float = 1
    path: "Hub | None" = None

    @pd.model_validator(mode="after")
    def Validation(self) -> "Hub":
        if not self.color:
            self.color = "white"
        else:
            colors = [color for color in webcolors.names("css3")]
            self.color = self.color.lower()
            if self.color not in colors:
                raise ValueError(f"Hub_MetaData_Error: color \'{self.color}\' "
                                 f"in '{self.name}' is not supported.")
        if not self.zone:
            self.zone = "normal"
        else:
            zones = ["normal", "blocked", "restricted", "priority"]
            self.zone = self.zone.lower()
            if self.zone not in zones:
                raise ValueError(f"Zone \'{self.zone}\' in '{self.name}' is"
                                 f" not supported, Use one of those {zones}")
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
        self.start_hub.size = self.drones
        self.end_hub.size = self.drones
        self.start_hub.zone = "normal"
        self.end_hub.zone = "normal"
        self.hubs.append(self.start_hub)
        self.hubs.append(self.end_hub)
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
        for hub in self.hubs:
            for net in hub.connections:
                hub2 = net["HUB"]
                line = Line(hub2, hub, net["SIZE"])
                hub2.lines.add(line)
                hub.lines.add(line)
        return self

    def reset(self) -> None:
        for hub in self.hubs:
            hub.path = None
            hub.g = 0
