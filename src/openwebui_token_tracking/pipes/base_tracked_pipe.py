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
import os
from typing import Any, List, Union, Generator, Iterator, Tuple

import requests

from openwebui_token_tracking import TokenTracker


class TokenLimitExceededError(Exception):
    pass


class RequestError(Exception):
    pass


class TokenCount:
    def __init__(self):
        self.prompt_tokens = 0
        self.response_tokens = 0


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

    def _check_limits(self, model_id: str, user: dict) -> bool:
        """
        Check if the user has exceeded their token usage limits.

        :param model_id: The ID of the model being accessed
        :type model_id: str
        :param user: User information dictionary
        :type user: dict
        :raises TokenLimitExceededError: If user has exceeded their daily token limit
        :return: True if within limits
        :rtype: bool
        """
        if (
            self.token_tracker.is_paid(model_id)
            and self.token_tracker.remaining_credits(user) <= 0
        ):
            free_models = [
                m
                for m in self.token_tracker.get_models()
                if not self.token_tracker.is_paid(m.id)
            ]
            raise TokenLimitExceededError(
                f"""You've exceeded the daily usage limit ({self.token_tracker.max_credits(user)} credits) for the paid AI models.
                    IMPORTANT: Click the "New Chat" button and select one of the free models (ex. {free_models[0].name}) to start a new chat session.
                    """
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

    def pipe(self, body: dict, __user__: dict) -> Union[str, Generator, Iterator]:
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
        :return: Either a string response or a generator for streaming responses
        :rtype: Union[str, Generator, Iterator]
        :raises TokenLimitExceededError: If user has exceeded their token limit
        :raises RequestError: If the API request fails
        """
        model_id = body.get("model").replace(
            self.provider + BaseTrackedPipe.MODEL_ID_PREFIX, "", 1
        )

        try:
            # This used to raise an exception that is displayed in the UI as an error
            # message. At some point this broke upstream, so we will need to wait
            # until it gets fixed. Until then, we return just a message so the user
            # at least gets some feedback.
            self._check_limits(model_id=model_id, user=__user__)
        except TokenLimitExceededError as e:
            return str(e)

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
                return self.stream_response(headers, payload, model_id, __user__)
            else:
                return self.non_stream_response(headers, payload, model_id, __user__)
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return f"Error: Request failed: {e}"
        except RequestError as e:
            print(f"Error in pipe method: {e}")
            return f"Error: {e}"

    def stream_response(self, headers, payload, model_id, user):
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
            )

        except Exception as e:
            print(f"Error in stream_response: {e}")
            yield f"Error: {e}"

    def non_stream_response(self, headers, payload, model_id, user):
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
            )

            return response

        except Exception as e:
            print(f"Error in non_stream_response: {e}")
            return f"Error: {e}"
