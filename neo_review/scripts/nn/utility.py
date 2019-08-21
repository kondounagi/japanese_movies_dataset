import random
import numpy as np


class Utility:
    @staticmethod
    def set_random_seed(seed=0):
        random.seed(seed)
        np.random.seed(seed)
