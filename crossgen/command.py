import logging
import argparse
import sys

class main:
    command_names = [
        "test",
        "create",
        "create-derp",
    ]

    def run(self, argv):
        parser = argparse.ArgumentParser(description="Crosswords",
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        parser.add_argument("command", help="subcommand to run")
        subparsers = parser.add_subparsers(metavar="", dest="command")
        self.add_subparsers(subparsers)

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

    def add_subparsers(self, subparsers):
        """Add a subparser for each command in command_names.

        Assumes that the command objects follow the given interface:
        
        class cmd:
            + build_parser(self, subparser):
                adds the appropriate command line options to the given argparser
            + run(self, args): exit_code
                runs the command, given the argparse.Namespace args object
                can return exit code or not return anything at all (which is the same as returning 0)
        """
        for command_name in main.command_names:
            command = globals()[command_name.replace("-", "_")]()
            description = command.run.__doc__
            help = description.split("\n", 1)[0]
            subparser = subparsers.add_parser(command_name, description=description, help=help)
            subparser.set_defaults(func=command.run)
            command.build_parser(subparser)

class test:
    def build_parser(self, subparser):
        subparser.add_argument("--option", metavar="VALUE", default="123456", help="description")

    def run(self, args):
        """This doesn't do anything"""
        print(args)

class create:
    def build_parser(self, subparser):
        subparser.add_argument("-i", "--from-file", metavar="PATH", default="-", help="file from which to read newline-separated words (use '-' to indicate stdin)")

    def run(self, args):
        """Read in words from stdout, terminated with an empty newline, and then generate crosswords.
        
        Output is in plain text format."""

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

        try:
            for crossword in walker.generate_crosswords(words):
                print(crossword)
        except KeyboardInterrupt: # graceful Ctrl + C
            return 0

class create_derp:
    def build_parser(self, subparser):
        pass

    def run(self, args):
        """Derp"""
        from crossgen import walker

        for crossword in walker.generate_crosswords_derp():
            print(crossword)
