from sumstats.utils.interval import *


class TestUnitUtils(object):

    def test_is_interval_value(self):
        interval = FloatInterval().set_string_tuple("2:1")
        assert is_interval(interval)

        interval = FloatInterval().set_tuple(1., None)
        assert is_interval(interval)

        interval = IntInterval().set_string_tuple("2:1")
        assert is_interval(interval)

        assert not is_interval(2)

