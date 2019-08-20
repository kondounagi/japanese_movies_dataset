import chainer
import numpy as np
import pandas as pd


class LoadData:
    def __init__(self):  # HACK: refactor init
        data_pass = '../../data/dataframes/'

        self.other_data = pd.read_pickle(data_pass + 'data.pkl')
        nomination_onehot = pd.read_pickle(data_pass + 'nomination_onehot.pkl')
        selected_performers_onehot = pd.read_pickle(data_pass + 'selected_performers_onehot.pkl')
        selected_directors_onehot = pd.read_pickle(data_pass + 'selected_directors_onehot.pkl')
        selected_studio_onehot = pd.read_pickle(data_pass + 'selected_studio_onehot.pkl')
        selected_scriptwriter_onehot = pd.read_pickle(data_pass + 'selected_scriptwriter_onehot.pkl')
        review_dataframe = pd.read_pickle(data_pass + 'review_dataframe.pkl')

        self.x = pd.concat(
            [
                nomination_onehot,
                selected_performers_onehot,
                selected_directors_onehot,
                selected_studio_onehot,
                selected_scriptwriter_onehot,
                self.other_data['screen_time'],
                self.other_data['year'],
            ],
            axis=1).astype(np.float32)
        self.map = self.create_map(self.other_data, self.x)

    def __call__(self, *args, **kwargs):
        pass

    def create_map(self, data, df):
        data_map = {}
        for year in range(1978, 2020):
            train = chainer.datasets.DictDataset(
                x=df[df["year"] != year].drop(["year"], axis=1).values.astype(np.float32),
                y=data[data["year"] != year]["prize"].values.astype(np.float32)
            )
            test = chainer.datasets.DictDataset(
                x=df[df["year"] == year].drop(["year"], axis=1).values.astype(np.float32),
                y=data[data["year"] == year]["prize"].values.astype(np.float32)
            )
            title = self.other_data[self.other_data["year"] == year]["title"].values
            data_map[year] = train, test, title
        return data_map
