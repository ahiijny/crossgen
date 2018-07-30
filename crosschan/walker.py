from crosschan import grid

def generate_crosswords(words):
    """words is a sequence of words"""

    crosswords = []
    cw = grid.Grid()
    cw.place("lapis", 0, 0, grid.HORIZONTAL)
    cw.place("peridot", 2, 0, grid.VERTICAL)
    crosswords.append(cw)
    for crossword in crosswords:
        yield crossword
    