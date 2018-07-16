import logging
import argparse

def main(argv):
    parser = argparse.ArgumentParser(description="Crosswords",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("command", help="subcommand to run")
    subparsers = parser.add_subparsers(metavar="", dest="command")
    _add_subparsers(subparsers)

    logging.basicConfig(level=logging.INFO)
    logging.debug('Started')

    args = parser.parse_args(argv)
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
    
    logging.debug('Finished')

command_names = [
    "test"
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
     print(args)
