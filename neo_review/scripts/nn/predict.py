import numpy as np
import chainer
import chainer.functions as F
from neural_network_model import NeuralNetworkModel
from load_data import LoadData


class Predict:
    def __init__(self):
        self.model_pass = 'model'

    def __call__(self, *args, **kwargs):
        pass

    def show_results(self, model, test, titles):
        x = np.array([t['x'] for t in test], dtype=np.float32)
        t = np.array([t['y'] for t in test], dtype=np.float32)
        with chainer.using_config('train', False):
            y = model.forward(x).data
        print('[loss] mean squared error : ', F.mean_squared_error(y, t.reshape(-1, 1)))
        for i, result in enumerate(y):
            print(titles[i], result[0])


def main():
    model = NeuralNetworkModel()
    predict = Predict()
    chainer.serializers.load_npz(predict.model_pass, model)

    print("### Test Result ###")
    load_data = LoadData()
    for year in range(1978, 2020):
        train, test, title = next(load_data.gen)
        predict.show_results(model, test, title)


if __name__ == '__main__':
    main()
