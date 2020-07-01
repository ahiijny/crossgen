# crossgen

Uses Python 3 to generate crosswords. Crosswords are generated randomly, so they may be different every time!

There's a score metric to sort the nicer-looking generated ones to the top (for some definition of "nice"),
but the weightings are pretty arbitrary, so it doesn't matter too much :P

Includes a GUI implemented with PyQt5, and also a command line version.

If you just want to try it out without actually pip installing this package, you can manually
pip install the dependencies listed in setup.py, and then directly run one of the following commands:

- For the command line tool:

  `python -m crossgen`

- For the GUI:

  `python -m crossgen.gui`

To actually install this package (which also automatically installs the dependencies):

- From GitHub:

  `python -m pip install https://github.com/ahiijny/crossgen/archive/master.zip`

- Or, if you have the repo already cloned:

  `python -m pip install .`

After installing, you should also be able to run the following scripts from your PATH:

- For the command line tool:
  
  `crossgenc`

- For the GUI:

  `crossgen`

## Screenshot

![screenshot of the GUI with one generated crossword](/doc/screenshot.png?raw=true)