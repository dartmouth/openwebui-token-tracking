"""
Google Gemini API integration with token tracking.
This module provides a tracked pipe implementation for the Google Gemini API,
handling both streaming and non-streaming responses while tracking token usage.
"""

import os
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from open_webui.utils.misc import pop_system_message
from pydantic import BaseModel, Field

from typing import Any, Generator, Tuple
from .base_tracked_pipe import BaseTrackedPipe, TokenCount


class GoogleTrackedPipe(BaseTrackedPipe):
    """
    Tracked pipe implementation for Google's Gemini API.

    This class handles API requests to Google's Gemini models while tracking token usage.
    It supports both streaming and non-streaming responses, and handles multimodal inputs
    including text and images.

    :param provider: The provider name, set to "google_genai"
    :type provider: str
    :param url: The base URL for the Gemini API
    :type url: str
    """

    class Valves(BaseModel):
        """
        Configuration parameters for the Google Gemini pipe.

        :param GOOGLE_API_KEY: API key for authenticating with Google's API
        :type GOOGLE_API_KEY: str
        :param USE_PERMISSIVE_SAFETY: Whether to use permissive safety settings
        :type USE_PERMISSIVE_SAFETY: bool
        :param DEBUG: Enable debug logging
        :type DEBUG: bool
        """

        GOOGLE_API_KEY: str = Field(default="")
        USE_PERMISSIVE_SAFETY: bool = Field(default=False)
        DEBUG: bool = Field(default=False)

    def __init__(self):
        """Initialize the Google Gemini pipe with API configuration."""
        super().__init__(
            provider="google_genai",
            url="https://generativelanguage.googleapis.com/v1/models",
        )
        self.valves = self.Valves(
            **{
                "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY", ""),
                "USE_PERMISSIVE_SAFETY": False,
            }
        )
        # Repeat configure every time the pipe runs because the valve might change
        genai.configure(api_key=self.valves.GOOGLE_API_KEY)

    def _headers(self) -> dict:
        """
        Get headers for API requests.

        :return: Empty dict as headers are handled by the Google API client
        :rtype: dict
        """
        return {}  # Not needed for Google API client library

    def _payload(self, model_id: str, body: dict) -> dict:
        """
        Prepare the payload for API requests.

        Processes messages and configurations into the format expected by the Gemini API.

        :param model_id: The ID of the model being accessed
        :type model_id: str
        :param body: The request body containing messages and parameters
        :type body: dict
        :return: Formatted payload for the API request
        :rtype: dict
        """
        messages = body["messages"]
        system_message, messages = pop_system_message(messages)

        contents = []
        for message in messages:
            if message["role"] != "system":
                if isinstance(message.get("content"), list):
                    parts = []
                    for content in message["content"]:
                        if content["type"] == "text":
                            parts.append({"text": content["text"]})
                        elif content["type"] == "image_url":
                            image_url = content["image_url"]["url"]
                            if image_url.startswith("data:image"):
                                image_data = image_url.split(",")[1]
                                parts.append(
                                    {
                                        "inline_data": {
                                            "mime_type": "image/jpeg",
                                            "data": image_data,
                                        }
                                    }
                                )
                            else:
                                parts.append({"image_url": image_url})
                    contents.append({"role": message["role"], "parts": parts})
                else:
                    contents.append(
                        {
                            "role": "user" if message["role"] == "user" else "model",
                            "parts": [{"text": message["content"]}],
                        }
                    )

        if system_message:
            contents.insert(
                0,
                {"role": "user", "parts": [{"text": f"System: {system_message}"}]},
            )

        generation_config = GenerationConfig(
            temperature=body.get("temperature", 0.7),
            top_p=body.get("top_p", 0.9),
            top_k=body.get("top_k", 40),
            max_output_tokens=body.get("max_tokens", 8192),
            stop_sequences=body.get("stop", []),
        )

        safety_settings = {}
        if self.valves.USE_PERMISSIVE_SAFETY:
            safety_settings = {
                genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
            }

        return {
            "model_id": model_id,
            "contents": contents,
            "generation_config": generation_config,
            "safety_settings": safety_settings,
            "system_message": system_message,
        }

    def _make_stream_request(
        self, headers: dict, payload: dict
    ) -> Tuple[TokenCount, Generator[Any, None, None]]:
        """
        Make a streaming request to the Gemini API.

        :param headers: HTTP headers (unused for Gemini API)
        :type headers: dict
        :param payload: Request payload containing messages and configuration
        :type payload: dict
        :return: Tuple of TokenCount object and response generator
        :rtype: Tuple[TokenCount, Generator[Any, None, None]]
        """
        model_id = payload.pop("model_id")
        if "gemini-1.5" in model_id:
            model = genai.GenerativeModel(
                model_name=model_id, system_instruction=payload["system_message"]
            )
        else:
            model = genai.GenerativeModel(model_name=model_id)

        tokens = TokenCount()

        def generate_stream():
            response = model.generate_content(
                payload["contents"],
                generation_config=payload["generation_config"],
                safety_settings=payload["safety_settings"],
                stream=True,
            )

            for chunk in response:
                if chunk.text:
                    yield chunk.text

            tokens.prompt_tokens = chunk.usage_metadata.prompt_token_count
            tokens.response_tokens = chunk.usage_metadata.candidates_token_count

        return tokens, generate_stream()

    def _make_non_stream_request(
        self, headers: dict, payload: dict
    ) -> Tuple[TokenCount, Any]:
        """
        Make a non-streaming request to the Gemini API.

        :param headers: HTTP headers (unused for Gemini API)
        :type headers: dict
        :param payload: Request payload containing messages and configuration
        :type payload: dict
        :return: Tuple of TokenCount object and response text
        :rtype: Tuple[TokenCount, Any]
        """
        model_id = payload.pop("model_id")
        if "gemini-1.5" in model_id:
            model = genai.GenerativeModel(
                model_name=model_id, system_instruction=payload["system_message"]
            )
        else:
            model = genai.GenerativeModel(model_name=model_id)

        response = model.generate_content(
            payload["contents"],
            generation_config=payload["generation_config"],
            safety_settings=payload["safety_settings"],
            stream=False,
        )

        tokens = TokenCount()
        tokens.prompt_tokens = response.usage_metadata.prompt_token_count
        tokens.response_tokens = response.usage_metadata.candidates_token_count

        return tokens, response.text

    def pipe(self, body, __user__, __metadata__):
        genai.configure(api_key=self.valves.GOOGLE_API_KEY)
        return super().pipe(body, __user__, __metadata__)
