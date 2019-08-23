import chainer
import chainer.functions as F  # noqa: N812
import chainer.links as L  # noqa: N812
from chainer import training, Chain
from chainer.training import extensions

from set_condition import SetCondition
from load_data import LoadData
from utility import Utility


class NeuralNetworkModel(Chain):
    def __init__(
            self, n_l0=25, n_l1=122, n_l2=5, n_l3=71, n_l4=72, n_l5=123,
            n_l6=37, n_l7=85, n_l8=108, n_out=1):
        self._n_out = n_out

        super().__init__()

        with self.init_scope():
            self._l0 = L.Linear(None, n_l0)
            self._l1 = L.Linear(None, n_l1)
            self._l2 = L.Linear(None, n_l2)
            self._l3 = L.Linear(None, n_l3)
            self._l4 = L.Linear(None, n_l4)
            self._l5 = L.Linear(None, n_l5)
            self._ll = L.Linear(None, n_out)

            self._b0 = L.BatchNormalization(n_l0)
            self._b1 = L.BatchNormalization(n_l1)
            self._b2 = L.BatchNormalization(n_l2)
            self._b3 = L.BatchNormalization(n_l3)
            self._b4 = L.BatchNormalization(n_l4)
            self._b5 = L.BatchNormalization(n_l5)

    def __call__(self, x, y):  # noqa: VNE001
        y = y.reshape(-1, self._n_out)  # noqa: VNE001
        loss = F.sigmoid_cross_entropy(self.forward(x), y)
        chainer.reporter.report({'loss': loss}, self)
        return loss

    def forward(self, x):  # noqa: VNE001
        h0 = F.relu(self._l0(x))
        h0 = self._b0(h0)

        h1 = F.relu(self._l1(h0))
        h1 = self._b1(h1)

        h2 = F.relu(self._l2(h1))
        h2 = self._b2(h2)

        h3 = F.relu(self._l3(h2))
        h3 = self._b3(h3)

        h4 = F.relu(self._l4(h3))
        h4 = self._b4(h4)

        h5 = F.relu(self._l5(h4))
        h5 = self._b5(h5)

        hl = self._ll(h5)
        return hl

    def run_as_script(self):
        args = SetCondition().args

        Utility.set_random_seed()  # 乱数シード固定

        print('# Minibatch-size: {}'.format(args.batchsize))
        print('# epoch: {}'.format(args.epoch))
        print('')

        optimizer = chainer.optimizers.Adam()
        optimizer.setup(self)

        # Load the dataset
        load_data = LoadData()

        # noinspection PyShadowingNames
        def setup_trainer(train, valid):
            train_iter = chainer.iterators.SerialIterator(train,
                                                          args.batchsize)
            valid_iter = chainer.iterators.SerialIterator(valid,
                                                          args.batchsize,
                                                          repeat=False,
                                                          shuffle=False)

            updater = training.updaters.StandardUpdater(train_iter, optimizer)
            trainer = training.Trainer(updater, (args.epoch, 'epoch'))

            # Evaluate the model with the test dataset for each epoch
            trainer.extend(extensions.Evaluator(valid_iter, self))

            # Write a log of evaluation statistics for each epoch
            trainer.extend(extensions.LogReport(trigger=(args.logtrigger,
                                                         "epoch")))
            trainer.extend(extensions.PrintReport(['epoch',
                                                   'main/loss',
                                                   'validation/main/loss',
                                                   'elapsed_time']))

            # Print a progress bar to stdout
            trainer.extend(extensions.ProgressBar())

            return trainer

        for year in range(1978, 2020):
            print('year: ', year)
            train, valid, _, _ = load_data.map[year]

            trainer = setup_trainer(train, valid)
            trainer.run()

            # Save the model
            model_name = 'models/model_' + str(year)
            chainer.serializers.save_npz(model_name, self)


if __name__ == '__main__':
    model = NeuralNetworkModel()
    model.run_as_script()
