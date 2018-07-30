"""Module for handling the actual crossword grid.

Used to check spatial constraints etc."""

HORIZONTAL = 0
VERTICAL = 1

class Grid:
    """Using screen coordinates"""
    def __init__(self):
        self.index = {}
        """sparse matrix such that index[(x,y)] = letter"""

    def hasChar(self, x, y):
        return (x, y) in self.index

    def place(self, word, x, y, orientation):
        """overwrite existing, if any"""
        dx = 0
        dy = 0 
        if orientation is HORIZONTAL:
            dx = 1
        elif orientation is VERTICAL:
            dy = 1

        for ch in word:
            self.index[(x,y)] = ch
            x = x + dx
            y = y + dy

    def recalc_bounds(self):
        self.xmin = 0
        self.xmax = 0
        self.ymin = 0
        self.ymax = 0
        for coords in self.index:
            self.xmin = min(self.xmin, coords[0])
            self.xmax = max(self.xmax, coords[0])
            self.ymin = min(self.ymin, coords[1])
            self.ymax = max(self.ymax, coords[1])

    def __str__(self):
        self.recalc_bounds()
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

def main():
    grid = Grid()
    grid.place("television", 0, 0, HORIZONTAL)
    grid.place("ship", 5, -2, VERTICAL)
    print(grid)

if __name__ == "__main__":
    main()
