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

def select_initial_word(master_link_graph, all_words):
    """Return sequence of word choices to add to initial empty state"""
    return random.shuffle(all_words)

def next_to_words(search_tree, master_link_graph, link_state, used_words, used_letters, all_words):
    """Return sequence of to-word edges to try adding next"""
    if len(used_words) == 0:
        return random.shuffle(all_words)
    word_list = []
    for letter in used_letters:
        g.adj[letter]

def flip_mode(mode):
    if mode == link.LETTER:
        return link.WORD
    elif mode == link.WORD:
        return link.LETTER
    else:
        raise ValueError(f"unknown mode {mode}")

class CrosswordTreeSearch:
    """class to try misc. word combinations to try andfind valid crosswords

    Attributes:
        all_words = list of words in the crossword
        master_link_graph =  link graph containing all possible edges and nodes (see also link.generate_link_graph
        search_tree = the search tree
            node = (current link graph state, LETTER or WORD)
            edge = the edge that was added to the link graph, or the node, if it's a new isolated node
        root = the root search tree node link graph state; i.e. an empty graph
        grids = map from link graph state to the corresponding Grid
        stack = working queue of places to search from next
            entries are in the form (link graph state, LETTER or WORD)
    
    """
    def __init__(self, all_words):
        self.all_words = all_words

        self.master_link_graph = link.generate_link_graph(all_words)

        self.search_tree = nx.Graph()
        self.root = nx.MultiGraph()
        self.search_tree.add_node((self.root, link.LETTER))
        
        self.grids = {self.root : grid.Grid()}

        self.stack = []
        self.stack.append((self.root, link.LETTER))

    def walk_test(self):
        while len(self.stack) > 0:
            (state, mode) = self.stack.pop()
            used_letters = [u for u,data in state.nodes(data=True) if data['bipartite'] == link.LETTER]
            used_words = [u for u,data in state.nodes(data=True) if data['bipartite'] == link.WORD]
            if mode == link.LETTER: # need to add a word
                next_from_letters = self.next_from_letters(state, used_words, used_letters)
                if len(next_from_letters) == 0:
                    for word in self.next_root_words():
                        self.read_word(state, mode, word)
                else:
                    for edge in next_from_letters:
                        self.read_letter_to_word(state, mode, edge)
            elif mode == link.WORD:
                pass

    def read_word(self, state, mode, word):
        """Add an orphan node to the current search tree, and push onto stack for further search"""
       new_state = state.copy()
       new_mode = flip_mode(mode)
       new_state.add_node(word)
       self.stack.append((state, mode))
       self.search_tree.add_edge((state, mode), (new_state, new_mode), change=word)

    def read_letter_to_word(self, state, mode, edge)
        """Edge is an edge from a letter to a word"""
        pass
    

    def next_root_words(self, state, used_words, used_letters):
        return random.shuffle(set(self.all_words) - set(used_words))

    def next_from_letters(self, state, used_words, used_letters):


    
def walk_test():
    words = ['reimu', 'marisa', 'sanae']
    g = link.generate_link_graph(words)

    base = nx.MultiGraph()

    tree = nx.Graph()
    tree.add_node((base, link.LETTER))
    """search tree:
        node = (current link graph state, LETTER or WORD)
        edge = the edge that was added to the link graph
    """
    grids = {base : grid.Grid()}
    """map from link graph state to the corresponding Grid"""

    q = []
    q.append((base, link.LETTER))
    """stack of link graphs to continue searching from"""

    while len(q) > 0:
        (state, mode) = q.pop()
        if mode == link.LETTER: # need to add a word
            used_letters = [u for u,data in g.nodes(data=True) if data['bipartite'] == link.LETTER]
            used_words = [u for u,data in g.nodes(data=True) if data['bipartite'] == link.WORD]
            current_grid = grids[state]
            iter_order = []

            if len(used_words) == 0: # need to add a word
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
