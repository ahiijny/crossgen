import sys

from crossgen import command
from crossgen import gui

def main():
	cmd = command.main()
	exit_code = cmd.run(sys.argv)
	return exit_code

if __name__ == "__main__":
	sys.exit(main())
