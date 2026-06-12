from Parsing import Parser
from Visualization import Visualizer
from Drones import map_solver
import sys
import pygame

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\033[41mThere is no config file given"
              "run program like this: -->"
              "python3 Script/fly_in.py <config_file>\033[0m")
    parser = Parser(sys.argv[1])
    pygame.init()
    try:
        data = parser.get_map()
        solver = map_solver(data)
    except Exception as err:
        print(f"\033[41m{err}\033[0m")
        exit(1)
    game = Visualizer(data, solver)
    game.game()
