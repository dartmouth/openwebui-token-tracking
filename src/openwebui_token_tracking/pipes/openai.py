import os
import requests
import json
from pydantic import BaseModel, Field
from typing import Generator, Any, Tuple
from open_webui.utils.misc import pop_system_message
from .base_tracked_pipe import BaseTrackedPipe, RequestError


class OpenAITrackedPipe(BaseTrackedPipe):
    """
    OpenAI-specific implementation of the BaseTrackedPipe for handling API requests
    to OpenAI's chat completion endpoints with token tracking.

    This class handles authentication, request formatting, and response processing
    specific to the OpenAI API while leveraging the base class's token tracking
    functionality.
    """

    class Valves(BaseModel):
        """Configuration parameters for OpenAI API connections."""
        OPENAI_API_KEY: str = Field(
            default="",
            description="API key for authenticating requests to the OpenAI API.",
        )
        DEBUG: bool = Field(default=False)

    def __init__(self):
        """Initialize the OpenAI pipe with API endpoint and configuration."""
        super().__init__("openai", "https://api.openai.com/v1/chat/completions")
        self.valves = self.Valves(**{"OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", "")})

    def _headers(self) -> dict:
        """
        Build headers for OpenAI API requests.

        :return: Dictionary containing authorization and content-type headers
        :rtype: dict
        """
        return {
            "Authorization": f"Bearer {self.valves.OPENAI_API_KEY}",
            "content-type": "application/json",
        }

    def _payload(self, model_id: str, body: dict) -> dict:
        """
        Format the request payload for OpenAI API.

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
    ) -> Tuple[int, int, Generator[Any, None, None]]:
        """
        Make a streaming request to the OpenAI API.

        :param headers: HTTP headers for the request
        :type headers: dict
        :param payload: Request payload
        :type payload: dict
        :return: Tuple of (prompt tokens, completion tokens, response generator)
        :rtype: Tuple[int, int, Generator[Any, None, None]]
        :raises RequestError: If the API request fails
        """
        prompt_tokens = 0
        response_tokens = 0

        def generate_stream():
            nonlocal prompt_tokens, response_tokens

            stream_payload = {**payload, "stream_options": {"include_usage": True}}

            with requests.post(
                self.url,
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
                                    prompt_tokens = data["usage"].get("prompt_tokens")
                                    response_tokens = data["usage"].get(
                                        "completion_tokens"
                                    )
                            except json.JSONDecodeError:
                                print(f"Failed to parse JSON: {line}")
                            except KeyError as e:
                                print(f"Unexpected data structure: {e}")
                                print(f"Full data: {data}")
                        yield line

        return prompt_tokens, response_tokens, generate_stream()

    def _make_non_stream_request(
        self, headers: dict, payload: dict
    ) -> Tuple[int, int, Any]:
        """
        Make a non-streaming request to the OpenAI API.

        :param headers: HTTP headers for the request
        :type headers: dict
        :param payload: Request payload
        :type payload: dict
        :return: Tuple of (prompt tokens, completion tokens, response data)
        :rtype: Tuple[int, int, Any]
        :raises RequestError: If the API request fails
        """
        response = requests.post(
            self.url, headers=headers, json=payload, timeout=(3.05, 60)
        )

        if response.status_code != 200:
            raise RequestError(f"HTTP Error {response.status_code}: {response.text}")

        res = response.json()
        prompt_tokens = res["usage"]["prompt_tokens"]
        response_tokens = res["usage"]["completion_tokens"]

        return prompt_tokens, response_tokens, res
