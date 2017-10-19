"""
Classes that have a get_mask method
They impose restrictions to the datasets based on some criteria
"""

from sumstats.utils import utils


class IntervalRestriction():
    def __init__(self, lower, upper, dataset):
        self.lower = lower
        self.upper = upper
        self.dataset = dataset

    def get_mask(self):
        return utils.interval_mask(self.lower, self.upper, self.dataset)


class EqualityRestriction():
    def __init__(self, value, dataset):
        self.value = value
        self.dataset = dataset

    def get_mask(self):
        return utils.equality_mask(self.value, self.dataset)