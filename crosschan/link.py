"""Module for handling the word relation graph.

Defines which words are linked to which words."""

class Graph:
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
    graph = Graph(words)
    graph.link("words", "sound", "o")
    graph.link("sound", "never", "n")


if __name__ == "__main__":
    main()
