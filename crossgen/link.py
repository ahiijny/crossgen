"""Module for handling the word relation graph.

Defines which words are linked to which words."""

import networkx as nx

def generate_link_graph(words):
    """Given a list of words, return the link graph for the list of words.

    The link graph is an undirected bipartite multigraph where group 0 consists
    of the words, group 1 consists of the letters, and for every letter in a word,
    there exists an edge between that letter and the word.

    The `index` attribute of an edge indicates the index (0-indexed) of the letter in the word.
    The `key` attribute of an edge indicates its order of occurrence (e.g. for "bob", the
    first b would have key=0, and the second b would have key=1).
    """

    G = nx.MultiGraph()
    
    for word in words:
        G.add_node(word, bipartite=0)
        for i, letter in enumerate(word):
            G.add_node(letter, bipartite=1)
            G.add_edge(word, letter, index=i)

    return G

def write_link_graph_to_file(words, path):
    """Generate the link graph for the given words, and write the Graphviz/DOT form of the graph to file.
    
    Needs pydot.
    """
    import sys
    G = generate_link_graph(words)
    for node in G.nodes(data=True):
        if node[1]['bipartite'] == 0:
            G.add_node(node[0], style="filled", color=_randbrightcolor())
    for edge in G.edges(data=True, keys=True):
        G.add_edge(edge[0], edge[1], edge[2], label=str(edge[3]['index']))

    nx.drawing.nx_pydot.write_dot(G, path)
    print(f"wrote DOT graph to {path}", file=sys.stderr)

def plot_link_graph(words):
    """Plot the link graph for the given words and show it on the screen.

    Needs matplotlib.
    """
    G = generate_link_graph(words)
    import matplotlib.pyplot as plt
    plt.subplot(1,1,1)
    nx.draw(G, with_labels=True, font_weight='bold')
    plt.show()

def _randbrightcolor():
    import random
    r = lambda: random.randint(128,255)
    return '#%02X%02X%02X' % (r(),r(),r())

def _blerp(): # for testing and stuff
    words = ["reimu", "marisa", "sanae"]
    write_link_graph_to_file(words, "grid.dot")
    # plot_link_graph(words)

if __name__ == "__main__": # for debugging and stuff
    _blerp()