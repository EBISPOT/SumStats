"""
Classes that have a get_mask method
They impose restrictions to the datasets based on some criteria
"""


class IntervalRestriction():
    def __init__(self, lower, upper, dataset):
        self.lower = lower
        self.upper = upper
        self.dataset = dataset

    def get_mask(self):
        return self.dataset.interval_mask(self.lower, self.upper)


class EqualityRestriction():
    def __init__(self, value, dataset):
        self.value = value
        self.dataset = dataset

    def get_mask(self):
        return self.dataset.equality_mask(self.value)