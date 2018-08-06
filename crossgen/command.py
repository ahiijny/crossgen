import logging
import argparse
import sys

def main(argv):
    parser = argparse.ArgumentParser(description="Crosswords",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("command", help="subcommand to run")
    subparsers = parser.add_subparsers(metavar="", dest="command")
    _add_subparsers(subparsers)

    logging.basicConfig(level=logging.INFO)
    logging.debug('Started')

    args = parser.parse_args(argv)
    exit_code = 0
    if hasattr(args, "func"):
        exit_code = args.func(args)
    else:
        parser.print_help()
    
    logging.debug('Finished')
    sys.exit(exit_code)

command_names = [
    "test",
    "create"
]

def _add_subparsers(subparsers):
    """Add a subparser for each command in command_names.

    Assumes that the parser function is `def _{command_name}_parser(subparsers):`"""

    for command_name in command_names:
        command = globals()[command_name]
        subparser = subparsers.add_parser(command_name, help=command.__doc__)
        subparser.set_defaults(func=command)
        build_parser = globals().get("_" + command_name + "_parser", None)
        assert build_parser is not None
        build_parser(subparser)

def _test_parser(subparser):
    subparser.add_argument("--option", metavar="VALUE", default="123456", help="description")

def test(args):
    """This doesn't do anything"""
    print(args)

def _create_parser(subparser):
    subparser.add_argument("-i", "--from_file", metavar="PATH", default="-", help="file from which to read newline-separated words (use '-' to indicate stdin)")

def create(args):
    """Read in words from stdout, terminated with an empty newline, and then generate crosswords"""

    from crossgen import walker

    words = []
    infile = sys.stdin
    inpath = args.from_file
    if inpath != "-":
        try:
            infile = open(inpath, "r")
        except IOError:
            print(f"could not open file {infile}")
            return 1

    for word in infile:
        word = word.strip()
        if len(word) == 0:
            break
        words.append(word)

    for crossword in walker.generate_crosswords(words):
        print(crossword)