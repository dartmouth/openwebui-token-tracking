from openwebui_token_tracking.credit_groups import add_user, create_credit_group

import pytest

from dotenv import find_dotenv, load_dotenv

from fixtures import user


load_dotenv(find_dotenv())


def test_create_credit_group():
    assert (
        create_credit_group(credit_group_name="test_credit_group", credit_allowance=0)
        is None
    )

    with pytest.raises(KeyError):
        create_credit_group(
            credit_group_name="test_credit_group", credit_allowance=1000
        )


def test_add_user(user):
    assert add_user(user_id=user["id"], credit_group_name="test_credit_group") is None

    with pytest.raises(KeyError):
        add_user(credit_group_name="does not exist", user_id=user["id"])
