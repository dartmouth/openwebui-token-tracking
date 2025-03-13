"""
Provider interface for AI model APIs with token tracking.

This module provides a base class for implementing providers that interface
with various AI model APIs while tracking token usage. It handles both
streaming and non-streaming responses, and manages token usage limits.

Classes:
    BaseTrackedPipe: Abstract base class for AI model providers
    TokenLimitExceededError: Exception for token limit violations
    RequestError: Exception for API request failures
"""

from abc import ABC, abstractmethod
import datetime
import os
import re
from typing import Any, List, Union, Generator, Iterator, Tuple

import requests

from openwebui_token_tracking import TokenTracker
from openwebui_token_tracking.tracking import (
    TokenLimitExceededError,
    DailyTokenLimitExceededError,
    TotalTokenLimitExceededError,
)


def _time_to_midnight():
    now = datetime.datetime.now()
    remaining_hours = 24 - now.hour - 1
    remaining_minutes = 60 - now.minute
    remaining_seconds = 60 - now.second

    time_to_midnight = datetime.timedelta(
        hours=remaining_hours, minutes=remaining_minutes, seconds=remaining_seconds
    )
    return time_to_midnight


class RequestError(Exception):
    pass


class TokenCount:
    def __init__(self):
        self.prompt_tokens = 0
        self.response_tokens = 0


def _make_mermaid_error_message(type: str, message: str) -> str:
    """A helper function creating a boxed error message with Mermaid syntax"""
    header = " ".join(re.findall("[A-Z][^A-Z]*", type))
    header = header.replace('"', "'")

    return f"""```mermaid
flowchart TD
header["⚠️ {header.upper()} ⚠️"]
style header fill:#fff0f0,stroke:#f5dc69,stroke-width:4px,color:black,font-weight:bold,text-align:center
```
{message}
"""


class BaseTrackedPipe(ABC):
    """
    Base class for handling API requests to different AI model providers with token
    tracking.

    This class provides a common interface for making requests to AI model APIs
    while tracking token usage. It handles both streaming and non-streaming responses,
    and manages token usage limits.

    :param provider: The name of the AI provider.
    :type provider: str
    :param url: The base URL for the provider's API
    :type url: str
    """

    DATABASE_URL_ENV = "DATABASE_URL"
    MODEL_ID_PREFIX = "."

    def __init__(self, provider, url):
        self.provider = provider
        self.url = url
        self.type = "manifold"
        self.valves = self.Valves()
        self.token_tracker = TokenTracker(os.environ[BaseTrackedPipe.DATABASE_URL_ENV])

    def _check_limits(
        self, model_id: str, user: dict, sponsored_allowance_name: str = None
    ) -> bool:
        """
        Check if the user has exceeded their token usage limits.

        :param model_id: The ID of the model being accessed
        :type model_id: str
        :param user: User information dictionary
        :type user: dict
        :param sponsored_allowance_name: The name of the sponsored allowance
        :type sponsored_allowance_name: str, optional
        :raises TokenLimitExceededError: If user has exceeded their daily token limit
        :return: True if within limits
        :rtype: bool
        """
        if not self.token_tracker.is_paid(model_id):
            return True

        daily_credits_remaining, total_sponsored_credits_remaining = (
            self.token_tracker.remaining_credits(
                user, sponsored_allowance_name=sponsored_allowance_name
            )
        )

        if (
            total_sponsored_credits_remaining is not None
            and total_sponsored_credits_remaining <= 0
        ):
            raise TotalTokenLimitExceededError(
                f"The total credit limit for the sponsored allowance '{sponsored_allowance_name}' "
                "has been exceeded. Please contact the sponsor to add more credits, or choose "
                "a different model."
            )
        elif sponsored_allowance_name is not None and daily_credits_remaining <= 0:
            max_credits = self.token_tracker.max_credits(
                user, sponsored_allowance_name=sponsored_allowance_name
            )
            raise DailyTokenLimitExceededError(
                f"You've exceeded the daily usage limit ({max_credits} credits) for "
                f"the sponsored allowance '{sponsored_allowance_name}'.\nYour usage will reset in {_time_to_midnight()}.\n"
                "Until then, please use a different model not covered by this sponsored allowance."
            )

        elif daily_credits_remaining <= 0:
            free_models = [
                m
                for m in self.token_tracker.get_models()
                if not self.token_tracker.is_paid(m.id)
            ]
            max_credits = self.token_tracker.max_credits(user)

            raise DailyTokenLimitExceededError(
                f"You've exceeded the daily usage limit ({max_credits} credits) for the paid AI models. "
                f"Your usage will reset in {_time_to_midnight()}.\nIf you would like to obtain more credits, please reach out to rc@dartmouth.edu.\n"
                f"**IMPORTANT:** You can still use one of the free models (e.g., {free_models[0].name})."
            )

        return True

    @abstractmethod
    def _headers(self) -> dict:
        """
        Build the headers required for API requests.

        Must be implemented by provider-specific subclasses to include
        appropriate authentication and other required headers.

        :return: Dictionary of HTTP headers
        :rtype: dict
        """
        pass

    @abstractmethod
    def _payload(self, model_id, body) -> dict:
        """
        Build the payload for API requests.

        Must be implemented by provider-specific subclasses to format
        the request payload according to the provider's API specifications.

        :param model_id: The ID of the model being accessed
        :type model_id: str
        :param body: The request body containing the prompt and other parameters
        :type body: dict
        :return: Formatted payload for the API request
        :rtype: dict
        """
        pass

    @abstractmethod
    def _make_stream_request(
        self, headers, payload
    ) -> Tuple[TokenCount, Generator[Any, None, None]]:
        """
        Make a streaming request to the API.

        Must be implemented by provider-specific subclasses to handle
        streaming responses according to the provider's API specifications.

        :param headers: HTTP headers for the request
        :type headers: dict
        :param payload: Request payload
        :type payload: dict
        :return: Tuple containing the token count and a response generator
        :rtype: tuple[TokenCount, Generator[Any, None, None]]
        :raises RequestError: If the API request fails
        """
        pass

    @abstractmethod
    def _make_non_stream_request(self, headers, payload) -> Tuple[TokenCount, Any]:
        """
        Make a non-streaming request to the API.

        Must be implemented by provider-specific subclasses to handle
        non-streaming responses according to the provider's API specifications.

        :param headers: HTTP headers for the request
        :type headers: dict
        :param payload: Request payload
        :type payload: dict
        :return: Tuple containing the token count and the response
        :rtype: tuple[TokenCount, Any]
        :raises RequestError: If the API request fails
        """
        pass

    def get_models(self) -> List[dict]:
        """
        Get a list of available models for this provider.

        Retrieves models from the token tracker and formats them into a list
        of dictionaries containing model information.

        :return: List of dictionaries, each containing:
            - id: The model identifier
            - name: The display name of the model
        :rtype: list[dict]
        """
        models = [
            {
                "id": model.id,
                "name": model.name,
            }
            for model in self.token_tracker.get_models(provider=self.provider)
        ]
        return models

    def pipes(self) -> List[dict]:
        """
        Alias for get_models().

        :return: List of available models
        :rtype: list[dict]
        :see: :meth:`get_models`
        """
        return self.get_models()

    def pipe(
        self, body: dict, __user__: dict, __metadata__: dict
    ) -> Union[str, Generator, Iterator]:
        """
        Process an incoming request through the appropriate model pipeline.

        This method handles the high-level flow of processing a request:
        1. Checks token limits
        2. Prepares the request
        3. Makes the API call
        4. Handles the response

        :param body: The request body containing model selection and message
        :type body: dict
        :param __user__: User information for token tracking
        :type __user__: dict
        :param __metadata__: Additional metadata for the request
        :type __metadata__: dict
        :return: Either a string response or a generator for streaming responses
        :rtype: Union[str, Generator, Iterator]
        :raises TokenLimitExceededError: If user has exceeded their token limit
        :raises RequestError: If the API request fails
        """
        model = __metadata__["model"]
        sponsored_allowance_name = None
        # <v0.5.19 and v0.5.19+ keep the model info in different places:
        # For <v0.5.19, there is a key 'info' that holds the base model id.
        # For v0.5.19, the base model id is a key in model
        # For v0.5.20, the base model id is in the key 'info' again
        model_info = model.get("info", None)
        if model_info is None and "base_model_id" in model:
            model_info = model

        if model_info and model_info.get("base_model_id", None) is not None:
            # Check if Workspace Model name follows sponsored allowance
            # naming scheme and extract sponsored allowance name
            if "---" in model_info["id"]:
                sponsored_allowance_name, *_ = model_info["id"].split("---")
            model_id = model_info["base_model_id"].replace(
                self.provider + BaseTrackedPipe.MODEL_ID_PREFIX, "", 1
            )
        else:
            model_id = model["id"].replace(
                self.provider + BaseTrackedPipe.MODEL_ID_PREFIX, "", 1
            )

        try:
            # This used to raise an exception that is displayed in the UI as an error
            # message. At some point this broke upstream, so we will need to wait
            # until it gets fixed. Until then, we return just a message so the user
            # at least gets some feedback.
            self._check_limits(
                model_id=model_id,
                user=__user__,
                sponsored_allowance_name=sponsored_allowance_name,
            )
        except TokenLimitExceededError as e:
            return _make_mermaid_error_message(type=type(e).__name__, message=str(e))

        if self.valves.DEBUG:
            print("Incoming body:", str(body))

        headers = self._headers()

        payload = self._payload(model_id=model_id, body=body)

        if self.valves.DEBUG:
            print(f"{self.provider} API request:")
            print("  Model:", model_id)
            print("  Contents:", payload)
            print("  Stream:", body.get("stream"))

        try:
            if body.get("stream", False):
                return self.stream_response(
                    headers,
                    payload,
                    model_id,
                    __user__,
                    sponsored_allowance_name=sponsored_allowance_name,
                )
            else:
                return self.non_stream_response(
                    headers,
                    payload,
                    model_id,
                    __user__,
                    sponsored_allowance_name=sponsored_allowance_name,
                )
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return f"Error: Request failed: {e}"
        except RequestError as e:
            print(f"Error in pipe method: {e}")
            return f"Error: {e}"

    def stream_response(
        self, headers, payload, model_id, user, sponsored_allowance_name: str = None
    ):
        """
        Handle streaming responses from the API.

        Makes the streaming request and ensures token usage is logged
        after the response is complete.

        :param headers: HTTP headers for the request
        :type headers: dict
        :param payload: Request payload
        :type payload: dict
        :param model_id: The ID of the model being accessed
        :type model_id: str
        :param user: User information for token tracking
        :type user: dict
        :param sponsored_allowance_name: The name of the sponsored allowance
        :type sponsored_allowance_name: str, optional
        :yield: Response chunks from the API
        :raises RequestError: If the API request fails
        """
        try:
            tokens, response_generator = self._make_stream_request(headers, payload)

            chunks = []
            for chunk in response_generator:
                chunks.append(chunk)
                yield chunk

            self.token_tracker.log_token_usage(
                provider=self.provider,
                model_id=model_id,
                user=user,
                prompt_tokens=tokens.prompt_tokens,
                response_tokens=tokens.response_tokens,
                sponsored_allowance_name=sponsored_allowance_name,
            )

        except Exception as e:
            print(f"Error in stream_response: {e}")
            yield f"Error: {e}"

    def non_stream_response(
        self, headers, payload, model_id, user, sponsored_allowance_name: str = None
    ):
        """
        Handle non-streaming responses from the API.

        Makes the request and ensures token usage is logged
        after receiving the response.

        :param headers: HTTP headers for the request
        :type headers: dict
        :param payload: Request payload
        :type payload: dict
        :param model_id: The ID of the model being accessed
        :type model_id: str
        :param user: User information for token tracking
        :type user: dict
        :param sponsored_allowance_name: The name of the sponsored allowance
        :type sponsored_allowance_name: str, optional
        :return: The API response
        :rtype: Any
        :raises RequestError: If the API request fails
        """
        try:
            tokens, response = self._make_non_stream_request(headers, payload)

            self.token_tracker.log_token_usage(
                provider=self.provider,
                model_id=model_id,
                user=user,
                prompt_tokens=tokens.prompt_tokens,
                response_tokens=tokens.response_tokens,
                sponsored_allowance_name=sponsored_allowance_name,
            )

            return response

        except Exception as e:
            print(f"Error in non_stream_response: {e}")
            return f"Error: {e}"


if __name__ == "__main__":
    print(_time_to_midnight())
