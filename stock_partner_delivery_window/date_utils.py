# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

import pytz
from dateutil.relativedelta import relativedelta


# This is a copy of odoo.tools.date_utils.date_range function,
# providing extra abilita to send a value that will be returned
# by an ensuing call to next
def date_range(start, end, step=relativedelta(months=1)):  # noqa: B008
    """Date range generator with a step interval.

    :param datetime start: beginning date of the range.
    :param datetime end: ending date of the range.
    :param relativedelta step: interval of the range.
    :return: a range of datetime from start to end.
    :rtype: Iterator[datetime]
    """

    are_naive = start.tzinfo is None and end.tzinfo is None
    are_utc = start.tzinfo == pytz.utc and end.tzinfo == pytz.utc

    # Cases with miscellenous timezone are more complexe because of DST.
    are_others = start.tzinfo and end.tzinfo and not are_utc

    if are_others:
        if start.tzinfo.zone != end.tzinfo.zone:
            raise ValueError(
                "Timezones of start argument and end argument seem inconsistent"
            )

    if not are_naive and not are_utc and not are_others:
        raise ValueError("Timezones of start argument and end argument mismatch")

    if start > end:
        raise ValueError("start > end, start date must be before end")

    if start == start + step:
        raise ValueError("Looks like step is null")

    if start.tzinfo:
        localize = start.tzinfo.localize
    else:
        localize = lambda dt: dt  # noqa: E731

    dt = start.replace(tzinfo=None)
    end = end.replace(tzinfo=None)
    while dt <= end:
        x = False
        x = yield localize(dt)
        if x:
            yield x
            dt = x
        else:
            dt = dt + step
