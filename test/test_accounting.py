from dartmouth_chat_accounting import Accountant

import pytest


@pytest.fixture
def accountant():
    from dotenv import find_dotenv, load_dotenv
    import os

    load_dotenv(find_dotenv())

    return Accountant(db_url=os.environ["DATABASE_URL"])


@pytest.fixture
def user():
    return {
        "id": "a80b7cc8-c8ab-48e2-ba74-f56086d83644",
        "email": "ai.integration@dartmouth.edu",
    }


@pytest.fixture
def model():
    return {"id": "openai.gpt-4o-2024-08-06"}


def test_remaining_credits(accountant, user):
    assert accountant.remaining_credits(user) > 0


def test_log_token_usage(accountant, model, user):
    accountant.log_token_usage(
        model_id=model["id"],
        user=user,
        prompt_tokens=1,
        response_tokens=1,
    )
