import os
import requests
import json
from pydantic import BaseModel, Field
from typing import List, Generator, Any, Tuple
from open_webui.utils.misc import pop_system_message
from .base_tracked_pipe import BaseTrackedPipe, RequestError, TokenCount


class AnthropicTrackedPipe(BaseTrackedPipe):
    """
    Anthropic-specific implementation of the BaseTrackedPipe for handling API requests
    to Anthropic's chat completion endpoints with token tracking.

    This class handles authentication, request formatting, and response processing
    specific to the Anthropic API, including support for image processing and
    multi-modal messages.
    """

    class Valves(BaseModel):
        """Configuration parameters for Anthropic API connections."""
        ANTHROPIC_API_KEY: str = Field(
            default="",
            description="API key for authenticating requests to the Anthropic API.",
        )
        DEBUG: bool = Field(default=False)

    def __init__(self):
        """
        Initialize the Anthropic pipe with API endpoint and configuration.
        Sets up image size limits and loads API key from environment.
        """
        super().__init__(
            provider="anthropic", url="https://api.anthropic.com/v1/messages"
        )
        self.valves = self.Valves(
            **{"ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY", "")}
        )
        self.MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB per image

    def _headers(self) -> dict:
        """
        Build headers for Anthropic API requests.

        :return: Dictionary containing authorization and content-type headers
        :rtype: dict
        """
        return {
            "x-api-key": self.valves.ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

    def _payload(self, model_id: str, body: dict) -> dict:
        """
        Format the request payload for Anthropic API.

        :param model_id: The ID of the model to use
        :type model_id: str
        :param body: The request body containing messages and parameters
        :type body: dict
        :return: Formatted payload for the API request
        :rtype: dict
        """
        system_message, messages = pop_system_message(body["messages"])
        processed_messages = self._process_messages(messages)

        return {
            "model": model_id,
            "messages": processed_messages,
            "max_tokens": body.get("max_tokens", 4096),
            "temperature": body.get("temperature", 0.8),
            "top_k": body.get("top_k", 40),
            "top_p": body.get("top_p", 0.9),
            "stop_sequences": body.get("stop", []),
            **({"system": str(system_message)} if system_message else {}),
            "stream": body.get("stream", False),
        }

    def _make_stream_request(
        self, headers: dict, payload: dict
    ) -> Tuple[int, int, Generator[Any, None, None]]:
        """
        Make a streaming request to the Anthropic API.

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
            with requests.post(
                self.url, headers=headers, json=payload, stream=True, timeout=(3.05, 60)
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
                                if data["type"] == "content_block_start":
                                    yield data["content_block"]["text"]
                                elif data["type"] == "content_block_delta":
                                    yield data["delta"]["text"]
                                elif data["type"] == "message_stop":
                                    break
                                elif data["type"] == "message_start":
                                    tokens.prompt_tokens = data["message"]["usage"][
                                        "input_tokens"
                                    ]
                                elif data["type"] == "message_delta":
                                    tokens.response_tokens = data["usage"][
                                        "output_tokens"
                                    ]
                                elif data["type"] == "message":
                                    for content in data.get("content", []):
                                        if content["type"] == "text":
                                            yield content["text"]
                            except json.JSONDecodeError:
                                print(f"Failed to parse JSON: {line}")
                            except KeyError as e:
                                print(f"Unexpected data structure: {e}")
                                print(f"Full data: {data}")

        return tokens, generate_stream()

    def _make_non_stream_request(
        self, headers: dict, payload: dict
    ) -> Tuple[int, int, Any]:
        """
        Make a non-streaming request to the Anthropic API.

        :param headers: HTTP headers for the request
        :type headers: dict
        :param payload: Request payload
        :type payload: dict
        :return: Tuple of (TokenCount, response data)
        :rtype: Tuple[TokenCount, Any]
        :raises RequestError: If the API request fails
        """
        response = requests.post(
            self.url, headers=headers, json=payload, timeout=(3.05, 60)
        )
        if response.status_code != 200:
            raise RequestError(f"HTTP Error {response.status_code}: {response.text}")

        res = response.json()
        tokens = TokenCount()
        tokens.prompt_tokens = res["usage"]["input_tokens"]
        tokens.response_tokens = res["usage"]["output_tokens"]
        response_text = (
            res["content"][0]["text"] if "content" in res and res["content"] else ""
        )

        return tokens, response_text

    def _process_messages(self, messages: List[dict]) -> List[dict]:
        processed_messages = []
        image_count = 0
        total_image_size = 0

        for message in messages:
            processed_content = []
            if isinstance(message.get("content"), list):
                for item in message["content"]:
                    if item["type"] == "text":
                        processed_content.append({"type": "text", "text": item["text"]})
                    elif item["type"] == "image_url":
                        if image_count >= 100:
                            raise ValueError(
                                "Maximum of 100 images per API call exceeded"
                            )
                        processed_image = self._process_image(item)
                        processed_content.append(processed_image)
                        if processed_image["source"]["type"] == "base64":
                            image_size = len(processed_image["source"]["data"]) * 3 / 4
                            total_image_size += image_size
                            if total_image_size > 100 * 1024 * 1024:
                                raise ValueError(
                                    "Total size of images exceeds 100 MB limit"
                                )
                        image_count += 1
            else:
                processed_content = [
                    {"type": "text", "text": message.get("content", "")}
                ]

            processed_messages.append(
                {"role": message["role"], "content": processed_content}
            )

        return processed_messages

    def _process_image(self, image_data: dict) -> dict:
        """Process image data with size validation."""
        if image_data["image_url"]["url"].startswith("data:image"):
            mime_type, base64_data = image_data["image_url"]["url"].split(",", 1)
            media_type = mime_type.split(":")[1].split(";")[0]
            image_size = len(base64_data) * 3 / 4
            if image_size > self.MAX_IMAGE_SIZE:
                raise ValueError(
                    f"Image size exceeds 5MB limit: {image_size / (1024 * 1024):.2f}MB"
                )
            return {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": base64_data,
                },
            }
        else:
            url = image_data["image_url"]["url"]
            response = requests.head(url, allow_redirects=True)
            content_length = int(response.headers.get("content-length", 0))
            if content_length > self.MAX_IMAGE_SIZE:
                raise ValueError(
                    f"Image at URL exceeds 5MB limit: {content_length / (1024 * 1024):.2f}MB"
                )
            return {
                "type": "image",
                "source": {"type": "url", "url": url},
            }
