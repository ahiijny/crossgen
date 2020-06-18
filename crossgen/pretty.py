"""For pretty-formatting grids and tables etc."""

import html
import sys

from crossgen import grid

style = """
    table, th, td {
        border-collapse: collapse;
        table-layout: fixed;
    }
    td {
        border: 1px solid black;
        width: 1.3em;
        height: 1.3em;
        text-align: center;
    }
    td.empty {
        border: 0;
    }
    body {
        font-family: Sans-Serif;
    }
"""

example_html = """
<!DOCTYPE html>
<head>
<style>
    {style}
</style>
</head>
<body>
<h2>Testing Testing</h2>
<table>
  <tr>
    <td class="empty"> </td>
    <td class="empty"> </td>
    <td class="empty"> </td>
    <td class="empty"> </td>
    <td class="empty"> </td>
    <td class="empty"> </td>
    <td class="empty"> </td>
    <td class="empty"> </td>
    <td class="empty"> </td>
    <td class="empty"> </td>
    <td><sup>5</sup>M</td>
    <td class="empty"> </td>
    <td class="empty"> </td>
    <td class="empty"> </td>
    <td class="empty"> </td>
    <td class="empty"> </td>
    <td class="empty"> </td>
    <td class="empty"> </td>
    <td class="empty"> </td>
  </tr>
  <tr>
    <td class="empty"> </td>
    <td class="empty"> </td>
    <td class="empty"> </td>
    <td class="empty"> </td>
    <td><sup>8</sup>M</td>
    <td>O</td>
    <td>N</td>
    <td>T</td>
    <td>A</td>
    <td>N</td>
    <td>A</td>
    <td class="empty"> </td>
    <td class="empty"> </td>
    <td class="empty"> </td>
    <td class="empty"> </td>
    <td class="empty"> </td>
    <td class="empty"> </td>
    <td class="empty"> </td>
    <td class="empty"> </td>
  </tr>
  <tr>
    <td class="empty"> </td>
    <td class="empty"> </td>
    <td class="empty"> </td>
    <td class="empty"> </td>
    <td class="empty"> </td>
    <td class="empty"> </td>
    <td class="empty"> </td>
    <td class="empty"> </td>
    <td class="empty"> </td>
    <td class="empty"> </td>
    <td>R</td>
    <td class="empty"> </td>
    <td class="empty"> </td>
    <td class="empty"> </td>
    <td class="empty"> </td>
    <td class="empty"> </td>
    <td class="empty"> </td>
    <td class="empty"> </td>
    <td class="empty"> </td>
  </tr>
</table>
</body>
</html>""".format(style=style)

class HtmlGridPrinter:
    
    def __init__(self, outstream=sys.stdout):
        self.out = outstream
        global style
        self.style = style

    def print_crosswords(self, crosswords):
        """`crosswords` should be a list of (score, crossword_grid) tuples"""
        self.print_header()

        for i, (score, crossword) in enumerate(crosswords):            
            self.print_crossword(crossword, title_string=f"Crossword {i+1}, score:{score:.2f}")

        self.print_footer()

    def print_header(self):
        out = self.out

        print("<!DOCTYPE html>", file=out)
        print("<html>", file=out)
        print("<head>", file=out)
        print("<style>", file=out)
        print(self.style, file=out)
        print("</style>", file=out)
        print("</head>", file=out)
        print("<body>", file=out)

    def print_crossword(self, crossword, title_string):
        out = self.out

        letters = str(crossword)
        numbers_map = crossword.get_grid_numbers()

        print(f"<h2>{title_string}</h2>", file=out)

        print("<table>", file=out)
        for y, row in enumerate(letters.split("\n")):
            print("  <tr>", file=out)
            for x, letter in enumerate(row):
                label = ""
                if (x, y) in numbers_map:
                    label = f"<sup>{numbers_map[(x,y)]}</sup>"
                style = ""
                if letter == " ":
                    style = ' class="empty"'
                print(f'    <td{style}>{label}{letter}</td>', file=out)
            print("  </tr>", file=out)

        print("</table>", file=out)

    def print_footer(self):
        out = self.out

        print("</body>", file=out)
        print("</html>", file=out)
  
def be_judgmental(crossword_grid):
    """return a number that scores how good the grid is based on various metrics
    
    higher = better"""
    (width, height) = crossword_grid.get_size()
    cross_count = crossword_grid.get_cross_count()
    cw_numbers = crossword_grid.get_grid_numbers()

    score_intersections = cross_count # more intersections is better
    score_too_tall = min(-(height / width) + 1, 0) # penalize crosswords that are too tall
    score_too_wide = min(-(width / height) + 1, 0) # penalize crosswords that are too wide
    score_too_big = -(width * height) # penalize crosswords that are too large
    score_more_horizontals = 0
    for attrs in crossword_grid.words.values():
        if attrs["orientation"] == grid.EAST:
            score_more_horizontals += 1
        else:
            score_more_horizontals -= 1
    score_one_is_horizontal = 0 # looks nicer if 1 is horizontal
    score_one_is_near_the_top = 0 # looks nicer if 1 is near the top
    for attrs in crossword_grid.words.values():
        true_coords = attrs["coords"]
        grid_coords = (true_coords[0] - crossword_grid.xmin, true_coords[1] - crossword_grid.ymin)
        if cw_numbers[grid_coords] == 1:
            if attrs["orientation"] == grid.EAST:
                score_one_is_horizontal = 1
            score_one_is_near_the_top = -grid_coords[1]
            break


    # totally arbitrary score weightings
    score = 10 * score_intersections \
        + 30 * score_one_is_horizontal \
        + 15 * score_one_is_near_the_top \
        + 5 * score_more_horizontals \
        + 10 * score_too_tall \
        + 0.5 * score_too_wide \
        + 0.05 * score_too_big

    return score

def test_html():
    g = grid.Grid()
    g.add_word("REIMU", 0, 0, grid.EAST)
    g.add_word("MARISA", 3, 0, grid.SOUTH)
    g.add_word("SANAE", 2, 5, grid.EAST)

    printer = HtmlGridPrinter()
    printer.print_header()
    printer.print_crossword(g, "lol jk")
    printer.print_footer()

if __name__ == "__main__":
    test_html()