from Parsing import Parser
from Visualization import Visualizor
from Drones import map_solver

parser = Parser()
data = parser.get_values("config.txt")
solver = map_solver(data)
game = Visualizor(data, solver)
game.game()
