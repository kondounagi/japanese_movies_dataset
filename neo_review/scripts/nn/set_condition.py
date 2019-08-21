import argparse


class SetCondition:
    def __init__(self):
        parser = argparse.ArgumentParser(
            description=('The parameter of PW model (traffic sound speed and '
                         'relaxation parameter) estimation from the results '
                         'of macro traffic simulation.'))

        parser.add_argument('--batchsize', '-b',
                            type=int,
                            default=100,
                            help='Number of data in each mini-batch')

        parser.add_argument('--epoch', '-e',
                            type=int,
                            default=100,
                            help='Number of sweeps over the dataset to train')

        parser.add_argument('--logtrigger', '-t',
                            type=int,
                            default=100,
                            help='Frequency of logging')

        parser.add_argument('--noplot',
                            dest='plot',
                            action='store_false',
                            help='Disable PlotReport extension')

        self.args = parser.parse_args()
