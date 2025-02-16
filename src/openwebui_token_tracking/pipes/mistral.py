"""
Mistral AI API integration with token tracking.

This module provides a tracked pipe implementation for the Mistral AI API,
handling both streaming and non-streaming responses while tracking token usage.
"""

import os
import json
import requests
import time
from typing import Any, Dict, Generator, Tuple
from pydantic import BaseModel, Field
from .base_tracked_pipe import BaseTrackedPipe, TokenCount, RequestError


class MistralTrackedPipe(BaseTrackedPipe):
    """
    Tracked pipe implementation for Mistral AI's API.

    This class handles API requests to Mistral AI models while tracking token usage.
    It supports both streaming and non-streaming responses, and implements
    rate limiting handling with automatic retries.
    """

    class Valves(BaseModel):
        """
        Configuration parameters for the Mistral pipe.

        :param MISTRAL_API_KEY: API key for authenticating with Mistral's API
        :type MISTRAL_API_KEY: str
        :param DEBUG: Enable debug logging
        :type DEBUG: bool
        """

        MISTRAL_API_KEY: str = Field(default="")
        DEBUG: bool = Field(default=False)

    def __init__(self):
        """Initialize the Mistral pipe with API configuration."""
        super().__init__(
            provider="mistral", url="https://api.mistral.ai/v1/chat/completions"
        )
        self.valves = self.Valves(
            **{"MISTRAL_API_KEY": os.getenv("MISTRAL_API_KEY", "")}
        )

    def _debug(self, message: str) -> None:
        """
        Print debug messages if debug mode is enabled.

        :param message: The message to print
        :type message: str
        """
        if self.valves.DEBUG:
            print(message)

    def _headers(self) -> Dict[str, str]:
        """
        Get headers for API requests.

        :return: Dictionary of required headers including authentication
        :rtype: Dict[str, str]
        :raises ValueError: If MISTRAL_API_KEY is not set
        """
        if not self.valves.MISTRAL_API_KEY:
            raise ValueError(
                "MISTRAL_API_KEY is not set. Please configure the environment variable."
            )
        return {
            "Authorization": f"Bearer {self.valves.MISTRAL_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _payload(self, model_id: str, body: dict) -> dict:
        """
        Prepare the payload for API requests.

        :param model_id: The ID of the model being accessed
        :type model_id: str
        :param body: The request body containing messages and parameters
        :type body: dict
        :return: Formatted payload for the API request
        :rtype: dict
        """
        return {
            "model": model_id,
            "messages": body["messages"],
            "stream": body.get("stream", False),
        }

    def _make_stream_request(
        self,
        headers: dict,
        payload: dict,
    ) -> Tuple[TokenCount, Generator[Any, None, None]]:
        """
        Make a streaming request to the Mistral API.

        Handles streaming responses.

        :param headers: HTTP headers for the request
        :type headers: dict
        :param payload: Request payload containing messages and configuration
        :type payload: dict
        :return: Tuple of TokenCount object and response generator
        :rtype: Tuple[TokenCount, Generator[Any, None, None]]
        :raises RequestError: If the API request fails after all retries
        """
        tokens = TokenCount()

        def generate_stream():
            try:
                response = requests.post(
                    self.url, json=payload, headers=headers, stream=True
                )
                response.raise_for_status()

                for line in response.iter_lines():
                    if line:
                        try:
                            line_data = line.decode("utf-8").lstrip("data: ")
                            event = json.loads(line_data)
                            self._debug(f"Received stream event: {event}")

                            delta_content = (
                                event.get("choices", [{}])[0]
                                .get("delta", {})
                                .get("content")
                            )
                            if delta_content:
                                yield delta_content

                            if (
                                event.get("choices", [{}])[0].get("finish_reason")
                                == "stop"
                            ):
                                tokens.prompt_tokens = event["usage"]["prompt_tokens"]
                                tokens.response_tokens = event["usage"][
                                    "completion_tokens"
                                ]
                                break

                        except json.JSONDecodeError:
                            self._debug(f"Failed to decode stream line: {line}")
                            continue

            except requests.RequestException as e:
                raise RequestError(f"Stream request failed: {e}")

        return tokens, generate_stream()

    def _make_non_stream_request(
        self, headers: dict, payload: dict
    ) -> Tuple[TokenCount, Any]:
        """
        Make a non-streaming request to the Mistral API.

        Handles regular responses.

        :param headers: HTTP headers for the request
        :type headers: dict
        :param payload: Request payload containing messages and configuration
        :type payload: dict
        :return: Tuple of TokenCount object and response text
        :rtype: Tuple[TokenCount, Any]
        :raises RequestError: If the API request fails after all retries
        """
        tokens = TokenCount()

        try:
            response = requests.post(self.url, json=payload, headers=headers)
            data = self._handle_response(response)

            tokens.prompt_tokens = data["usage"]["prompt_tokens"]
            tokens.response_tokens = data["usage"]["completion_tokens"]

            return tokens, data["choices"][0]["message"]["content"]

        except requests.RequestException as e:
            raise RequestError(f"Request failed: {e}")

    def _handle_response(self, response: requests.Response) -> dict:
        """
        Handle and parse API responses.

        :param response: Response object from the requests library
        :type response: requests.Response
        :return: Parsed JSON response
        :rtype: dict
        :raises RequestError: If response status is not 200 or JSON is invalid
        """
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            self._debug(f"HTTPError: {e.response.text}")
            raise RequestError(f"HTTP Error: {e}")
        except ValueError as e:
            self._debug(f"Invalid JSON response: {response.text}")
            raise RequestError(f"Invalid JSON response: {e}")
