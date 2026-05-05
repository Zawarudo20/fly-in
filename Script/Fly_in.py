from Parsing import Parser
from Visualization import Visualizor

parser = Parser()
data = parser.get_values("config.txt")
game = Visualizor(data)
game.game()
