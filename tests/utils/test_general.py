# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals
from datetime import datetime, date

import pytest

from estuary.utils.general import (
    timestamp_to_datetime, timestamp_to_date)


@pytest.mark.parametrize('input_dt,expected_dt', [
    ('2018-04-15T20:30:00Z', datetime(2018, 4, 15, 20, 30)),
    ('2018-04-15T20:30:10Z', datetime(2018, 4, 15, 20, 30, 10)),
    ('2022-04-21T21:30:10', datetime(2022, 4, 21, 21, 30, 10)),
    ('2018-04-15T20:30:10.12312Z', datetime(2018, 4, 15, 20, 30, 10))
])
def test_timestamp_to_datetime_iso(input_dt, expected_dt):
    """Test that an ISO 8601 timestamp can be converted to a datetime object."""
    assert timestamp_to_datetime(input_dt) == expected_dt


@pytest.mark.parametrize('input_dt,expected_dt', [
    ('2018-04-15', datetime(2018, 4, 15)),
    ('2018-4-15', datetime(2018, 4, 15)),
    ('2018-04-15 20:30:10', datetime(2018, 4, 15, 20, 30, 10)),
    ('2018-4-1 21:30:10', datetime(2018, 4, 1, 21, 30, 10))
])
def test_timestamp_to_datetime(input_dt, expected_dt):
    """Test that a generic timestamp can be converted to a datetime object."""
    assert timestamp_to_datetime(input_dt) == expected_dt


@pytest.mark.parametrize('input_date,expected_date', [
    ('2018-04-15', date(2018, 4, 15)),
    ('2018-4-15', date(2018, 4, 15)),
    ('2018-04-15 20:30:10', date(2018, 4, 15)),
    ('2018-4-1 21:30:10', date(2018, 4, 1))
])
def test_timestamp_to_date(input_date, expected_date):
    """Test that a timestamp can be converted to a date object."""
    assert timestamp_to_date(input_date) == expected_date


@pytest.mark.parametrize('input_dt', [
    ('2018-04-15T20:30:1'),
    ('2018-04-1520:30:10'),
    ('2018-04-15T20:90:10'),
    ('2018-04-15 90:30:10'),
    ('2018-04-90 20:30:10'),
    ('2018-90-15'),
])
def test_timestamp_to_datetime_invalid(input_dt):
    """Test that an error is raised when an invalid timestamp is provided."""
    with pytest.raises(ValueError)as exc_info:
        timestamp_to_datetime(input_dt)
    assert 'The timestamp "{0}" is an invalid format'.format(input_dt) == str(exc_info.value)
