import os
import requests
import json
from pydantic import BaseModel, Field
from typing import List, Union, Generator, Iterator
from open_webui.utils.misc import pop_system_message

from openwebui_token_tracking import TokenTracker
from openwebui_token_tracking.models import DEFAULT_MODEL_PRICING

PROVIDER = "openai"


class Pipe:
    class Valves(BaseModel):
        OPENAI_API_KEY: str = Field(
            default="",
            description="API key for authenticating requests to the OpenAI API.",
        )
        DEBUG: bool = Field(default=False)

    def __init__(self):
        print(f"__init__:{__name__}")
        self.type = "manifold"
        self.valves = self.Valves()
        self.token_tracker = TokenTracker(os.environ["DATABASE_URL"])

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

        payload = {**body, "model": model_name}

        headers = {
            "Authorization": f"Bearer {self.valves.OPENAI_API_KEY}",
            "content-type": "application/json",
        }

        url = "https://api.openai.com/v1/chat/completions"

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

    def stream_response(self, url, headers, payload, model_id, user):
        try:
            prompt_tokens = 0
            response_tokens = 0
            with requests.post(
                url,
                headers=headers,
                json={**payload, "stream_options": {"include_usage": True}},
                stream=True,
                timeout=(3.05, 60),
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

            self.log_token_usage(
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
            self.log_token_usage(
                model_id,
                user,
                res["usage"]["prompt_tokens"],
                res["usage"]["completion_tokens"],
            )
            return res
        except requests.exceptions.RequestException as e:
            print(f"Failed non-stream request: {e}")
            return f"Error: {e}"
