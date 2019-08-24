import argparse

import chainer
import chainer.functions as F  # noqa: N812
import chainer.links as L  # noqa: N812
from chainer import training, Chain
from chainer.training import extensions

from optuna.pruners import SuccessiveHalvingPruner

from load_data import LoadData


def set_arg():
    parser = argparse.ArgumentParser(
        description=('Optuna example that optimizes '
                     'multi-layer perceptrons using Chainer.'),
    )

    parser.add_argument(
        '--epoch',
        '-e',
        type=int,
        default=1000,
        help='Number of sweeps over the dataset to train',
    )

    parser.add_argument(
        '--trial',
        '-t',
        type=int,
        default=100,
        help='Number of trials of hyper parameter optimization.',
    )

    return parser.parse_args()


# Network definition

class NeuralNetworkModel(Chain):
    def __init__(self, _trial):
        super(NeuralNetworkModel, self).__init__()
        n_layers = _trial.suggest_int('n_layers', 2, 20)

        self.layers = []
        for i in range(n_layers):
            n_units = int(_trial.suggest_int('n_units_l{}'.format(i), 4, 128))
            self.batchsize = _trial.suggest_int('batchsize', 16, 2048)
            self.layers.append(L.Linear(None, n_units))
            self.layers.append(F.relu)
            self.layers.append(L.BatchNormalization(n_units))
        self.layers.append(L.Linear(None, 1))

    def create_model(self, x):  # noqa: VNE001
        model = chainer.Sequential(*self.layers)
        with chainer.using_config('train', False):
            return model.forward(x)

    def __call__(self, x, y):  # noqa: VNE001
        y = y.reshape(-1, 1)  # noqa: VNE001
        loss = F.sigmoid_cross_entropy(self.create_model(x), y)
        chainer.reporter.report({'loss': loss}, self)
        return loss


def objective(_trial):
    # Model and optimizer
    model = NeuralNetworkModel(_trial=_trial)
    optimizer = chainer.optimizers.Adam()
    optimizer.setup(model)

    # Dataset
    load_data = LoadData()
    for year in range(1978, 2020):
        train, valid, test, _ = load_data.map[year]
        train_iter = chainer.iterators.SerialIterator(train,
                                                      model.batchsize)
        valid_iter = chainer.iterators.SerialIterator(valid,
                                                      model.batchsize,
                                                      repeat=False,
                                                      shuffle=False)

        # Trainer
        updater = training.updaters.StandardUpdater(train_iter, optimizer)
        trainer = training.Trainer(updater, (args.epoch, 'epoch'))
        trainer.extend(extensions.Evaluator(valid_iter, model))

        log_report_extension = (
            chainer.training.extensions.LogReport(log_name=None))

        trainer.extend(log_report_extension)

        integrator = (
            optuna.integration.ChainerPruningExtension(_trial,
                                                       "validation/main/loss",
                                                       (1, 'epoch')))

        trainer.extend(integrator)

        # Run!
        trainer.run()

        # Set the user attributes such as loss and accuracy for train and
        # validation sets
        log_last = log_report_extension.log[-1]
        for _key, _value in log_last.items():
            _trial.set_user_attr(_key, _value)

        # Return the mean square error
        mse = log_report_extension.log[-1]["validation/main/loss"]
        return mse


if __name__ == '__main__':
    import optuna

    args = set_arg()

    pruner = SuccessiveHalvingPruner(
        min_resource=100,
        reduction_factor=4,
        min_early_stopping_rate=0,
    )

    study = optuna.create_study(pruner=pruner)
    study.optimize(objective, n_trials=args.trial)

    # Summaryを出力
    print("[Trial summary]")
    df = study.trials_dataframe()
    state = optuna.structs.TrialState
    print("  Completed: ", len(df[df['state'] == state.COMPLETE]))
    print("  Pruned: ", len(df[df['state'] == state.PRUNED]))
    print("  Failed: ", len(df[df['state'] == state.FAIL]))

    print('Number of finished trials: ', len(study.trials))

    print('[Best trial]')
    trial = study.best_trial

    print('  Value: ', trial.value)

    print('  Params: ')
    for key, value in trial.params.items():
        print('    {}: {}'.format(key, value))

    print('  User attrs:')
    for key, value in trial.user_attrs.items():
        print('    {}: {}'.format(key, value))
