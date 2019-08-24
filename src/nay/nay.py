import argparse
import json
from .prize import Prize


def main():
    """Entry point for the application script"""
    parser = argparse.ArgumentParser(description="nay")

    parser.add_argument('subcommand',
                        help='[fetch]',
                        type=str)

    args = parser.parse_args()

    if args.subcommand == 'fetch':
        prize = Prize()
        ds = prize.data_set()
        print(json.dumps(ds, indent=4, ensure_ascii=False))
