import networkx as nx
import queue
import random
from crossgen import link
from crossgen import grid

def generate_crosswords(words):
    """words is a sequence of words"""

    base = link.generate_link_graph(words)
    tree = nx.Graph()
    tree.add_node(base)
    unused_words = list(words)

    stack = [(base, unused_words)]

    while len(stack) > 0:
        graph, unused_words = stack.pop()
        graph = tree.copy()
        if len(unused_words) == 0:
            continue
        next = unused_words[0]

def generate_crosswords_derp():
    """words is a sequence of words"""

    crosswords = []
    cw = grid.Grid()
    cw.add_word("lapis", 0, 0, grid.EAST)
    cw.add_word("peridot", 2, 0, grid.SOUTH)
    crosswords.append(cw)
    for crossword in crosswords:
        yield crossword
    
def walk_test():
    words = ['reimu', 'marisa', 'sanae']
    g = link.generate_link_graph(words)

    base = nx.MultiGraph()

    tree = nx.Graph()
    tree.add_node((base, link.LETTER))
    used_nodes = {base : set()}
    grids = {base : grid.Grid()}

    q = queue.Queue()
    q.put(base)

    while not q.empty():
        (state, mode) = q.get()
        if mode == link.LETTER: # need to add a word
            all_letter_nodes = [u for u,data in g.nodes(data=True) if data['bipartite'] == link.LETTER]
            used_words = used_nodes[state]
            current_grid = grids[state]
            iter_order = []

            if len(all_letter_nodes) == 0: # add a random word
                iter_order = random.sample(set(words), 1)
                current_grid.add_word(iter_order[0], 0, 0, grid.EAST)

            for word in iter_order:
                next_state = state.copy()
                next_state.add_node(word)
                new_grid = current_grid.copy()
                new_grid.add_word(word, 0, 0, grid.EAST)
                grids[next_state] = new_grid
                new_used_words = used_words.copy()
                new_used_words.add(word)
                used_nodes[next_state] = new_used_words
                
            
            
        elif mode == link.WORD: # need to add a letter
            if len(progress_list) == 0: # randomly add a node
                iter_order = random.sample(set(words), 1)
                plane.add_word(iter_order[0], 0, 0, grid.EAST)
            else:
                iter_order = random.shuffle(progress_list)
            print(iter_order)
            for node in iter_order:
                print(g.adj[node])
                for v, keys in g.adj[node].items():
                    for k in keys:
                        new_state = state.copy()
                        new_state.add_edge(node, v, k)
                        q.put(new_state)
        break

if __name__ == "__main__":
    walk_test()
