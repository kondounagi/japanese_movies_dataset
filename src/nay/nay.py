import argparse
import json
from .prize import PrizeSet

__version__ = '0.0.4'


def main():
    """Entry point for the application script"""
    parser = argparse.ArgumentParser(prog='nay',
                                     description="nay")

    parser.add_argument('-V', '--version',
                        action='version',
                        version='%(prog)s v' + __version__)

    parser.add_argument('subcommand',
                        help='[fetch]',
                        type=str)

    args = parser.parse_args()

    if args.subcommand == 'fetch':
        ps = PrizeSet()
        ds = ps.data_set()
        print(json.dumps(list(ds), indent=4, ensure_ascii=False))
