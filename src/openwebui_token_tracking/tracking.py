from openwebui_token_tracking.db import init_db
from openwebui_token_tracking.db.token_usage import TokenUsageLog
from openwebui_token_tracking.db.credit_group import CreditGroup, CreditGroupUser
from openwebui_token_tracking.db.settings import BaseSetting
from openwebui_token_tracking.db.model_pricing import ModelPricing
from openwebui_token_tracking.models import ModelPricingSchema
from openwebui_token_tracking.db.sponsored import SponsoredAllowance
from openwebui_token_tracking.sponsored import get_sponsored_allowance


import sqlalchemy as db
from sqlalchemy.orm import Session

from datetime import datetime, date, UTC
import logging
from typing import Iterable
from uuid import UUID

logger = logging.getLogger(__name__)


class TokenLimitExceededError(Exception):
    """Raised when a token limit was exceeded"""

    pass


class DailyTokenLimitExceededError(TokenLimitExceededError):
    """Raised when a daily token limit was exceeded"""

    pass


class TotalTokenLimitExceededError(TokenLimitExceededError):
    """Raised when a total token limit was exceeded"""

    pass


class TokenTracker:
    """A class for tracking token usage and managing credit limits for users.

    The TokenTracker connects to the Open WebUI database to track token
    consumption by users, calculate remaining credits, and enforce token usage
    limits across different models and providers.

    :param db_url: Database connection URL
    :type db_url: str

    :ivar db_engine: SQLAlchemy database engine
    :ivar db_url: Database connection URL

    :raises TokenLimitExceededError: When a token limit is exceeded
    :raises DailyTokenLimitExceededError: When a daily token limit is exceeded
    :raises TotalTokenLimitExceededError: When a total token limit is exceeded
    """
    def __init__(self, db_url: str):
        self.db_engine = init_db(db_url)
        self.db_url = db_url

    def _calc_credits_from_tokens(
        self, records: Iterable[tuple[str, int, int]], models: list[ModelPricingSchema]
    ) -> int:
        """Calculates the number of consumed credits from a series of token logs

        :param records: A token log record consisting of the model ID, the number of
        consumed input tokens, and the number of consumed output tokens
        :type records: Iterable[tuple[str, int, int]]
        :param models: A list of the pricing schemas of all models appearing in the records
        :type models: list[ModelPricingSchema]
        :return: Total number of credits used
        :rtype: int
        """
        used_credits = 0
        for row in records:
            (cur_model, cur_prompt_tokens, cur_response_tokens) = row
            model_data = next((item for item in models if item.id == cur_model), None)

            model_cost = (
                model_data.input_cost_credits / model_data.per_input_tokens
            ) * cur_prompt_tokens + (
                model_data.output_cost_credits / model_data.per_output_tokens
            ) * cur_response_tokens

            used_credits += model_cost
        return used_credits

    def _remaining_user_credits(
        self, user: dict, sponsored_allowance_id: UUID | None
    ) -> int:
        """Return user's remaining daily credits.

        If the name of a sponsored allowance is provided, the daily credit limit is
        calculated considering only the daily limit from that allowance.
        Otherwise, the remaining credits are calculated using the user's group allowances.

        :param user_id: User
        :type user_id: dict
        :param sponsored_allowance_id: ID of a sponsored allowance to consider
        :type sponsored_allowance_id: UUID, optional
        :return: Remaining credits
        :rtype: int
        """

        with Session(self.db_engine) as session:
            current_date = date.today()
            logger.debug(current_date)
            models = self.get_models()
            model_list = [m.id for m in models]

            query = (
                db.select(
                    TokenUsageLog.model_id,
                    db.func.sum(TokenUsageLog.prompt_tokens).label("prompt_tokens_sum"),
                    db.func.sum(TokenUsageLog.response_tokens).label(
                        "response_tokens_sum"
                    ),
                )
                .where(
                    TokenUsageLog.user_id == user["id"],
                    db.func.date(TokenUsageLog.log_date) == current_date,
                    TokenUsageLog.model_id.in_(model_list),
                    TokenUsageLog.sponsored_allowance_id == sponsored_allowance_id,
                )
                .group_by(TokenUsageLog.model_id)
            )
            results = session.execute(query).fetchall()

            used_daily_credits = self._calc_credits_from_tokens(
                records=results, models=models
            )

        return self.max_credits(
            user, sponsored_allowance_id=sponsored_allowance_id
        ) - int(used_daily_credits)

    def _remaining_sponsored_credits(self, sponsored_allowance_id: str):
        """Get remaining credits in a sponsored allowance

        :param sponsored_allowance_id: ID of the sponsored allowance
        :type sponsored_allowance_id: str
        :return: Remaining credits in the allowance
        :rtype: int
        """

        with Session(self.db_engine) as session:
            query = db.select(
                SponsoredAllowance.creation_date,
                SponsoredAllowance.total_credit_limit,
            ).where(SponsoredAllowance.id == sponsored_allowance_id)

            creation_date, total_credit_limit = session.execute(query).first()

            models = self.get_models()
            model_list = [m.id for m in models]

            query = (
                db.select(
                    TokenUsageLog.model_id,
                    db.func.sum(TokenUsageLog.prompt_tokens).label("prompt_tokens_sum"),
                    db.func.sum(TokenUsageLog.response_tokens).label(
                        "response_tokens_sum"
                    ),
                )
                .where(
                    TokenUsageLog.sponsored_allowance_id == sponsored_allowance_id,
                    db.func.date(TokenUsageLog.log_date) <= creation_date,
                    TokenUsageLog.model_id.in_(model_list),
                )
                .group_by(TokenUsageLog.model_id)
            )
            results = session.execute(query).fetchall()

            total_credits_used = self._calc_credits_from_tokens(
                records=results, models=models
            )
            return int(total_credit_limit - total_credits_used)

    def get_models(
        self, provider: str = None, id: str = None
    ) -> list[ModelPricingSchema]:
        """Get all available models.

        :param provider: If not None, only returns the models by this provider. Defaults to None
        :type provider: str, optional
        :return: A description of the models' pricing schema
        :rtype: list[ModelPricingSchema]
        """

        with Session(self.db_engine) as session:
            if provider is None:
                models = session.query(ModelPricing).all()
            else:
                models = (
                    session.query(ModelPricing)
                    .filter(ModelPricing.provider == provider)
                    .all()
                )
        return [
            ModelPricingSchema.model_validate(m, from_attributes=True) for m in models
        ]

    def is_paid(self, model_id: str) -> bool:
        """Check whether a model requires credits to use

        :param model_id: ID of the model
        :type model_id: str
        :return: True if credits are required to use this model, False otherwise
        :rtype: bool
        """
        model = [m for m in self.get_models() if m.id == model_id]
        if len(model) != 1:
            raise RuntimeError(
                f"Could not uniquely determine the model based on {model_id=}!"
            )
        return model[0].input_cost_credits > 0 or model[0].output_cost_credits > 0

    def max_credits(
        self,
        user: dict,
        sponsored_allowance_name: str = None,
        sponsored_allowance_id: UUID = None,
    ) -> int:
        """Get a user's maximum daily credits.

        :param user: User
        :type user: dict
        :param sponsored_allowance_name: Name of the sponsored allowance to consider
        :type sponsored_allowance_name: str, optional
        :param sponsored_allowance_id: ID of the sponsored allowance to consider
        :type sponsored_allowance_id: str, optional
        :return: Maximum daily credit allowance
        :rtype: int
        """
        if sponsored_allowance_name is not None and sponsored_allowance_id is not None:
            raise RuntimeError(
                """Pass either `sponsored_allowance_name` or
                `sponsored_allowance_id`, not both!"""
            )
        with Session(self.db_engine) as session:
            if sponsored_allowance_name is None and sponsored_allowance_id is None:
                base_allowance = int(
                    session.query(BaseSetting)
                    .filter(BaseSetting.setting_key == "base_credit_allowance")
                    .scalar()
                    .setting_value
                )
                group_allowances = (
                    session.query(
                        db.func.coalesce(db.func.sum(CreditGroup.max_credit), 0)
                    )
                    .join(
                        CreditGroupUser,
                        CreditGroup.id == CreditGroupUser.credit_group_id,
                    )
                    .filter(CreditGroupUser.user_id == user["id"])
                    .scalar()
                )
                max_credits = base_allowance + group_allowances
            elif sponsored_allowance_name is not None:
                max_credits = (
                    session.query(SponsoredAllowance.daily_credit_limit)
                    .filter(SponsoredAllowance.name == sponsored_allowance_name)
                    .scalar()
                )
            elif sponsored_allowance_id is not None:
                max_credits = (
                    session.query(SponsoredAllowance.daily_credit_limit)
                    .filter(SponsoredAllowance.id == sponsored_allowance_id)
                    .scalar()
                )

        return max_credits

    def remaining_credits(
        self, user: dict, sponsored_allowance_name: str = None
    ) -> tuple[int, int]:
        """Get remaining credits for the specified user and sponsored
        allowance.

        :param user_id: User
        :type user_id: dict
        :param sponsored_allowance_name: Name of the sponsored allowance
        :type sponsored_allowance_name: str, optional
        :return: Remaining daily credits available to the user, and in the sponsored allowance (if specified)
        :rtype: tuple[int, int]
        """
        logger.debug("Checking remaining credits...")

        if sponsored_allowance_name is not None:
            sponsored_allowance_id = UUID(
                get_sponsored_allowance(
                    database_url=self.db_url, name=sponsored_allowance_name
                )["id"]
            )
        else:
            sponsored_allowance_id = None
        user_credits_remaining = self._remaining_user_credits(
            user, sponsored_allowance_id
        )
        total_sponsored_credits_remaining = None
        if sponsored_allowance_name:
            total_sponsored_credits_remaining = self._remaining_sponsored_credits(
                sponsored_allowance_id
            )
        return user_credits_remaining, total_sponsored_credits_remaining

    def log_token_usage(
        self,
        provider: str,
        model_id: str,
        user: dict,
        prompt_tokens: int,
        response_tokens: int,
        sponsored_allowance_name: str = None,
    ):
        """Log the used tokens in the database

        :param provider: Provider of the model used with these tokens
        :type provider: str
        :param model_id: ID of the model used with these tokens
        :type model_id: str
        :param user: User
        :type user: dict
        :param prompt_tokens: Number of tokens used in the prompt (input tokens)
        :type prompt_tokens: int
        :param response_tokens: Number of tokens in the response (output tokens)
        :type response_tokens: int
        :param sponsored_allowance_name: Name of the sponsored allowance to apply
        :type sponsored_allowance_name: str, optional
        """
        logging.debug(
            f"Date: {datetime.now(UTC)}Z | Email: {user.get('email')} "
            f"| Model: {model_id} | Prompt Tokens: {prompt_tokens} "
            f"| Response Tokens: {response_tokens}"
        )

        with Session(self.db_engine) as session:
            if sponsored_allowance_name is not None:
                sponsored_allowance_id = UUID(
                    get_sponsored_allowance(
                        database_url=self.db_url, name=sponsored_allowance_name
                    )["id"]
                )
            else:
                sponsored_allowance_id = None

            session.add(
                TokenUsageLog(
                    provider=provider,
                    user_id=user.get("id"),
                    model_id=model_id,
                    prompt_tokens=prompt_tokens,
                    response_tokens=response_tokens,
                    sponsored_allowance_id=sponsored_allowance_id,
                    log_date=datetime.now(),
                )
            )
            session.commit()


if __name__ == "__main__":
    from dotenv import find_dotenv, load_dotenv
    import os

    load_dotenv(find_dotenv())

    logging.basicConfig(level=logging.INFO)

    acc = TokenTracker(os.environ["DATABASE_URL"])

    print(acc.get_models())
    print(acc.get_models(provider="anthropic"))
