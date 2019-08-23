import argparse


def main():
    """Entry point for the application script"""
    parser = argparse.ArgumentParser(description="nay")

    parser.add_argument('subcommand',
                        help='[fetch]',
                        type=str)

    args = parser.parse_args()

    if args.subcommand == 'fetch':
        print("TODO: fetch'em all!")
