"""Module for handling the actual crossword grid.

Used to check spatial constraints etc."""

import operator

EAST = (1, 0)
SOUTH = (0, 1)
WEST = (-1, 0)
NORTH = (0, -1)
"""Convenience direction constants"""

def add(v1, v2):
    """Add two tuples elementwise"""
    return tuple(a + b for a, b in zip(v1, v2))

def sub(v1, v2):
    """Subtract two tuples elementwise"""
    return tuple(a - b for a, b in zip(v1, v2))

def normal(v1):
    """Return the two perpendiculars"""
    if v1 == EAST:
        return (NORTH, SOUTH)
    elif v1 == SOUTH:
        return (EAST, WEST)
    elif v1 == WEST:
        return (SOUTH, NORTH)
    elif v1 == NORTH:
        return (WEST, EAST)
    else:
        raise ValueError(f"Unsupported input: {v1}")

class Grid:
    """Grid of words, using screen coordinates"""
    def __init__(self):
        self.index = {}
        """sparse matrix such that index[(x,y)] = letter"""

        self.counts = {}
        """sparse matrix such that counts[(x,y)] = number of overlaps at (x,y)"""

        self.words = {}
        """map from (word, key=0) to {"coords" : (x, y), "orientation" : <int>}"""

    def has_letter_at(self, pos):
        """Return True if there is a letter at self.index[pos], where pos = (x, y)"""
        return pos in self.index

    def add_letter(self, ch, pos):
        """Where pos = (x,y).
        
        Letters can stack, but only if they are the same letter.
        """
        if pos in self.index:
            if self.index[pos] != ch:
                raise ValueError(f"tried to put '{ch}' at {pos}, which already contains '{self.index[pos]}'")
            self.counts[pos] += 1
        else:
            self.index[pos] = ch
            self.counts[pos] = 1

    def remove_letter(self, pos):
        """Do nothing if nothing is there.
        
        pos = (x, y)
        """
        if pos in self.index:
            self.counts[pos] -= 1
            if self.counts[pos] == 0:
                del self.index[pos]

    def can_add_word(self, word, x, y, direction):
        """Boundary checks:

        - all cells in path must be either empty or match word
        - cannot touch any cells on either side unless crossing a path
        - cell before beginning must be empty
        - cell past end must be empty
        """

        pos = (x, y)
        normals = normal(direction)
        
        for i, ch in enumerate(word):
            # cell before beginning must be empty
            if i == 0:
                if self.has_letter_at(sub(pos, dir)):
                    return False

            # cell past end must be empty
            if i == len(word) - 1:
                if self.has_letter_at(add(pos, dir)):
                    return False

            # all cells in path must be either empty or match word
            if self.has_letter_at(pos):
                if self.index[pos] != ch:
                    return False

            # cannot touch any cells on either side unless crossing a path
            if not self.has_letter_at(pos):
                if self.has_letter_at(add(pos, normals[0])):
                    return False
                if self.has_letter_at(add(pos, normals[1])):
                    return False

            # increment
            pos = add(pos, direction)
        return True
        
    def add_word(self, word, x, y, direction, key=0):
        if (word, key) in self.words:
            raise ValueError(f"word '{word}' with key={key}' is already in grid'")

        pos = (x, y)

        for ch in word:
            self.add_letter(ch, pos)
            pos = add(pos, direction)

    def __str__(self):
        self._recalc_bounds()
        grid = []
        for y in range(self.ymin, self.ymax+1):
            grid.append([])
            for x in range(self.xmin, self.xmax+1):
                ch = self.index.get((x,y), " ")
                grid[-1].append(ch)
        lines = []
        for line in grid:
            lines.append(''.join(line))
        return '\n'.join(lines)
    
    def _recalc_bounds(self):
        self.xmin = 0
        self.xmax = 0
        self.ymin = 0
        self.ymax = 0
        for coords in self.index:
            self.xmin = min(self.xmin, coords[0])
            self.xmax = max(self.xmax, coords[0])
            self.ymin = min(self.ymin, coords[1])
            self.ymax = max(self.ymax, coords[1]) 

def main():
    grid = Grid()
    grid.add_word("television", 0, 0, EAST)
    grid.add_word("ship", 5, -2, SOUTH)
    print(grid)

if __name__ == "__main__":
    main()
