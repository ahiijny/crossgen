"""For pretty-formatting grids and tables etc."""

import html
import sys

from crossgen import grid

def print_html_grid(out, grid):
    """Print an HTML grid to the given output stream"""
    letters = str(grid)
    numbers_map = grid.get_grid_numbers()

    print("<!DOCTYPE html>", file=out)
    print("<html>", file=out)
    print("<head>", file=out)
    print("<style>", file=out)
    print("""
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
    """, file=out)
    print("</style>", file=out)
    print("</head>", file=out)
    print("<body>", file=out)
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
            print(f'    <td{style}>{label}{letter}</td>')
        print("  </tr>", file=out)

    print("</table>", file=out)
    print("</body>", file=out)
    print("</html>", file=out)


def test_html():
    g = grid.Grid()
    g.add_word("REIMU", 0, 0, grid.EAST)
    g.add_word("MARISA", 3, 0, grid.SOUTH)
    g.add_word("SANAE", 2, 5, grid.EAST)
    print_html_grid(sys.stdout, g)

if __name__ == "__main__":
    test_html()