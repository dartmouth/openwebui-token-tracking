import pytest
import sqlalchemy as db
from sqlalchemy.orm import Session

from openwebui_token_tracking.db import init_db
from openwebui_token_tracking.db.user import User
from openwebui_token_tracking.credit_groups import add_user, create_credit_group

import os

TEST_CREDIT_LIMIT = 2000
BASE_ALLOWANCE = 1000


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
    create_credit_group(
        database_url=os.environ["DATABASE_URL"],
        credit_group_name="test credit group",
        credit_allowance=TEST_CREDIT_LIMIT,
        description="Credit group for testing purposes.",
    )
    add_user(credit_group_name="test credit group", user_id=user["id"])


@pytest.fixture
def model():
    return {"id": "gpt-4o-2024-08-06", "provider": "openai"}
