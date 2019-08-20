# coding:utf-8

import json
import warnings
from os import path

import numpy
import six
from chainer import reporter
from chainer import serializer as serializer_module
from chainer.training import extension
from chainer.training import trigger as trigger_module

_available = None


def _try_import_matplotlib():
    global matplotlib, _available
    try:
        import matplotlib  # NOQA
        _available = True
    except (ImportError, TypeError):
        _available = False


def _check_available():
    if _available is None:
        _try_import_matplotlib()

    if not _available:
        warnings.warn('matplotlib is not installed on your environment, '
                      'so nothing will be plotted at this time. '
                      'Please install matplotlib to plot figures.\n\n'
                      '  $ pip install matplotlib\n')


class PlotReportLogScale(extension.Extension):

    def __init__(self, y_keys, x_key='iteration', trigger=(5, 'epoch'),
                 postprocess=None, file_name='plot.png', marker='x',
                 grid=True):

        _check_available()

        self._x_key = x_key
        if isinstance(y_keys, str):
            y_keys = (y_keys,)

        self._y_keys = y_keys
        self._trigger = trigger_module.get_trigger(trigger)
        self._file_name = file_name
        self._marker = marker
        self._grid = grid
        self._postprocess = postprocess
        self._init_summary()
        self._data = {k: [] for k in y_keys}

    @staticmethod
    def available():
        _check_available()
        return _available

    def __call__(self, trainer):
        if self.available():
            # Dynamically import pyplot to call matplotlib.use()
            # after importing chainer.training.extensions
            import matplotlib.pyplot as plt
        else:
            return

        keys = self._y_keys
        observation = trainer.observation
        summary = self._summary

        if keys is None:
            summary.add(observation)
        else:
            summary.add({k: observation[k] for k in keys if k in observation})

        if self._trigger(trainer):
            stats = self._summary.compute_mean()
            stats_cpu = {}
            for name, value in six.iteritems(stats):
                stats_cpu[name] = float(value)  # copy to CPU

            updater = trainer.updater
            stats_cpu['epoch'] = updater.epoch
            stats_cpu['iteration'] = updater.iteration
            x = stats_cpu[self._x_key]
            data = self._data

            for k in keys:
                if k in stats_cpu:
                    data[k].append((x, stats_cpu[k]))

            f = plt.figure()
            a = f.add_subplot(111)
            a.set_xlabel(self._x_key)
            if self._grid:
                a.grid(which='major', color='gray', linestyle=':')
                a.grid(which='minor', color='gray', linestyle=':')

            for i, k in enumerate(keys):
                xy = data[k]
                if len(xy) == 0:
                    continue

                xy = numpy.array(xy)
                plt.xscale("log")
                plt.yscale("log")
                a.plot(xy[:, 0], xy[:, 1], marker=self._marker, label=k, zorder=-i)

            if a.has_data():
                if self._postprocess is not None:
                    self._postprocess(f, a, summary)
                l = a.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
                f.savefig(path.join(trainer.out, self._file_name),
                          bbox_extra_artists=(l,), bbox_inches='tight')

                # 追加（validationの最新の値を表示）
                a.annotate('validation\n{0:8.6f}'.format(xy[-1, 1]),
                           xy=(xy[-1]), xycoords='data',
                           xytext=(-90, 75), textcoords='offset points',
                           bbox=dict(boxstyle="round", fc="0.8"),
                           arrowprops=dict(arrowstyle="->",
                                           connectionstyle="arc,angleA=0,armA=50,rad=10"))

            plt.close()
            self._init_summary()

    def serialize(self, serializer):
        if isinstance(serializer, serializer_module.Serializer):
            serializer('_plot_{}'.format(self._file_name),
                       json.dumps(self._data))

        else:
            self._data = json.loads(
                serializer('_plot_{}'.format(self._file_name), ''))

    def _init_summary(self):
        self._summary = reporter.DictSummary()
