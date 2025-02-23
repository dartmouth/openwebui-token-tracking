import os
import requests
import json
from pydantic import BaseModel, Field
from typing import Generator, Any, Tuple
from .base_tracked_pipe import BaseTrackedPipe, RequestError, TokenCount


class OpenAITrackedPipe(BaseTrackedPipe):
    """
    OpenAI-specific implementation of the BaseTrackedPipe for handling API requests
    to OpenAI's chat completion endpoints with token tracking.

    Note that providers that are fully compliant with OpenAI's API specification
    (both regarding the request and the response structure), can also be used with
    this pipe by setting the respective values in the Valves.

    This class handles authentication, request formatting, and response processing
    specific to the OpenAI API while leveraging the base class's token tracking
    functionality.
    """

    class Valves(BaseModel):
        """Configuration parameters for OpenAI (compatible) API connections."""
        API_KEY: str = Field(
            default="",
            description="API key for authenticating requests to the OpenAI (or compatible) API.",
        )
        API_BASE_URL: str = Field(
            default="https://api.openai.com/v1",
            description="Base URL of the OpenAI (or compatible) API ",
        )
        PROVIDER: str = Field(
            default="openai", description="Name of the model provider."
        )
        DEBUG: bool = Field(default=False)

    def __init__(self):
        """Initialize the OpenAI pipe with API endpoint and configuration."""
        self.valves = self.Valves(**{"API_KEY": os.getenv("OPENAI_API_KEY", "")})
        super().__init__(
            # Provider and URL are read from Valves for each request
            provider="",
            url="",
        )

    def _headers(self) -> dict:
        """
        Build headers for OpenAI (compatible) API requests.

        :return: Dictionary containing authorization and content-type headers
        :rtype: dict
        """
        return {
            "Authorization": f"Bearer {self.valves.API_KEY}",
            "content-type": "application/json",
        }

    def _payload(self, model_id: str, body: dict) -> dict:
        """
        Format the request payload for OpenAI (compatible) API.

        :param model_id: The ID of the model to use
        :type model_id: str
        :param body: The request body containing messages and parameters
        :type body: dict
        :return: Formatted payload for the API request
        :rtype: dict
        """
        return {**body, "model": model_id}

    def _make_stream_request(
        self, headers: dict, payload: dict
    ) -> Tuple[TokenCount, Generator[Any, None, None]]:
        """
        Make a streaming request to the OpenAI (compatible) API.

        :param headers: HTTP headers for the request
        :type headers: dict
        :param payload: Request payload
        :type payload: dict
        :return: Tuple of (TokenCount, response generator)
        :rtype: Tuple[TokenCount, Generator[Any, None, None]]
        :raises RequestError: If the API request fails
        """
        tokens = TokenCount()

        def generate_stream():
            self.url = f"{self.valves.API_BASE_URL.rstrip('/')}/chat/completions"
            stream_payload = {**payload, "stream_options": {"include_usage": True}}

            with requests.post(
                url=self.url,
                headers=headers,
                json=stream_payload,
                stream=True,
                timeout=(3.05, 60),
            ) as response:
                if response.status_code != 200:
                    raise RequestError(
                        f"HTTP Error {response.status_code}: {response.text}"
                    )

                for line in response.iter_lines():
                    if line:
                        line = line.decode("utf-8")
                        if line.startswith("data: "):
                            try:
                                data = json.loads(line[6:])
                                if data.get("usage", None):
                                    tokens.prompt_tokens = data["usage"].get(
                                        "prompt_tokens"
                                    )
                                    tokens.response_tokens = data["usage"].get(
                                        "completion_tokens"
                                    )
                            except json.JSONDecodeError:
                                print(f"Failed to parse JSON: {line}")
                            except KeyError as e:
                                print(f"Unexpected data structure: {e}")
                                print(f"Full data: {data}")
                    yield line

        return tokens, generate_stream()

    def _make_non_stream_request(
        self, headers: dict, payload: dict
    ) -> Tuple[TokenCount, Any]:
        """
        Make a non-streaming request to the OpenAI (compatible) API.

        :param headers: HTTP headers for the request
        :type headers: dict
        :param payload: Request payload
        :type payload: dict
        :return: Tuple of (TokenCount, response data)
        :rtype: Tuple[int, int, Any]
        :raises RequestError: If the API request fails
        """
        self.url = f"{self.valves.API_BASE_URL.rstrip('/')}/chat/completions"
        response = requests.post(
            self.url, headers=headers, json=payload, timeout=(3.05, 60)
        )

        if response.status_code != 200:
            raise RequestError(f"HTTP Error {response.status_code}: {response.text}")

        res = response.json()
        tokens = TokenCount()
        tokens.prompt_tokens = res["usage"]["prompt_tokens"]
        tokens.response_tokens = res["usage"]["completion_tokens"]

        return tokens, res

    def pipes(self):
        self.provider = self.valves.PROVIDER
        self.url = f"{self.valves.API_BASE_URL.rstrip('/')}/v1/chat/completions"
        return super().pipes()

    def pipe(self, body, __user__, __metadata__):
        self.provider = self.valves.PROVIDER
        self.url = f"{self.valves.API_BASE_URL.rstrip('/')}/v1/chat/completions"
        return super().pipe(body, __user__, __metadata__)
