import sys

from crossgen import command

def main():
	cmd = command.main()
	exit_code = cmd.run(sys.argv)
	sys.exit(exit_code)

if __name__ == "__main__":
	main()
