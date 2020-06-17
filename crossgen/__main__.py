import sys

from crossgen import command
from crossgen import gui

def console():
	cmd = command.main()
	exit_code = cmd.run(sys.argv)
	sys.exit(exit_code)

def gui():
	exit_code = gui.run(sys.argv)
	sys.exit(exit_code)

if __name__ == "__main__":
	console()
