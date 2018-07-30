import sys
import argparse

from crosschan import command

def main(args): # TODO: don't need this anymore, remove it
	parser = argparse.ArgumentParser(prog="crosschan", description="derp crosswords")
	parser.add_argument('path', metavar='path', type=str, nargs='?', default='-',
	               help='location of file contain newline-separated list of words')
	parser.add_argument('-c', '--encoding', default='utf8', type=str, nargs='?',
	               help='encoding of file (default is utf8)')
	args = parser.parse_args(args)
	print("hi")
	path = args.path
	encoding = args.encoding
	fin = sys.stdin
	if path != "-":
		try:
			fin = open(path, "r", encoding=encoding)
		except IOError as e:
			print(e)
			return
		except LookupError as e:
			print(e)
			return
	words = []
	for word in fin:
		words.append(word)
	print(words)
	fin.close()

if __name__ == "__main__":
	command.main(sys.argv)
