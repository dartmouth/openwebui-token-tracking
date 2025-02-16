from openwebui_token_tracking import TokenTracker
from openwebui_token_tracking.db import CreditGroup, CreditGroupUser, User

import pytest
import sqlalchemy as db
from sqlalchemy.orm import Session
from dotenv import find_dotenv, load_dotenv

import os

load_dotenv(find_dotenv())


TEST_CREDIT_LIMIT = 2000
BASELINE_ALLOWANCE = 1000


@pytest.fixture
def tracker():
    return TokenTracker(db_url=os.environ["DATABASE_URL"])


@pytest.fixture
def user():
    # Make sure a user table exists in the database
    engine = db.create_engine(os.environ["DATABASE_URL"])
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
    # Make sure user has an associated credit group
    engine = db.create_engine(os.environ["DATABASE_URL"])

    with Session(engine) as session:
        # Create test credit group if necessary
        credit_group = (
            session.query(CreditGroup).filter_by(name="test credit group").first()
        )
        if not credit_group:
            session.add(
                CreditGroup(name="test credit group", max_credit=TEST_CREDIT_LIMIT)
            )
            credit_group = (
                session.query(CreditGroup).filter_by(name="test credit group").first()
            )

        # Add user to credit group
        user = session.query(User).filter_by(id=user["id"]).first()
        session.add(CreditGroupUser(credit_group_id=credit_group.id, user_id=user.id))
        session.commit()


@pytest.fixture
def model():
    return {"id": "gpt-4o-2024-08-06"}


def test_max_credits(tracker, user, with_credit_group):
    assert tracker.max_credits(user) == TEST_CREDIT_LIMIT + BASELINE_ALLOWANCE


def test_remaining_credits(tracker, user):
    assert tracker.remaining_credits(user) > 0


def test_log_token_usage(tracker, model, user):
    tracker.log_token_usage(
        model_id=model["id"],
        user=user,
        prompt_tokens=1,
        response_tokens=1,
    )


def test_is_paid(tracker, model):
    assert tracker.is_paid(model["id"])


if __name__ == "__main__":
    print(with_credit_group(user()))
