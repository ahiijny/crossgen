"""Module for handling the word relation graph.

Defines which words are linked to which words."""

import networkx as nx

def generate_link_graph(words):
    """Given a list of words, return the link graph for the list of words.

    The link graph is an undirected bipartite multigraph where group 0 consists
    of the words, group 1 consists of the letters, and for every letter in a word,
    there exists an edge between that letter and the word.
    """

    G = nx.MultiGraph()
    
    for word in words:
        G.add_node(word, bipartite=0)
        for i, letter in enumerate(word):
            G.add_node(letter, bipartite=1)
            G.add_edge(word, letter, index=i)

    return G

class WordGraph:
    """nodes = words"""

    def __init__(self, words):
        self.words = [word for word in words]

    def link(self, word1, word2, letter, skip1=0, skip2=0): # todo: O(n) word lookup
        """link the skip1th occurrence of letter in word 1(0-indexed)
        with the skip2th occurrence of letter in word 2"""

class Node:
    def __init__(self, value):
        self.value = value
        self.edges = []

class Edge:
    def __init__(self, a, b):
        self.a = a
        self.b = b

def main():
    words = ["words","sound", "never"]
    graph = WordGraph(words)
    graph.link("words", "sound", "o")
    graph.link("sound", "never", "n")

def randbrightcolor():
    import random
    r = lambda: random.randint(128,255)
    return '#%02X%02X%02X' % (r(),r(),r())


if __name__ == "__main__":
    G = generate_link_graph(["reimu", "sanae", "marisa"])
    #import matplotlib.pyplot as plt
    #plt.subplot(1,1,1)
    #nx.draw(G, with_labels=True, font_weight='bold')
    #plt.show()

    import pydot
    for node in G.nodes(data=True):
        if node[1]['bipartite'] == 0:
            G.add_node(node[0], style="filled", color=randbrightcolor())
    for edge in G.edges(data=True, keys=True):
        G.add_edge(edge[0], edge[1], edge[2], label=str(edge[3]['index']))

    nx.drawing.nx_pydot.write_dot(G, "grid.dot")
