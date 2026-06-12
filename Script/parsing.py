import sys
import re
import pydantic as pd
from Hubs import Hub, Map


class Parsing_Error(Exception):
    def __init__(self, line: int, file: str, message: str) -> None:
        super().__init__(f"Config_file Error:\n\tFile"
                         f" {file}, Line {line}\n\t{message}")


class Parser:
    def __init__(self, file: str) -> None:
        self.file = file
        self.line = 1

    def __check_keyword(self, before: str | None, after: str) -> str:
        if before:
            raise Parsing_Error(self.line,
                                self.file,
                                "MetaData_Error: Two keys repeated")
        return after

    def __get_connection(self, text: str) -> dict:
        connection = re.findall(r"^\s*\w+-\w+", text)
        if not connection:
            raise Parsing_Error(self.line, self.file,
                                "Connection_Error: Wrong Syntax use this -->"
                                " \"connection: <name1>-<name2> [metadata]\"")
        net1, net2 = connection[0].split("-")
        line_size = None
        text = re.sub(r"^\s*\w+-\w+\s*", "", text)
        if text:
            if text[0] == "#":
                return {"connection": {net1, net2}, "size": 1}
            data = re.findall(r"^\[(.*)\]", text)
            if not data:
                raise Parsing_Error(self.line, self.file,
                                    "Connection_Error: Wrong Syntax use this "
                                    "--> \"connection: <name1>-<name2> "
                                    "[metadata]\"")
            data = data[0].split()
            for keywargs in data:
                keyword = keywargs.split("=")
                if len(keyword) != 2 or keyword[1] == "":
                    raise Parsing_Error(self.line, self.file,
                                        "MetaData_Error: Wrong Syntax use this"
                                        "--> \"<Key>=<Value>\"")
                key, word = keyword
                if key == "max_link_capacity":
                    line_size = self.__check_keyword(line_size, word)
                else:
                    raise Parsing_Error(self.line, self.file,
                                        "Connection_MetaData_Error: No key "
                                        f"named {key} use --> "
                                        "\"max_link_capacity\"")
            text = re.sub(r"^\[(.*)\]\s*", "", text)
            if text and text[0] != "#":
                raise Parsing_Error(self.line, self.file,
                                    "Connection_Error: Wrong Syntax use this "
                                    "--> \"connection: <name1>-<name2> "
                                    "[metadata]\"")
        if line_size:
            try:
                size = int(line_size)
            except ValueError:
                raise Parsing_Error(self.line, self.file,
                                    "Value error: max_link_capacity "
                                    "should be a positive intiger")
        else:
            size = 1
        return {"connection": {net1, net2}, "size": size}

    def __check_connection(self,
                           net1: str,
                           net2: str,
                           size: int,
                           hubs: list[Hub]) -> None:
        hub1 = None
        hub2 = None
        for hub in hubs:
            if hub.name == net1:
                hub1 = hub
            elif hub.name == net2:
                hub2 = hub
        if not hub1:
            raise Parsing_Error(self.line, self.file,
                                "Connection_Error there is"
                                f" no hub called {net1}")
        if not hub2:
            raise Parsing_Error(self.line, self.file,
                                "Connection_Error there is "
                                f"no hub called {net2}")
        hub1.connections.append({"HUB": hub2, "SIZE": size})
        hub2.connections.append({"HUB": hub1, "SIZE": size})

    def __get_hub(self, text: str) -> Hub:
        text = re.sub(r"^\s*", "", text)
        name = re.findall(r"^\w+", text)
        text = re.sub(r"^\w+\s+", "", text)
        pos = re.findall(r"^-?\d+\s+-?\d+", text)
        text = re.sub(r"^-?\d+\s+-?\d+\s*", "", text)
        zone_size = None
        color = None
        zone = None
        if not name or not pos:
            raise Parsing_Error(self.line, self.file,
                                "hub_Error: Wrong Syntax use this "
                                "--> \"hub: <name> <x> <y> [metadata]\"")
        pos = pos[0].split()
        if text:
            if text[0] == "#":
                return Hub(name=name[0],
                           position=(int(pos[0]), int(pos[1])),
                           color=color,
                           size=1,
                           zone=zone)
            data = re.findall(r"\[(.*)\]", text)
            if not data:
                raise Parsing_Error(self.line, self.file,
                                    "hub_Error: Wrong Syntax use this "
                                    "--> \"hub: <name> <x> <y> [metadata]\"")
            data = data[0].split()
            for keywargs in data:
                keyword = keywargs.split("=")
                if len(keyword) != 2 or keyword[0] == "":
                    raise Parsing_Error(self.line, self.file,
                                        "MetaData_Error: Wrong Syntax use this"
                                        "--> \"<Key>=<Value>\"")
                key, word = keyword
                if key == "color":
                    color = self.__check_keyword(color, word)
                elif key == "zone":
                    zone = self.__check_keyword(zone, word)
                elif key == "max_drones":
                    zone_size = self.__check_keyword(zone_size, word)
                else:
                    raise Parsing_Error(self.line, self.file,
                                        "Hub_MetaData_Error: No key named "
                                        f"{key} use one of those --> "
                                        "\"color\", \"max_drones\", \"zone\"")
            text = re.sub(r"\[.*\]\s*", "", text)
            if text and text[0] != "#":
                raise Parsing_Error(self.line, self.file,
                                    "hub_Error: Wrong Syntax use this "
                                    "--> \"hub: <name> <x> <y> [metadata]\"")
        if zone_size:
            try:
                size = int(zone_size)
            except ValueError:
                raise Parsing_Error(self.line, self.file,
                                    "Value error: hub size must be a "
                                    "positive intiger")
        else:
            size = 1
        try:
            return Hub(name=name[0],
                       position=(int(pos[0]), int(pos[1])),
                       color=color,
                       size=size,
                       zone=zone)
        except pd.ValidationError as err:
            raise Parsing_Error(self.line, self.file,
                                err.errors()[0]["msg"])

    def __check_hub(self, new_hub: Hub, hubs: list[Hub]) -> None:
        for hub in hubs:
            if hub.name == new_hub.name:
                raise Parsing_Error(self.line, self.file,
                                    "Hub_Error: Hub name is repeated")
            if hub.position == new_hub.position:
                raise Parsing_Error(self.line, self.file,
                                    "Hub_Error: Hub position is repeated")

    def __get_nb_drones(self, lines: list[str]) -> int:
        drones = None
        for line in lines:
            if not line:
                self.line += 1
                continue
            line = re.sub(r"^\s*", "", line)
            if not line or line[0] == "#":
                self.line += 1
                continue
            nb_drones = re.findall(r"^nb_drones: .*", line)
            if nb_drones:
                nb_drones = re.findall(r"^\s*-?\d+", line[11:])
                if not nb_drones:
                    raise Parsing_Error(self.line, self.file,
                                        "nb_drones_error: Wrong"
                                        "Syntax use this"
                                        "--> \"nb_drones: <number>\"")
                line = re.sub(r"^\s*-?\d+\s*", "", line[11:])
                if line and line[0] != "#":
                    raise Parsing_Error(self.line, self.file,
                                        "nb_drones_error: Wrong"
                                        "Syntax use this"
                                        "--> \"nb_drones: <number>\"")
                try:
                    drones = int(nb_drones[0])
                except ValueError:
                    raise Parsing_Error(self.line, self.file,
                                        "Value error nb_drone should"
                                        "be a positive intiger")
                if drones < 1:
                    raise Parsing_Error(self.line,
                                        self.file,
                                        "Value error nb_drone should be"
                                        "greater than or equal to 1")
                self.line += 1
                break
            else:
                raise Parsing_Error(self.line,
                                    self.file,
                                    "Syntax_Error: Wrong Syntax or nb_drones"
                                    " is not the first parameter")
        if not drones:
            raise ValueError("Drones number are messing")
        return drones

    def get_map(self) -> Map:
        with open(sys.argv[1]) as fd:
            text = fd.read()
        lines = text.split("\n")
        start_hub = None
        hubs: list[Hub] = []
        end_hub = None
        connections = []
        drones = self.__get_nb_drones(lines)
        i = self.line
        while i - 2 >= 0:
            lines.pop(i - 2)
            i -= 1
        for line in lines:
            if not line:
                self.line += 1
                continue
            line = re.sub(r"^\s*", "", line)
            if not line or line[0] == "#":
                self.line += 1
                continue
            nb_drones = re.findall(r"^nb_drones: .*", line)
            start = re.findall(r"^start_hub: .*", line)
            hub = re.findall(r"^hub: .*", line)
            end = re.findall(r"^end_hub: .*", line)
            connection = re.findall(r"^connection: .*", line)
            if nb_drones:
                raise Parsing_Error(self.line,
                                    self.file,
                                    "nb_drones_error: Drones number repeated")
            elif start:
                if start_hub:
                    raise Parsing_Error(self.line,
                                        self.file,
                                        "Hubs_Error: Strat hub is repeated")
                start_hub = self.__get_hub(line[11:])
                self.__check_hub(start_hub, hubs)
                hubs.append(start_hub)
            elif hub:
                new_hub = self.__get_hub(line[5:])
                self.__check_hub(new_hub, hubs)
                hubs.append(new_hub)
            elif end:
                if end_hub:
                    raise Parsing_Error(self.line,
                                        self.file,
                                        "Hubs_Error: End hub is repeated")
                end_hub = self.__get_hub(line[8:])
                self.__check_hub(end_hub, hubs)
                hubs.append(end_hub)
            elif connection:
                network = self.__get_connection(line[12:])
                net = network["connection"]
                if len(net) == 1:
                    raise Parsing_Error(self.line,
                                        self.file,
                                        "Connection_Error: Hub can't"
                                        " connect to itself")
                if net in connections:
                    raise Parsing_Error(self.line,
                                        self.file,
                                        "Connection_Error: Connection"
                                        " is repeated")
                connections.append(net)
                hub1, hub2 = net
                self.__check_connection(hub1, hub2, network["size"], hubs)
            else:
                raise Parsing_Error(self.line,
                                    self.file,
                                    "Syntax_Error: Wrong Syntax")
            self.line += 1
        if not start_hub:
            raise ValueError("start_hub is messing")
        if not end_hub:
            raise ValueError("end_hub is messing")
        if not connections:
            raise ValueError("connections are messing")
        return Map(drones=drones,
                   start_hub=start_hub,
                   end_hub=end_hub,
                   hubs=hubs)
