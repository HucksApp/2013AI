#!/usr/bin/env python
# encoding: utf-8

from game import Game


def parse_cmdline_args():
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Run the Bomberman game')
    parser.add_argument('-n', '--num-players', dest='num_players', metavar='N',
            choices=[1, 2, 3, 4], default=2, type=int,
            help='How many players')
    parser.add_argument('-m', '--map', dest='map_name', metavar='MAP',
            choices=['pirate', 'village'], default='village',
            help='Specify the map file')
    return parser.parse_args()


def main(args):
    bomberman_game = Game(
            n_players=args.num_players,
            map_name=args.map_name)
    bomberman_game.run_game()


def setup_signal_handlers():

    # A SIGINT handler that exits the program after pressing ^C three times
    def sigint_handler(sig, frm):
        sigint_handler.counter += 1
        if sigint_handler.counter >= 2:
            print 'Force exiting the program...'
            raise SystemExit
    sigint_handler.counter = 0

    # Register the signal handler
    from signal import signal, SIGINT
    signal(SIGINT, sigint_handler)


if __name__ == '__main__':
    setup_signal_handlers()
    args = parse_cmdline_args()
    main(args)

