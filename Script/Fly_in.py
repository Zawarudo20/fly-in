from Parsing import Parser
from Visualization import Visualizer
from Drones import map_solver
from sys import exit
import pygame

if __name__ == "__main__":
    parser = Parser()
    pygame.init()
    try:
        data = parser.get_values("config.txt")
        solver = map_solver(data)
    except Exception as err:
        print(f"\033[41m{err}\033[0m")
        exit(1)
    game = Visualizer(data, solver)
    game.game()
