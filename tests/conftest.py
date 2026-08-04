import pytest


@pytest.fixture
def employee_id():
    return 101


@pytest.fixture
def admin_id():
    return 1


@pytest.fixture
def sample_leave_dates():
    from datetime import date, timedelta

    start = date.today() + timedelta(days=5)
    end = start + timedelta(days=2)

    return start, end
