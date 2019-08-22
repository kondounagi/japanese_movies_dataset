import numpy as np
import matplotlib.pyplot as plt
import chainer
from sklearn import metrics
from sklearn.metrics import confusion_matrix

from neural_network_model import NeuralNetworkModel
from load_data import LoadData


class Predict:
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        pass

    def show_results(self, model, test, titles):
        npax = np.array([t['x'] for t in test], dtype=np.float32)
        npay = np.array([t['y'] for t in test], dtype=np.float32)

        with chainer.using_config('train', False):
            next_layer = model.forward(npax)

        for i, result in enumerate(next_layer):
            label = ""
            if npay[i] == 1:
                label = "*"
            print(label, titles[i], result.data[0])

        return npay, next_layer.data

    def run_as_script(self):
        model = NeuralNetworkModel()

        print("### Test Result ###")

        load_data = LoadData()
        y_true, y_score = [], []

        for year in range(1978, 2020):
            _, test, title = load_data.map[year]
            model_name = 'models/model_' + str(year)
            chainer.serializers.load_npz(model_name, model)
            ans, score = self.show_results(model, test, title)
            y_true.extend(ans)
            y_score.extend(score)

        fpr, tpr, thresholds = metrics.roc_curve(y_true, y_score)
        auc = metrics.auc(fpr, tpr)
        plt.plot(fpr, tpr, label='ROC curve (area = {}.2f)'.format(auc))

        print("confusion matrix:\n {}".format(confusion_matrix(y_true, [y > 0.5 for y in y_score])))
        print("auc: {}".format(auc))

        plt.legend()
        plt.title('ROC curve')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.grid(True)
        plt.savefig("figures/neural_network_default_params.png")


if __name__ == '__main__':
    predict = Predict()
    predict.run_as_script()
