import openwebui_token_tracking.credit_groups as cg

import pytest

from dotenv import find_dotenv, load_dotenv

from fixtures import user


load_dotenv(find_dotenv())


def test_create_credit_group():
    assert (
        cg.create_credit_group(
            credit_group_name="test_credit_group",
            credit_allowance=0,
            description="Delete me",
        )
        is None
    )

    with pytest.raises(KeyError):
        cg.create_credit_group(
            credit_group_name="test_credit_group",
            credit_allowance=1000,
            description="Delete me",
        )


def test_add_user(user: dict[str, str]):
    assert (
        cg.add_user(user_id=user["id"], credit_group_name="test_credit_group") is None
    )

    with pytest.raises(KeyError):
        cg.add_user(credit_group_name="does not exist", user_id=user["id"])


def test_list_credit_groups():
    assert len(cg.list_credit_groups()) > 0


def test_list_users():
    print(cg.list_users(credit_group_name="test_credit_group"))
