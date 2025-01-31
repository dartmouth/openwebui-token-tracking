from openwebui_token_tracking.models import DEFAULT_MODEL_PRICING

import sqlalchemy as db

from datetime import datetime, UTC
import logging

logger = logging.getLogger(__name__)


class TokenTracker:
    def __init__(self, db_url: str):
        self.db_engine = db.create_engine(db_url)

    def is_paid(self, model_id: str) -> bool:
        """Check whether a model requires credits to use

        :param model_id: ID of the model
        :type model_id: str
        :return: True if credits are required to use this model, False otherwise
        :rtype: bool
        """
        model = [m for m in DEFAULT_MODEL_PRICING if m.id == model_id]
        if len(model) != 1:
            raise RuntimeError(
                f"Could not uniquely determine the model based on {model_id=}!"
            )
        return model[0].input_cost_credits > 0 or model[0].output_cost_credits > 0

    def max_credits(self, user: dict) -> int:
        """Get a user's maximum daily credits

        :param user: User
        :type user: dict
        :return: Maximum daily credit allowance
        :rtype: int
        """

        return 1000  # TODO: Make this depend on the user's group affiliations

    def remaining_credits(self, user: dict) -> int:
        """Get a user's remaining credits

        :param user_id: User
        :type user_id: dict
        :return: Remaining credits
        :rtype: int
        """

        with self.db_engine.connect() as connection:
            statement = db.text(
                """
                select model, sum(prompt_tokens) prompt_tokens_sum,
                sum(response_tokens) response_tokens_sum
                from token_usage_log join "user" on token_usage_log.user_id = "user".id
                where user_id = :user_id
                and DATE_TRUNC('day', log_date AT TIME ZONE 'America/New_York')
                = DATE_TRUNC('day', now() AT TIME ZONE 'America/New_York')
                and model in :model_list
                group by model
                """
            )
            data = {
                "user_id": user["id"],
                "model_list": tuple(m.id for m in DEFAULT_MODELS),
            }
            result = connection.execute(statement, data)
        used_daily_credits = 0
        for row in result:
            (cur_model, cur_prompt_tokens_sum, cur_response_tokens_sum) = row
            model_data = next(
                (item for item in DEFAULT_MODELS if item.id == cur_model), None
            )

            model_cost_today = (
                model_data.input_cost_credits / model_data.per_input_tokens
            ) * cur_prompt_tokens_sum + (
                model_data.output_cost_credits / model_data.per_output_tokens
            ) * cur_response_tokens_sum

            used_daily_credits += model_cost_today

            logging.info(
                f"Date: {datetime.now(UTC)}Z | Email: {user.get('email')} "
                f"| Model: {cur_model} | Prompt Tokens: {cur_prompt_tokens_sum} "
                f"| Response Tokens: {cur_response_tokens_sum} "
                f"| Cost today: {model_cost_today}"
            )

        return self.max_credits(user) - int(used_daily_credits)

    def log_token_usage(
        self, model_id: str, user: dict, prompt_tokens: int, response_tokens: int
    ):
        """Log the used tokens in the database

        :param model_id: ID of the model used with these tokens
        :type model_id: str
        :param user: User
        :type user: dict
        :param prompt_tokens: Number of tokens used in the prompt (input tokens)
        :type prompt_tokens: int
        :param response_tokens: Number of tokens in the response (output tokens)
        :type response_tokens: int
        """
        logging.info(
            f"Date: {datetime.now(UTC)}Z | Email: {user.get('email')} "
            f"| Model: {model_id} | Prompt Tokens: {prompt_tokens} "
            f"| Response Tokens: {response_tokens}"
        )
        with self.db_engine.connect() as connection:
            statement = db.text(
                "insert into token_usage_log (log_date, user_id, model, prompt_tokens, "
                "response_tokens) VALUES (now(), :user_id, :model, :prompt_tokens, "
                ":response_tokens)"
            )
            data = {
                "user_id": user.get("id"),
                "model": model_id,
                "prompt_tokens": prompt_tokens,
                "response_tokens": response_tokens,
            }
            connection.execute(statement, data)
            connection.commit()


if __name__ == "__main__":
    from dotenv import find_dotenv, load_dotenv
    import os

    load_dotenv(find_dotenv())

    logging.basicConfig(level=logging.INFO)

    acc = TokenTracker(os.environ["DATABASE_URL"])

    print(
        acc.remaining_credits(
            user={
                "id": "c555fd72-fada-440f-9238-8948beeadd34",
                "email": "simon.stone@dartmouth.edu",
            },
        )
    )

    acc.log_token_usage(
        model_id=DEFAULT_MODELS[0].id,
        user={
            "id": "c555fd72-fada-440f-9238-8948beeadd34",
            "email": "simon.stone@dartmouth.edu",
        },
        prompt_tokens=1,
        response_tokens=1,
    )
