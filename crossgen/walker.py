import logging
import networkx as nx
import queue
import random
import sys
from crossgen import link
from crossgen import grid

def generate_crosswords(words, max=None):
    """words is a sequence of words"""

    outcount = 0
    searcher = CrosswordTreeSearch(words)
    for crossword in searcher.search():
        yield crossword
        outcount += 1
        if outcount == max:
            break

def generate_crosswords_example():
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
        master_link_graph =  link graph containing all possible edges and nodes (see also link.generate_link_graph)
        search_tree = the search tree
            node = (this_grid, this_link, mode)
                mode = LETTER if word needs to be added next, or WORD if letter needs to be added next
            edge = the edge that was added to the link graph, or the node, if it's a new isolated node
                move = the node or edge that was added
        root = the root search tree node link graph state; i.e. an empty graph
        stack = working queue of places to search from next
            entries are in the form (link graph state, LETTER or WORD)
        visited = dict where visited.get(link state, False) = True if already visited and False otherwise
        node_count = number of nodes visited so far
    """
    def __init__(self, all_words):
        self.all_words = all_words

        self.master_link_graph = link.generate_link_graph(all_words)

        self.search_tree = nx.DiGraph()
        self.root_grid = grid.Grid()
        self.root_link = nx.MultiGraph()
        self.search_tree.add_node((self.root_grid, self.root_link, link.LETTER))

        self.visited = {}

        self.stack = []
        self.stack.append((self.root_grid, self.root_link, link.LETTER))

        self.node_count = 0
    
    def print_pv(self, this_grid, this_link, mode):
        labels = []
        node = (this_grid, this_link, mode)
        parents = list(self.search_tree.predecessors(node))
        while len(parents) > 0:
            parent = parents[0]
            label = self.search_tree.edges[(parent, node)]["move"]
            labels.append(str(label))
            node = parent
            parents = list(self.search_tree.predecessors(node))
        sequence = " -> ".join(reversed(labels))
        logging.debug(sequence)

    def search(self):
        """Yields valid grid.Grids that it finds

        This is a brute-force search, so runtime is probably exponential wrt number of words.
        """
        while len(self.stack) > 0:
            (this_grid, this_link, mode) = self.stack.pop()
            self.print_pv(this_grid, this_link, mode)
            used_letters = [u for u,data in this_link.nodes(data=True) if data['bipartite'] == link.LETTER]
            used_words = [u for u,data in this_link.nodes(data=True) if data['bipartite'] == link.WORD]

            if mode == link.LETTER: # need to add a word
                next_from_letters = self.next_from_letters(this_grid, this_link, used_words, used_letters)
                if len(next_from_letters) == 0:
                    for word in self.next_root_words(this_grid, this_link, used_words, used_letters):
                        self.read_word(this_grid, this_link, word)
                else:
                    for edge in next_from_letters:
                        self.read_letter_to_word(this_grid, this_link, edge)
            elif mode == link.WORD: # need to add a letter
                if len(used_words) == len(self.all_words):
                    assert(len(this_grid.words) == len(self.all_words))
                    logging.debug(f"FINISHED GRID: \n{str(this_grid)}")
                    yield this_grid
                    continue
                next_from_words = self.next_from_words(this_grid, this_link, used_words, used_letters)
                for edge in next_from_words:
                    self.read_word_to_letter(this_grid, this_link, edge)
            self.visited[(this_grid, this_link)] = True

    def next_root_words(self, this_grid, this_link, used_words, used_letters):
        """Return list of word nodes to esearch next"""
        unused_words = set(self.all_words) - set(used_words)
        return random.sample(unused_words, len(unused_words))

    def next_from_letters(self, this_grid, this_link, used_words, used_letters):
        """Return list of (letter, word, key) edges to search next"""
        next_list = []

        for letter in random.sample(used_letters, len(used_letters)):
            edge_count = sum(len(atlas) for atlas in this_link.adj[letter].values())
            if edge_count % 2 == 0: # only letters with an odd number of edges will be able to have a word added
                continue
            for word, atlas in self.master_link_graph.adj[letter].items():
                if word not in used_words:
                    for key in atlas: # for each edge between letter and word
                        proposed_edge = (letter, word, key)
                        if proposed_edge not in this_link.edges:
                            next_list.append(proposed_edge)
        return next_list

    def next_from_words(self, this_grid, this_link, used_words, used_letters):
        """Return list of (word, letter, key) edges to search next"""
        next_list = []
        for word in random.sample(used_words, len(used_words)):
            for letter, atlas in self.master_link_graph.adj[word].items():
                for key in atlas: # for each edge between word and letter
                        proposed_edge = (word, letter, key)
                        if proposed_edge not in this_link.edges:
                            next_list.append(proposed_edge)
        return next_list

    def read_word(self, this_grid, this_link, word):
        """If legal on grid, add an orphan node to the current search tree and push onto stack for further reading
        
        Update index:
        - stack += (new_grid, new_link, new_mode)
        - search_tree += edge((this_grid, this_link, mode), (new_grid, new_link, new_mode), move=word)
        """
        mode = link.LETTER
        new_mode = flip_mode(mode)
        new_link = this_link.copy()        
        new_link.add_node(word, **self.master_link_graph.nodes[word])
        new_grid = this_grid.copy()
        if new_grid.can_add_word(word, 0, 0, grid.EAST): # by default, add word horizontally at origin
            new_grid.add_word(word, 0, 0, grid.EAST)
            if self.visited.get((new_grid, new_link), False) == False:
                self.stack.append((new_grid, new_link, new_mode))
                self.search_tree.add_edge((this_grid, this_link, mode), (new_grid, new_link, new_mode), move=word)

    def read_word_to_letter(self, this_grid, this_link, edge):
        """ Add (word, letter, key) edge to search tree and push onto stack for further reading

        Update index:
        - grids[new_state] = grids[state]
        - stack += (new_state, new_mode)
        - search_tree += edge((state, mode), (new_state, new_mode), move=edge)
        """
        mode = link.WORD
        new_mode = flip_mode(mode)
        new_link = this_link.copy()
        new_link.add_node(edge[1], **self.master_link_graph.nodes[edge[1]])
        new_link.add_edge(*edge, **self.master_link_graph.edges[edge])
        new_grid = this_grid.copy() # grid doesn't change yet
        if self.visited.get((new_grid, new_link), False) == False: 
            self.stack.append((new_grid, new_link, new_mode))
            self.search_tree.add_edge((this_grid, this_link, mode), (new_grid, new_link, new_mode), move=edge)

    def read_letter_to_word(self, this_grid, this_link, edge):
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
        parent_word_candidates = this_link.adj[letter].items()
        for parent_word, atlas in parent_word_candidates:
            for key, attrs in atlas.items():
                parent_edge = (parent_word, letter, key)
                parent_letter_index = attrs["index"]
                logging.debug(f"can join: {parent_word}-{parent_letter_index}, {child_word}-{child_letter_index}?")
                if this_grid.can_join_word(parent_word, parent_letter_index, child_word, child_letter_index):
                    logging.debug("  yes")
                    new_grid = this_grid.copy()
                    new_grid.join_word(parent_word, parent_letter_index, child_word, child_letter_index)
                    new_link = this_link.copy()
                    new_link.add_node(child_word, **self.master_link_graph.nodes[child_word])
                    new_link.add_edge(*edge, **self.master_link_graph.edges[edge])
                    self.stack.append((new_grid, new_link, new_mode))
                    self.search_tree.add_edge((this_grid, this_link, mode), (new_grid, new_link, new_mode), move=edge)
    
def walk_test():
    logging.basicConfig(level=logging.DEBUG)
    words = ['reimu', 'marisa', 'sanae']
    g = link.generate_link_graph(words)
    
    search_tree = CrosswordTreeSearch(words)
    search_tree.search()

if __name__ == "__main__":
    walk_test()
