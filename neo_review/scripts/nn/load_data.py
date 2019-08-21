import chainer
import numpy as np
import pandas as pd


class LoadData:
    def __init__(self):  # HACK: refactor init
        data_path = '../../data/dataframes/'

        _other_data = pd.read_pickle(data_path + 'data.pkl')
        df = pd.read_pickle('../../data/dataframes/pos_val_df.pkl')

        self._map = self._create_map(_other_data, df)

    @property
    def map(self):
        return self._map

    def _create_map(self, data, df):
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
            curr_df, other_df = pick_by_year(df, year)
            curr_data, other_data = pick_by_year(data, year)
            curr_sod, _ = pick_by_year(data, year)

            train_x, train_y = shuffle_samples(
                other_df.drop(["year"], axis=1).values.astype(np.float32),
                other_data["prize"].values.astype(np.float32),
            )

            test_x, test_y = (
                curr_df.drop(["year"], axis=1).values.astype(np.float32),
                curr_data["prize"].values.astype(np.float32),
            )

            train = chainer.datasets.DictDataset(x=train_x, y=train_y)
            test = chainer.datasets.DictDataset(x=test_x, y=test_y)

            title = curr_sod["title"].values
            data_map[year] = train, test, title
        return data_map
