import pytest
import app.utils.decorators as decorators

from app.utils.decorators import with_retry
from app.utils.logger import configure_logging

configure_logging(level="DEBUG", environment="development")


def test_retry_raises_after_max_retries(monkeypatch):
    sleep_calls = []

    def fake_sleep(seconds):
        sleep_calls.append(seconds)

    # replace sleep function with fake_sleep dummy function
    # which records the sleep time in a list
    monkeypatch.setattr(decorators.time, "sleep", fake_sleep)

    call_count = 0

    @with_retry(max_retry=3, backoff=0.2)
    def always_fail():
        nonlocal call_count
        call_count += 1
        raise ValueError("boom")

    with pytest.raises(ValueError, match="boom"):
        always_fail()

    assert call_count == 3
    assert sleep_calls == [0.2, 0.4]


def test_retry_after_failure(monkeypatch):
    sleep_calls = []

    def fake_sleep(seconds):
        sleep_calls.append(seconds)

    monkeypatch.setattr(decorators.time, "sleep", fake_sleep)

    call_count = 0

    @with_retry(max_retry=3, backoff=0.2)
    def eventually_succeeds():
        nonlocal call_count
        if call_count < 2:
            call_count += 1
            raise ValueError("boom")
        return True

    result = eventually_succeeds()

    assert result is True
    assert call_count == 2
    assert sleep_calls == [0.2, 0.4]
