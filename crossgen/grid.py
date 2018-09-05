"""Module for handling the actual crossword grid.

This is using screen coordinates (i.e. y values increase downwards)

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

def scale(v, s):
    """Multiply tuple elementwise by scalar"""
    return tuple(a * s for a in v)

def normal(v1):
    """Return a tuple containing the two perpendicular unit vectors
    
    Only supports axis-aligned unit vectors at the moment"""
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

def flip_orientation(orientation):
    if orientation == EAST:
        return SOUTH
    elif orientation == SOUTH:
        return EAST
    else:
        raise ValueError(f"unsupported orientation {orientation}")

class Grid:
    """Grid of words, using screen coordinates"""
    def __init__(self):
        self.index = {}
        """sparse matrix such that index[(x,y)] = letter"""

        self.counts = {}
        """sparse matrix such that counts[(x,y)] = number of occurrences at (x,y)"""

        self.words = {}
        """map from (word, key=0) to {"coords" : (x, y), "orientation" : <int>} object"""

    def copy(self):
        new_grid = Grid()
        new_grid.index = self.index.copy()
        new_grid.counts = self.counts.copy()
        new_grid.words = self.words.copy()
        return new_grid

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

    def can_join_word(self, parent_word, parent_index, child_word, child_index):
        """Return true if can join child_word at letter child_index to existing parent_word at parent_index"""
        if parent_word not in self.words:
            return False
        parent_coords = self.words[parent_word]["coords"]
        parent_orientation = self.words[parent_word]["orientation"]
        child_orientation = flip_orientation(parent_orientation)
        join_coords = add(parent_coords, scale(parent_orientation, parent_index))
        child_coords = sub(join_coords, scale(child_orientation, child_index))
        return self.can_add_word(child_word, child_coords[0], child_coords[1], child_orientation)

    def join_word(self, parent_word, parent_index, child_word, child_index):
        parent_coords = self.words[parent_word]["coords"]
        parent_orientation = self.words[parent_word]["orientation"]
        child_orientation = flip_orientation(parent_orientation)
        join_coords = add(parent_coords, scale(parent_orientation, parent_index))
        child_coords = sub(join_coords, scale(child_orientation, child_index))
        self.add_word(child_word, child_coords[0], child_coords[1], child_orientation)

    def can_add_word(self, word, x, y, direction):
        """Boundary checks:

        - all cells in path must be either empty or match letter in word
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
        self.words[(word, key)] = {"coords" : (x, y), "orientation" : direction}

        pos = (x, y)

        for ch in word:
            self.add_letter(ch, pos)
            pos = add(pos, direction)

    def get_cross_count(self):
        cross_count = 0
        for count in self.counts.values():
            cross_count += count - 1
        return cross_count

    def get_size(self):
        """return (width, height) of smallest grid that bounds words"""
        self._recalc_bounds()
        return (self.xmax - self.xmin, self.ymax - self.ymin)

    def get_grid_numbers(self):
        """Return a map from (grid_x, grid_y) to number, relative to printed grid"""
        self._recalc_bounds()
        word_starts = []
        for data in self.words.values():
            (x, y) = data["coords"]
            grid_coords = (x - self.xmin, y - self.ymin)
            word_starts.append(grid_coords)
        sorted(word_starts)
        word_numbers = {}
        for i, grid_coords in enumerate(word_starts):
            word_numbers[grid_coords] = i
        return word_numbers

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
