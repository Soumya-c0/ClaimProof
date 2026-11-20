import pytest

@pytest.mark.parametrize('days,expected', [(20, 'reject'), (35, 'approve')])
def test_waiting_period_boundary(days, expected):
    outcome = 'approve' if days >= 30 else 'reject'
    assert outcome == expected