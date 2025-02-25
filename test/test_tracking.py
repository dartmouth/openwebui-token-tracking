from dotenv import find_dotenv, load_dotenv

from fixtures import (
    user,
    with_credit_group,
    with_sponsored_allowance,
    TEST_CREDIT_GROUP_LIMIT,
    TEST_SPONSORED_ALLOWANCE_NAME,
    TEST_SPONSORED_ALLOWANCE_DAILY_LIMIT,
    TEST_SPONSORED_ALLOWANCE_TOTAL_LIMIT,
    BASE_ALLOWANCE,
    model,
    tracker,
)

load_dotenv(find_dotenv())


def test_max_credits(tracker, user, with_credit_group, with_sponsored_allowance):
    # Simple daily allowance for user (based on credit groups)
    assert tracker.max_credits(user) == TEST_CREDIT_GROUP_LIMIT + BASE_ALLOWANCE
    # Daily credits through sponsored allowance
    assert (
        tracker.max_credits(
            user, sponsored_allowance_name=TEST_SPONSORED_ALLOWANCE_NAME
        )
        == TEST_SPONSORED_ALLOWANCE_DAILY_LIMIT
    )


def test_remaining_credits(tracker, user, with_sponsored_allowance):
    # Remaining credits without a sponsored allowance
    daily_credits, total_sponsored_credits = tracker.remaining_credits(user)
    assert daily_credits > 0
    assert total_sponsored_credits is None

    # Remaining credits with a sponsored allowance
    daily_credits, total_sponsored_credits = tracker.remaining_credits(
        user, TEST_SPONSORED_ALLOWANCE_NAME
    )
    assert daily_credits == TEST_SPONSORED_ALLOWANCE_DAILY_LIMIT
    assert total_sponsored_credits == TEST_SPONSORED_ALLOWANCE_TOTAL_LIMIT


def test_log_token_usage(tracker, model, user, with_sponsored_allowance):
    tracker.log_token_usage(
        model_id=model["id"],
        provider=model["provider"],
        user=user,
        prompt_tokens=1,
        response_tokens=1,
    )
    tracker.log_token_usage(
        model_id=model["id"],
        provider=model["provider"],
        user=user,
        prompt_tokens=10,
        response_tokens=10,
        sponsored_allowance_name=TEST_SPONSORED_ALLOWANCE_NAME,
    )


def test_is_paid(tracker, model):
    assert tracker.is_paid(model["id"])
