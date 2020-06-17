# crossgen

Uses Python 3 to generate crosswords.

Includes a GUI implemented with PyQt5, and also a command line version.

If you just want to try it out without actually pip installing this package, you can manually
pip install the dependencies listed in setup.py, and then directly run one of the following commands:

- For the command line tool:

  `python -m crossgen`

- For the GUI:

  `python -m crossgen.gui`

To actually install this package (which also automatically installs the dependencies):

- From GitHub:

  `python -m pip install git+https://github.com/ahiijny/crossgen.git`

- Or, if you have the repo already cloned:

  `python -m pip install .`

After installing, you should also be able to run the following scripts from your PATH:

- For the command line tool:
  
  `crossgenc`

- For the GUI:

  `crossgen`
