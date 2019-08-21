import chainer
import numpy as np
import pandas as pd


class LoadData:
    def __init__(self):  # HACK: refactor init
        data_path = '../../data/dataframes/'

        self._other_data = pd.read_pickle(data_path + 'data.pkl')

        nomination_onehot = (
            pd.read_pickle(data_path + 'nomination_onehot.pkl'))
        selected_performers_onehot = (
            pd.read_pickle(data_path + 'selected_performers_onehot.pkl'))
        selected_directors_onehot = (
            pd.read_pickle(data_path + 'selected_directors_onehot.pkl'))
        selected_studio_onehot = (
            pd.read_pickle(data_path + 'selected_studio_onehot.pkl'))
        selected_scriptwriter_onehot = (
            pd.read_pickle(data_path + 'selected_scriptwriter_onehot.pkl'))
        review_dataframe = (
            pd.read_pickle(data_path + 'review_dataframe.pkl'))

        df = pd.concat(
            [
                nomination_onehot,
                selected_performers_onehot,
                selected_directors_onehot,
                selected_studio_onehot,
                selected_scriptwriter_onehot,
                self._other_data['screen_time'],
                self._other_data['year'],
            ],
            axis=1).astype(np.float32)
        self._map = self._create_map(self._other_data, df)

    def __call__(self, *args, **kwargs):
        pass

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

        for year in range(1978, 2020):
            curr_df, other_df = pick_by_year(df, year)
            curr_data, other_data = pick_by_year(data, year)
            curr_sod, _ = pick_by_year(self._other_data, year)

            train = chainer.datasets.DictDataset(
                x=other_df.drop(["year"], axis=1).values.astype(np.float32),
                y=other_data["prize"].values.astype(np.float32),
            )

            test = chainer.datasets.DictDataset(
                x=curr_df.drop(["year"], axis=1).values.astype(np.float32),
                y=curr_data["prize"].values.astype(np.float32),
            )

            title = curr_sod["title"].values
            data_map[year] = train, test, title
        return data_map
