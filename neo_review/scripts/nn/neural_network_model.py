import chainer
import chainer.functions as F
import chainer.links as L
from chainer import training, Chain
from chainer.training import extensions

from set_condition import SetCondition
from load_data import LoadData
from utility import Utility


class NeuralNetworkModel(Chain):
    def __init__(self, n_l0=100, n_l1=100, n_l2=100, n_out=1, *args, **kwargs):
        self.n_out = n_out

        super().__init__(*args, **kwargs)

        with self.init_scope():
            self.l0 = L.Linear(None, n_l0)
            self.l1 = L.Linear(None, n_l1)
            self.l2 = L.Linear(None, n_l2)
            self.ll = L.Linear(None, n_out)

            self.b0 = L.BatchNormalization(n_l0)
            self.b1 = L.BatchNormalization(n_l1)
            self.b2 = L.BatchNormalization(n_l2)

    def __call__(self, x, y):
        y = y.reshape(-1, self.n_out)
        loss = F.mean_squared_error(self.forward(x), y)
        chainer.reporter.report({'loss': loss}, self)
        return loss

    def forward(self, x):
        h0 = F.relu(self.l0(x))
        h0 = self.b0(h0)

        h1 = F.relu(self.l1(h0))
        h1 = self.b1(h1)

        h2 = F.relu(self.l2(h1))
        h2 = self.b2(h2)

        hl = self.ll(h2)
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

        for year in range(1978, 2020):
            train, test, _ = load_data.map[year]

            train_iter = chainer.iterators.SerialIterator(train,
                                                          args.batchsize)

            test_iter = chainer.iterators.SerialIterator(test,
                                                         args.batchsize,
                                                         repeat=False,
                                                         shuffle=False)

            # Set up a trainer
            updater = training.updaters.StandardUpdater(train_iter, optimizer)
            trainer = training.Trainer(updater, (args.epoch, 'epoch'))

            # Evaluate the model with the test dataset for each epoch
            trainer.extend(extensions.Evaluator(test_iter, self))

            # Write a log of evaluation statistics for each epoch
            trainer.extend(extensions.LogReport(trigger=(args.logtrigger,
                                                         "epoch")))
            trainer.extend(extensions.PrintReport(['epoch',
                                                   'main/loss',
                                                   'validation/main/loss',
                                                   'elapsed_time']))

            # Print a progress bar to stdout
            trainer.extend(extensions.ProgressBar())

            # Run the training
            trainer.run()

            # Save the model
            model_name = 'models/model_' + str(year)
            chainer.serializers.save_npz(model_name, self)


if __name__ == '__main__':
    model = NeuralNetworkModel()
    model.run_as_script()
