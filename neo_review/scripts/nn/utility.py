import random
import numpy as np


class Utility:
    def __call__(self):  # 乱数シード固定
        self.random_seed()

    @staticmethod
    def random_seed(seed=0):
        random.seed(seed)
        np.random.seed(seed)
