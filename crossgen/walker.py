import networkx as nx
import queue
import random
import sys
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

def flip_mode(mode):
    if mode == link.LETTER:
        return link.WORD
    elif mode == link.WORD:
        return link.LETTER
    else:
        raise ValueError(f"unknown mode {mode}")

class CrosswordTreeSearch:
    """class to try misc. word combinations to try and find valid crosswords

    Attributes:
        all_words = list of words in the crossword
        master_link_graph =  link graph containing all possible edges and nodes (see also link.generate_link_graph
        search_tree = the search tree
            node = (current link graph state, LETTER or WORD)
            edge = the edge that was added to the link graph, or the node, if it's a new isolated node
                move = the node or edge that was added
        root = the root search tree node link graph state; i.e. an empty graph
        grids = map from link graph state to the corresponding Grid
        stack = working queue of places to search from next
            entries are in the form (link graph state, LETTER or WORD)
        visited = dict where visited.get(link state, False) = True if already visited and False otherwise
        node_count = number of nodes visited so far
    """
    def __init__(self, all_words):
        self.all_words = all_words

        self.master_link_graph = link.generate_link_graph(all_words)

        self.search_tree = nx.DiGraph()
        self.root = nx.MultiGraph()
        self.search_tree.add_node((self.root, link.LETTER))
        
        self.grids = {self.root : grid.Grid()}

        self.visited = {}

        self.stack = []
        self.stack.append((self.root, link.LETTER))

        self.node_count = 0
    
    def print_pv(self, state, mode):
        labels = []
        node = (state, mode)
        parents = list(self.search_tree.predecessors(node))
        while len(parents) > 0:
            parent = parents[0]
            label = self.search_tree.edges[(parent, node)]["move"]
            labels.append(str(label))
            node = parent
            parents = list(self.search_tree.predecessors(node))
        sequence = " -> ".join(reversed(labels))
        print(sequence, file=sys.stderr)

    def walk_test(self):
        while len(self.stack) > 0:
            (state, mode) = self.stack.pop()
            self.print_pv(state, mode)
            used_letters = [u for u,data in state.nodes(data=True) if data['bipartite'] == link.LETTER]
            used_words = [u for u,data in state.nodes(data=True) if data['bipartite'] == link.WORD]

            if mode == link.LETTER: # need to add a word
                next_from_letters = self.next_from_letters(state, used_words, used_letters)
                if len(next_from_letters) == 0:
                    for word in self.next_root_words(state, used_words, used_letters):
                        self.read_word(state, word)
                else:
                    for edge in next_from_letters:
                        self.read_letter_to_word(state, edge)
            elif mode == link.WORD: # need to add a letter
                if len(used_words) == len(self.all_words):
                    print("DONE", file=sys.stderr)
                    print(str(self.grids[state]), file=sys.stderr)
                    continue
                next_from_words = self.next_from_words(state, used_words, used_letters)
                for edge in next_from_words:
                    self.read_word_to_letter(state, edge)
            self.visited[state] = True

    def next_root_words(self, state, used_words, used_letters):
        """Return list of word nodes to esearch next"""
        unused_words = set(self.all_words) - set(used_words)
        return random.sample(unused_words, len(unused_words))

    def next_from_letters(self, state, used_words, used_letters):
        """Return list of (letter, word, key) edges to search next"""
        next_list = []

        for letter in random.sample(used_letters, len(used_letters)):
            edge_count = sum(len(atlas) for atlas in state.adj[letter].values())
            if edge_count % 2 == 0: # only letters with an odd number of edges will be able to have a word added
                continue
            for word, atlas in self.master_link_graph.adj[letter].items():
                if word not in used_words:
                    for key in atlas: # for each edge between letter and word
                        proposed_edge = (letter, word, key)
                        if proposed_edge not in state.edges:
                            next_list.append(proposed_edge)
        return next_list

    def next_from_words(self, state, used_words, used_letters):
        """Return list of (word, letter, key) edges to search next"""
        next_list = []
        for word in random.sample(used_words, len(used_words)):
            for letter, atlas in self.master_link_graph.adj[word].items():
                for key in atlas: # for each edge between word and letter
                        proposed_edge = (word, letter, key)
                        if proposed_edge not in state.edges:
                            next_list.append(proposed_edge)
        return next_list

    def read_word(self, state, word):
        """If legal on grid, add an orphan node to the current search tree and push onto stack for further reading
        
        Update index:
        - grids[new_state] = new_grid
        - stack += (new_state, new_mode)
        - search_tree += edge((state, mode), (new_state, new_mode), move=word)
        """
        mode = link.LETTER
        new_mode = flip_mode(mode)
        new_state = state.copy()        
        new_state.add_node(word, **self.master_link_graph.nodes[word])
        if self.visited.get(new_state, False) == False:
            current_grid = self.grids[state]
            new_grid = current_grid.copy()
            if new_grid.can_add_word(word, 0, 0, grid.EAST): # by default, add word horizontally at origin
                new_grid.add_word(word, 0, 0, grid.EAST)
                self.grids[new_state] = new_grid
                self.stack.append((new_state, new_mode))
                self.search_tree.add_edge((state, mode), (new_state, new_mode), move=word)

    def read_word_to_letter(self, state, edge):
        """ Add (word, letter, key) edge to search tree and push onto stack for further reading

        Update index:
        - grids[new_state] = grids[state]
        - stack += (new_state, new_mode)
        - search_tree += edge((state, mode), (new_state, new_mode), move=edge)
        """
        mode = link.WORD
        new_mode = flip_mode(mode)
        new_state = state.copy()
        new_state.add_node(edge[1], **self.master_link_graph.nodes[edge[1]])
        new_state.add_edge(*edge, **self.master_link_graph.edges[edge])
        if self.visited.get(new_state, False) == False:
            self.stack.append((new_state, new_mode))
            self.search_tree.add_edge((state, mode), (new_state, new_mode), move=edge)
            self.grids[new_state] = self.grids[state] # no change yet

    def read_letter_to_word(self, state, edge):
        """Edge is an edge from a letter to a word
        
        Update index:
        - grids[new_state] = new_grid
        - stack += (new_state, new_mode)
        - search_tree += edge((state, mode), (new_state, new_mode), move=edge)
        """
        mode = link.LETTER
        new_mode = flip_mode(mode)
        letter = edge[0]
        child_word = edge[1]
        key = edge[2]
        child_letter_index = self.master_link_graph.edges[edge]["index"]
        parent_word_candidates = state.adj[letter].items()
        current_grid = self.grids[state]
        for parent_word, atlas in parent_word_candidates:
            for key, attrs in atlas.items():
                parent_edge = (parent_word, letter, key)
                parent_letter_index = attrs["index"]
                print(f"can join: {parent_word}-{parent_letter_index}, {child_word}-{child_letter_index}?", file=sys.stderr)
                if current_grid.can_join_word(parent_word, parent_letter_index, child_word, child_letter_index):
                    print("  yes", file=sys.stderr)
                    new_grid = current_grid.copy()
                    current_grid.join_word(parent_word, parent_letter_index, child_word, child_letter_index)
                    new_state = state.copy()
                    new_state.add_node(child_word, **self.master_link_graph.nodes[child_word])
                    new_state.add_edge(*edge, **self.master_link_graph.edges[edge])
                    self.grids[new_state] = new_grid
                    self.stack.append((new_state, new_mode))
                    self.search_tree.add_edge((state, mode), (new_state, new_mode), move=edge)
    
def walk_test():
    words = ['reimu', 'marisa', 'sanae']
    g = link.generate_link_graph(words)
    
    search_tree = CrosswordTreeSearch(words)
    search_tree.walk_test()

if __name__ == "__main__":
    walk_test()
