import pytest
from sqlalchemy.orm import Session

from openwebui_token_tracking import TokenTracker
from openwebui_token_tracking.db import init_db
from openwebui_token_tracking.db.user import User
from openwebui_token_tracking.credit_groups import (
    add_user,
    create_credit_group,
    get_credit_group,
)
from openwebui_token_tracking.sponsored import (
    create_sponsored_allowance,
    get_sponsored_allowance,
)

import os


BASE_ALLOWANCE = 1000
TEST_CREDIT_GROUP_NAME = "test credit group"
TEST_CREDIT_GROUP_LIMIT = 2000

TEST_SPONSORED_ALLOWANCE_SPONSOR = "f12345"
TEST_SPONSORED_ALLOWANCE_NAME = "test sponsored allowance"
TEST_SPONSORED_ALLOWANCE_MODELS = ["mistral-small-2409", "claude-3-5-haiku-20241022"]
TEST_SPONSORED_ALLOWANCE_DAILY_LIMIT = 500
TEST_SPONSORED_ALLOWANCE_TOTAL_LIMIT = 10000


@pytest.fixture
def tracker():
    return TokenTracker(db_url=os.environ["DATABASE_URL"])


@pytest.fixture
def user():
    # Make sure a user table exists in the database
    engine = init_db(os.environ["DATABASE_URL"])
    User.__table__.create(bind=engine, checkfirst=True)

    # Upsert a test user
    test_user = {
        "id": "a80b7cc8-c8ab-48e2-ba74-f56086d83644",
        "name": "Test user",
        "email": "ai.integration@dartmouth.edu",
    }
    with Session(engine) as session:
        session.merge(User(**test_user))
        session.commit()

    return test_user


@pytest.fixture
def with_credit_group(user):
    try:
        cg = get_credit_group(
            database_url=os.environ["DATABASE_URL"],
            credit_group_name=TEST_CREDIT_GROUP_NAME,
        )
    except KeyError:
        create_credit_group(
            database_url=os.environ["DATABASE_URL"],
            credit_group_name=TEST_CREDIT_GROUP_NAME,
            credit_allowance=TEST_CREDIT_GROUP_LIMIT,
            description="Credit group for testing purposes.",
        )
        add_user(credit_group_name=TEST_CREDIT_GROUP_NAME, user_id=user["id"])


@pytest.fixture
def with_sponsored_allowance():
    try:
        sa = get_sponsored_allowance(
            database_url=os.environ["DATABASE_URL"],
            name=TEST_SPONSORED_ALLOWANCE_NAME,
        )
    except KeyError:
        create_sponsored_allowance(
            database_url=os.environ["DATABASE_URL"],
            sponsor_id=TEST_SPONSORED_ALLOWANCE_SPONSOR,
            name=TEST_SPONSORED_ALLOWANCE_NAME,
            models=TEST_SPONSORED_ALLOWANCE_MODELS,
            daily_credit_limit=TEST_SPONSORED_ALLOWANCE_DAILY_LIMIT,
            total_credit_limit=TEST_SPONSORED_ALLOWANCE_TOTAL_LIMIT,
        )


@pytest.fixture
def model():
    return {"id": "gpt-4o-2024-08-06", "provider": "openai"}
