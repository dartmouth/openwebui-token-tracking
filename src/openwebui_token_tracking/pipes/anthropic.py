import os
import requests
import json
from pydantic import BaseModel, Field
from typing import List, Union, Generator, Iterator
from open_webui.utils.misc import pop_system_message

from openwebui_token_tracking import TokenTracker
from openwebui_token_tracking.models import DEFAULT_MODEL_PRICING

PROVIDER = "anthropic"


class TrackedPipe:
    class Valves(BaseModel):
        ANTHROPIC_API_KEY: str = Field(
            default="",
            description="API key for authenticating requests to the Anthropic API.",
        )
        DEBUG: bool = Field(default=False)

    def __init__(self):
        print(f"__init__:{__name__}")
        self.type = "manifold"
        self.valves = self.Valves(
            **{"ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY", "")}
        )
        self.token_tracker = TokenTracker(os.environ["DATABASE_URL"])
        self.MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB per image

    def get_models(self):
        models = [
            {
                "id": model.id.replace(PROVIDER + ".", "", 1),
                "name": model.name,
            }
            for model in DEFAULT_MODEL_PRICING
            if model.id.startswith(PROVIDER)
        ]
        return models

    def pipes(self) -> List[dict]:
        return self.get_models()

    def pipe(self, body: dict, __user__: dict) -> Union[str, Generator, Iterator]:
        system_message, messages = pop_system_message(body["messages"])
        model_id = body.get("model")
        model_name = model_id.replace(PROVIDER + ".", "", 1)

        if self.valves.DEBUG:
            print("Incoming body:", str(body))

        if (
            self.token_tracker.is_paid(model_id)
            and self.token_tracker.remaining_credits(__user__) <= 0
        ):
            # This used to raise an exception that is displayed in the UI as an error message.
            # At some point this broke upstream, so we will need to wait until it gets fixed.
            # Until then, we return just a message so the user at least gets some feedback.
            free_models = [
                m for m in DEFAULT_MODEL_PRICING if not self.token_tracker.is_paid(m.id)
            ]
            return f"""You've exceeded the daily usage limit ({self.token_tracker.max_credits(__user__)} credits) for the paid AI models.
                    IMPORTANT: Click the "New Chat" button and select one of the free models (ex. {free_models[0].name}) to start a new chat session.
                    """

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

                        processed_image = self.process_image(item)
                        processed_content.append(processed_image)

                        # Track total size for base64 images
                        if processed_image["source"]["type"] == "base64":
                            image_size = len(processed_image["source"]["data"]) * 3 / 4
                            total_image_size += image_size
                            if (
                                total_image_size > 100 * 1024 * 1024
                            ):  # 100MB total limit
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

        # Ensure the system_message is coerced to a string
        payload = {
            "model": model_name,
            "messages": processed_messages,
            "max_tokens": body.get("max_tokens", 4096),
            "temperature": body.get("temperature", 0.8),
            "top_k": body.get("top_k", 40),
            "top_p": body.get("top_p", 0.9),
            "stop_sequences": body.get("stop", []),
            **({"system": str(system_message)} if system_message else {}),
            "stream": body.get("stream", False),
        }

        headers = {
            "x-api-key": self.valves.ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        url = "https://api.anthropic.com/v1/messages"

        if self.valves.DEBUG:
            print(f"{PROVIDER} API request:")
            print("  Model:", model_id)
            print("  Contents:", payload)
            print("  Stream:", body.get("stream"))

        try:
            if body.get("stream", False):
                return self.stream_response(url, headers, payload, model_id, __user__)
            else:
                return self.non_stream_response(
                    url, headers, payload, model_id, __user__
                )
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return f"Error: Request failed: {e}"
        except Exception as e:
            print(f"Error in pipe method: {e}")
            return f"Error: {e}"

    def process_image(self, image_data):
        """Process image data with size validation."""
        if image_data["image_url"]["url"].startswith("data:image"):
            mime_type, base64_data = image_data["image_url"]["url"].split(",", 1)
            media_type = mime_type.split(":")[1].split(";")[0]

            # Check base64 image size
            image_size = len(base64_data) * 3 / 4  # Convert base64 size to bytes
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
            # For URL images, perform size check after fetching
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

    def stream_response(self, url, headers, payload, model_id, user):
        try:
            prompt_tokens = 0
            response_tokens = 0
            with requests.post(
                url, headers=headers, json=payload, stream=True, timeout=(3.05, 60)
            ) as response:
                if response.status_code != 200:
                    raise Exception(
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
                                    prompt_tokens = data["message"]["usage"][
                                        "input_tokens"
                                    ]
                                elif data["type"] == "message_delta":
                                    response_tokens = data["usage"]["output_tokens"]
                                elif data["type"] == "message":
                                    for content in data.get("content", []):
                                        if content["type"] == "text":
                                            yield content["text"]

                            except json.JSONDecodeError:
                                print(f"Failed to parse JSON: {line}")
                            except KeyError as e:
                                print(f"Unexpected data structure: {e}")
                                print(f"Full data: {data}")

            self.token_tracker.log_token_usage(
                model_id,
                user,
                prompt_tokens,
                response_tokens,
            )
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            yield f"Error: Request failed: {e}"
        except Exception as e:
            print(f"General error in stream_response method: {e}")
            yield f"Error: {e}"

    def non_stream_response(self, url, headers, payload, model_id, user):
        try:
            response = requests.post(
                url, headers=headers, json=payload, timeout=(3.05, 60)
            )
            if response.status_code != 200:
                raise Exception(f"HTTP Error {response.status_code}: {response.text}")

            res = response.json()
            self.token_tracker.log_token_usage(
                model_id,
                user,
                res["usage"]["input_tokens"],
                res["usage"]["output_tokens"],
            )
            return (
                res["content"][0]["text"] if "content" in res and res["content"] else ""
            )
        except requests.exceptions.RequestException as e:
            print(f"Failed non-stream request: {e}")
            return f"Error: {e}"
