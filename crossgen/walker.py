import networkx as nx

from crossgen import link
from crossgen import grid

def generate_crosswords(words):
    """words is a sequence of words"""

    base = link.WordGraph(words)
    tree = nx.Graph()
    tree.add_node(base)

def generate_crosswords_derp(words):
    """words is a sequence of words"""

    crosswords = []
    cw = grid.Grid()
    cw.place("lapis", 0, 0, grid.HORIZONTAL)
    cw.place("peridot", 2, 0, grid.VERTICAL)
    crosswords.append(cw)
    for crossword in crosswords:
        yield crossword
    