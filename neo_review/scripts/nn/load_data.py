import chainer
import numpy as np
import pandas as pd
from chainer.datasets import split_dataset_random


class LoadData:
    def __init__(self):
        _other_data = pd.read_pickle('../../data/dataframes/data.pkl')
        self._map = self._create_map(_other_data)

    @property
    def map(self):
        return self._map

    def _create_map(self, data):
        data_map = {}

        def pick(df, func):
            cond = func(df)
            return df[cond], df[~cond]

        def pick_by_year(df, year):
            return pick(df, lambda x: x["year"] == year)

        def shuffle_samples(*args):
            zipped = list(zip(*args))
            np.random.shuffle(zipped)
            shuffled = list(zip(*zipped))
            result = []
            for ar in shuffled:
                result.append(np.asarray(ar))
            return result

        for year in range(1978, 2020):
            curr_sod, _ = pick_by_year(data, year)

            base = '../../data/std_data'
            pkl_train_x = pd.read_pickle(base + '/train/{}_x.pkl'.format(year))
            pkl_train_y = pd.read_pickle(base + '/train/{}_y.pkl'.format(year))
            pkl_test_x = pd.read_pickle(base + '/test/{}_x.pkl'.format(year))
            pkl_test_y = pd.read_pickle(base + '/test/{}_y.pkl'.format(year))

            train_x, train_y = shuffle_samples(
                pkl_train_x.values.astype(np.float32),
                pkl_train_y.values.astype(np.float32),
            )

            train = chainer.datasets.DictDataset(x=train_x, y=train_y)
            train, valid = split_dataset_random(train, 1, seed=0)

            train = chainer.datasets.DictDataset(x=[t['x'] for t in train], y=[t['y'] for t in train])
            valid = chainer.datasets.DictDataset(x=[v['x'] for v in valid], y=[v['y'] for v in valid])

            test_x, test_y = (
                pkl_test_x.values.astype(np.float32),
                pkl_test_y.values.astype(np.float32),
            )
            test = chainer.datasets.DictDataset(x=test_x, y=test_y)

            title = curr_sod["title"].values
            data_map[year] = train, valid, test, title
        return data_map
