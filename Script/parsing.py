from copy import deepcopy
from Hubs import Hub, Map
import re


class Parser:
    @staticmethod
    def __get_hub_data(text: tuple[str]) -> Hub:
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

    @staticmethod
    def __get_connection_data(net: tuple[str], hubs: list[Hub], start: Hub, end: Hub) -> None:
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

    def get_values(self, file_name: str) -> Map:
        with open(file_name) as fd:
            text = fd.read()
        drones = re.findall(r"^\s*nb_drones:\s*(-?\d+)",
                            text, re.IGNORECASE)
        start = re.findall(r"^start_hub:\s*(\w+)\s+(-?\d+)\s+"
                           r"(-?\d+)\s*(?:\[(.*?)\])?",
                           text, re.MULTILINE | re.IGNORECASE)
        end = re.findall(r"^end_hub:\s*(\w+)\s+(-?\d+)\s+"
                         r"(-?\d+)\s*(?:\[(.*?)\])?",
                         text, re.IGNORECASE | re.MULTILINE)
        hubs = re.findall(r"^hub:\s*(\w+)\s+(-?\d+)\s+"
                          r"(-?\d+)\s*(?:\[(.*?)\])?",
                          text, re.IGNORECASE | re.MULTILINE)
        nets = re.findall(r"^connection:\s*(\w+)-(\w+)\s*(?:\[(.*?)\])?",
                          text, re.IGNORECASE | re.MULTILINE)
        if not start:
            raise ValueError("Start hub is missing")
        if not end:
            raise ValueError("End hub is missing")
        start = self.__get_hub_data(start[0])
        end = self.__get_hub_data(end[0])
        positions = []
        for hub in hubs:
            positions.append(self.__get_hub_data(deepcopy(hub)))
        for net in nets:
            self.__get_connection_data(net, positions, start, end)
        return Map(
            drones=int(drones[0]),
            start_hub=start,
            end_hub=end,
            hubs=positions,
        )
