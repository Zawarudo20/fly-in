from copy import deepcopy
from typing import Any
import webcolors
import re
import pygame
import pydantic as pd

class Hub(pd.BaseModel):
    name: str = pd.Field(min_length=1)
    position: tuple[int, int]
    color: str = pd.Field(min_length=1)
    size: int = pd.Field(ge=1)
    zone: str= pd.Field(min_length=1)
    connections: list[dict] = []
    visited: bool = False
    visitors: int = 0

    @pd.model_validator(mode="after")
    def Validation(self):
        x, y = self.position
        if x < 0 or y < 0:
            raise ValueError(f"{self.name} positions must be positive, got {self.position}")
        colors = [color for color in webcolors.names("css3")]
        self.color = self.color.lower()
        if self.color not in colors:
            raise ValueError(f"color \'{self.color}\' in '{self.name}' is not supported,"
                                     f"Use one of those {colors}")
        zones = ["normal", "blocked", "restricted", "priority"]
        self.zone = self.zone.lower()
        if self.zone not in zones:
            raise ValueError(f"Zone \'{self.zone}\' in '{self.name}' is not supported,"
                                     f"Use one of those {zones}")
        for hub in self.connections:
            if hub["SIZE"] < 0:
                raise ValueError(f"Line size can't be negative")
        return self


class Fly_in(pd.BaseModel):
    drones: int = pd.Field(ge=1)
    start_hub: Hub
    end_hub: Hub
    hubs: list[Hub]
    size: tuple[int, int] = (0, 0)

    @pd.model_validator(mode="after")
    def validation(self):
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

    def reset(self):
        for hub in self.hubs:
            hub.visited = False
            hub.visitors = 0
        self.start_hub.visited = False
        self.end_hub.visited = False

def get_hub_data(text: tuple[str]):
    name = text[0]
    pos = (int(text[1]), int(text[2]))
    if text[3]:
        color = re.findall(r"color=(\w+)", text[3], re.IGNORECASE) 
        color = color[0] if color else "white"
        zone = re.findall(r"zone=(\w+)", text[3], re.IGNORECASE)
        zone = zone[0] if zone else "normal"
        size = re.findall(r"max_drones=(\d+)", text[3], re.IGNORECASE)
        size = size[0] if size else "1"
    else:
        color = "cyan"
        zone = "normal"
        size = "1"
    hub = Hub(name=name,
            position=pos,
            color=color,
            zone=zone,
            size=int(size))
    return hub

def set_connection_data(net, hubs: list[Hub], start: Hub, end: Hub):
    name = net[0]
    hub1 = None
    hub2 = None
    if name == start.name:
        hub1 = start
    elif name == end.name:
        hub1 = end
    else:
        for hub in hubs:
            if name == hub.name:
                hub1 = hub
                break
    name = net[1]
    if name == start.name:
        hub2 = start
    elif name == end.name:
        hub2 = end
    else:
        for hub in hubs:
            if name == hub.name:
                hub2 = hub
                break
    if not hub1 or not hub2:
        return
    size = re.findall(r"max_link_capacity=(-?\d+)", net[2])
    size = int(size[0]) if size else 1
    a = {"HUB": hub1, "SIZE": size}
    b = {"HUB": hub2, "SIZE": size}
    hub1.connections.append(b)
    hub2.connections.append(a)

def get_values():
    with open("config.txt") as fd:
        text = fd.read()
    drones = re.findall(r"^\s*nb_drones:\s*(-?\d+)", text, re.IGNORECASE)
    start = re.findall(r"^start_hub:\s*(\w+)\s+(-?\d+)\s+(-?\d+)\s*(?:\[(.*?)\])?",text, re.MULTILINE | re.IGNORECASE)
    end = re.findall(r"^end_hub:\s*(\w+)\s+(-?\d+)\s+(-?\d+)\s*(?:\[(.*?)\])?",text, re.IGNORECASE | re.MULTILINE)
    hubs = re.findall(r"^hub:\s*(\w+)\s+(-?\d+)\s+(-?\d+)\s*(?:\[(.*?)\])?",text, re.IGNORECASE | re.MULTILINE)
    nets = re.findall(r"^connection:\s*(\w+)-(\w+)\s*(?:\[(.*?)\])?",text, re.IGNORECASE | re.MULTILINE)
    if not start:
        raise ValueError("Start hub is missing")
    if not end:
        raise ValueError("End hub is missing")
    start = get_hub_data(start[0])
    end = get_hub_data(end[0])
    positions = []
    for hub in hubs:
        positions.append(get_hub_data(deepcopy(hub)))
    for net in nets:
        set_connection_data(net, positions, start, end)
    return Fly_in(
        drones=int(drones[0]),
        start_hub=start,
        end_hub=end,
        hubs=positions,
    )
