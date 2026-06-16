import importlib
import sys
try:
    pygame = importlib.import_module("pygame")
    importlib.import_module("webcolors")
    importlib.import_module("pydantic")
except ImportError as err:
    print(f"\033[41m Module_not_found_error: {err},"
          " Please install it\033[0m")
    sys.exit(1)
from Parsing import Parser
from Visualization import Main_Menu
from Drones import Map_solver


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\033[41mThere is no config file given"
              "run program like this: -->"
              "python3 Script/fly_in.py <config_file>\033[0m")
    parser = Parser(sys.argv[1])
    pygame.init()
    solver = Map_solver()
    menu = Main_Menu(parser, solver)
    menu.visual()
