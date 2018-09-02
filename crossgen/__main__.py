import sys

from crossgen import command

if __name__ == "__main__":
	main = command.main()
	exit_code = main.run(sys.argv)
	sys.exit(exit_code)
