from openwebui_token_tracking import TokenTracker

import pytest

from dotenv import find_dotenv, load_dotenv

import os

from fixtures import user, with_credit_group, TEST_CREDIT_LIMIT, model

load_dotenv(find_dotenv())


@pytest.fixture
def tracker():
    return TokenTracker(db_url=os.environ["DATABASE_URL"])


def test_max_credits(tracker, user, with_credit_group):
    assert tracker.max_credits(user) == TEST_CREDIT_LIMIT + BASELINE_ALLOWANCE


def test_remaining_credits(tracker, user):
    assert tracker.remaining_credits(user) > 0


def test_log_token_usage(tracker, model, user):
    tracker.log_token_usage(
        model_id=model["id"],
        provider=model["provider"],
        user=user,
        prompt_tokens=1,
        response_tokens=1,
    )


def test_is_paid(tracker, model):
    assert tracker.is_paid(model["id"])


if __name__ == "__main__":
    print(with_credit_group(user()))
