from sumstats.utils.constants import *


class FloatInterval():
    pass

    def set_tuple(self, lower_limit, upper_limit):

        if lower_limit is not None:
            lower_limit = float(lower_limit)
        if upper_limit is not None:
            upper_limit = float(upper_limit)

        if _limits_are_none(lower_limit, upper_limit):
            is_none = True
        else:
            is_none = False

        self.is_none = is_none
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit

        return self

    def set_string_tuple(self, interval_string):
        if interval_string is not None:
            lower_limit = _get_lower_limit(interval_string)
            upper_limit = _get_upper_limit(interval_string)
        else:
            lower_limit = None
            upper_limit = None

        return self.set_tuple(lower_limit, upper_limit)

    def is_set(self):
        return self.is_none

    def floor(self):
        return self.lower_limit

    def ceil(self):
        return self.upper_limit


class IntInterval():
    pass

    def set_tuple(self, lower_limit, upper_limit):

        if lower_limit is not None:
            lower_limit = int(lower_limit)
        if upper_limit is not None:
            upper_limit = int(upper_limit)

        if _limits_are_none(lower_limit, upper_limit):
            is_none = True
        else:
            is_none = False

        self.is_none = is_none
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit

        return self

    def set_string_tuple(self, interval_string):
        if interval_string is not None:
            lower_limit = _get_lower_limit(interval_string)
            upper_limit = _get_upper_limit(interval_string)
        else:
            lower_limit = None
            upper_limit = None

        return self.set_tuple(lower_limit, upper_limit)

    def is_set(self):
        return self.is_none

    def floor(self):
        return self.lower_limit

    def ceil(self):
        return self.upper_limit


def _get_lower_limit(interval_string):
    lower_limit = interval_string.split(INTERVAL_DELIMITER)[0]
    if lower_limit is '':
        lower_limit = None
    return lower_limit


def _get_upper_limit(interval_string):
    upper_limit = interval_string.split(INTERVAL_DELIMITER)[1]
    if upper_limit is '':
        upper_limit = None
    return upper_limit


def _limits_are_none(lower_limit, upper_limit):
    return lower_limit is None and upper_limit is None