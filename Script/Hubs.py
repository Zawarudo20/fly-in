import webcolors
import pydantic as pd


class Hub(pd.BaseModel):
    name: str = pd.Field(min_length=1)
    position: tuple[int, int]
    color: str = pd.Field(min_length=1)
    size: int = pd.Field(ge=1)
    zone: str = pd.Field(min_length=1)
    connections: list[dict] = []
    visited: bool = False
    visitors: int = 0

    @pd.model_validator(mode="after")
    def Validation(self) -> object:
        x, y = self.position
        if x < 0 or y < 0:
            raise ValueError(f"{self.name} positions must be positive,"
                             f" got {self.position}")
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
        return self


class Map(pd.BaseModel):
    drones: int = pd.Field(ge=1)
    start_hub: Hub
    end_hub: Hub
    hubs: list[Hub]
    size: tuple[int, int] = (0, 0)

    @pd.model_validator(mode="after")
    def validation(self) -> object:
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
        x = 0
        y = 0
        for hub in self.hubs:
            xh, yh = hub.position
            x = xh if x < xh else x
            y = yh if y < yh else y
        self.size = (x + 1, y + 1)
        self.hubs = sorted(self.hubs, key=lambda x: x.position[0])
        return self

    def reset(self) -> None:
        for hub in self.hubs:
            hub.visited = False
            hub.visitors = 0
        self.start_hub.visited = False
        self.end_hub.visited = False
