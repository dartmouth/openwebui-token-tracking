"""
title: Show credit balance
author: Simon Stone
version: 0.0.1
icon_url: data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+CjwhLS0gQ3JlYXRlZCB3aXRoIElua3NjYXBlIChodHRwOi8vd3d3Lmlua3NjYXBlLm9yZy8pIC0tPgoKPHN2ZwogICB3aWR0aD0iMjRtbSIKICAgaGVpZ2h0PSIyNG1tIgogICB2aWV3Qm94PSIwIDAgMjQgMjQiCiAgIHZlcnNpb249IjEuMSIKICAgaWQ9InN2ZzUiCiAgIHhtbDpzcGFjZT0icHJlc2VydmUiCiAgIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgeG1sbnM6c3ZnPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnMKICAgICBpZD0iZGVmczIiIC8+PHRleHQKICAgICB4bWw6c3BhY2U9InByZXNlcnZlIgogICAgIHN0eWxlPSJmb250LXNpemU6My4yMTgzN3B4O2ZvbnQtZmFtaWx5OlZpcmdpbDstaW5rc2NhcGUtZm9udC1zcGVjaWZpY2F0aW9uOlZpcmdpbDtmaWxsOiM2NzY3Njc7ZmlsbC1vcGFjaXR5OjE7c3Ryb2tlLXdpZHRoOjAuNjA4NTQxO3N0cm9rZS1saW5lY2FwOnJvdW5kO3N0cm9rZS1saW5lam9pbjpyb3VuZDtzdHJva2UtZGFzaGFycmF5Om5vbmUiCiAgICAgeD0iMTYuNTE3MTkxIgogICAgIHk9Ii0xLjk1NjE0MTUiCiAgICAgaWQ9InRleHQ0NTciCiAgICAgdHJhbnNmb3JtPSJzY2FsZSgwLjk5MzQyNjk4LDEuMDA2NjE2NSkiPjx0c3BhbgogICAgICAgaWQ9InRzcGFuNDU1IgogICAgICAgc3R5bGU9ImZpbGw6IzY3Njc2NztmaWxsLW9wYWNpdHk6MTtzdHJva2Utd2lkdGg6MC42MDg1NDE7c3Ryb2tlLWRhc2hhcnJheTpub25lIgogICAgICAgeD0iMTYuNTE3MTkxIgogICAgICAgeT0iLTEuOTU2MTQxNSIgLz48L3RleHQ+PGcKICAgICBpZD0iZzE4NjkxIgogICAgIHRyYW5zZm9ybT0ibWF0cml4KDAuODI4MTEzOTgsMCwwLDAuODMxMDI1NzMsMi4zNDAyODg3LDIuMzcwOTM0MSkiCiAgICAgc3R5bGU9InN0cm9rZS13aWR0aDoxLjIwNTQ1Ij48dGV4dAogICAgICAgeG1sOnNwYWNlPSJwcmVzZXJ2ZSIKICAgICAgIHN0eWxlPSJmb250LXNpemU6MTQuMjQ1cHg7Zm9udC1mYW1pbHk6VmlyZ2lsOy1pbmtzY2FwZS1mb250LXNwZWNpZmljYXRpb246VmlyZ2lsO2ZpbGw6IzY3Njc2NztmaWxsLW9wYWNpdHk6MTtzdHJva2U6bm9uZTtzdHJva2Utd2lkdGg6MC43MzM1NjM7c3Ryb2tlLWxpbmVjYXA6cm91bmQ7c3Ryb2tlLWxpbmVqb2luOnJvdW5kO3N0cm9rZS1kYXNoYXJyYXk6bm9uZTtzdHJva2Utb3BhY2l0eToxIgogICAgICAgeD0iMTIuODE3OTE5IgogICAgICAgeT0iMTkuNTEwNDg5IgogICAgICAgaWQ9InRleHQxMTcxIgogICAgICAgdHJhbnNmb3JtPSJzY2FsZSgwLjk5MzQyNjk5LDEuMDA2NjE2NSkiPjx0c3BhbgogICAgICAgICBpZD0idHNwYW4xMTY5IgogICAgICAgICBzdHlsZT0iZm9udC1zdHlsZTpub3JtYWw7Zm9udC12YXJpYW50Om5vcm1hbDtmb250LXdlaWdodDpib2xkO2ZvbnQtc3RyZXRjaDpub3JtYWw7Zm9udC1mYW1pbHk6J0RhcnRtb3V0aCBSdXppY2thJzstaW5rc2NhcGUtZm9udC1zcGVjaWZpY2F0aW9uOidEYXJ0bW91dGggUnV6aWNrYSBCb2xkJztmaWxsOiM2NzY3Njc7ZmlsbC1vcGFjaXR5OjE7c3Ryb2tlOm5vbmU7c3Ryb2tlLXdpZHRoOjAuNzMzNTYzO3N0cm9rZS1kYXNoYXJyYXk6bm9uZTtzdHJva2Utb3BhY2l0eToxIgogICAgICAgICB4PSIxMi44MTc5MTkiCiAgICAgICAgIHk9IjE5LjUxMDQ4OSI+JDwvdHNwYW4+PC90ZXh0PjxyZWN0CiAgICAgICBzdHlsZT0iZmlsbDpub25lO2ZpbGwtb3BhY2l0eToxO3N0cm9rZTojNjc2NzY3O3N0cm9rZS13aWR0aDoxLjkxMzY0O3N0cm9rZS1saW5lY2FwOmJ1dHQ7c3Ryb2tlLWxpbmVqb2luOnJvdW5kO3N0cm9rZS1kYXNoYXJyYXk6bm9uZTtzdHJva2Utb3BhY2l0eToxIgogICAgICAgaWQ9InJlY3QyMDYxIgogICAgICAgd2lkdGg9IjE3LjU4OTg1MSIKICAgICAgIGhlaWdodD0iMjIuMTE0MjA2IgogICAgICAgeD0iMy4yMDUwNzQxIgogICAgICAgeT0iMC45NDI4OTYzNyIgLz48cGF0aAogICAgICAgc3R5bGU9ImZpbGw6bm9uZTtmaWxsLW9wYWNpdHk6MTtzdHJva2U6IzY3Njc2NztzdHJva2Utd2lkdGg6MS45MTM2NDtzdHJva2UtbGluZWNhcDpidXR0O3N0cm9rZS1saW5lam9pbjpyb3VuZDtzdHJva2UtZGFzaGFycmF5Om5vbmU7c3Ryb2tlLW9wYWNpdHk6MSIKICAgICAgIGQ9Ik0gNi40NjI0NTM1LDMuODU4NDUxMSBIIDE3LjUzNzU0NiIKICAgICAgIGlkPSJwYXRoMjEyNiIgLz48cGF0aAogICAgICAgc3R5bGU9ImZpbGw6bm9uZTtmaWxsLW9wYWNpdHk6MTtzdHJva2U6IzY3Njc2NztzdHJva2Utd2lkdGg6MS45MTM2NDtzdHJva2UtbGluZWNhcDpidXR0O3N0cm9rZS1saW5lam9pbjpyb3VuZDtzdHJva2UtZGFzaGFycmF5Om5vbmU7c3Ryb2tlLW9wYWNpdHk6MSIKICAgICAgIGQ9Ik0gNi40NjI0NTM1LDcuMTMyMTU4OSBIIDE3LjUzNzU0NiIKICAgICAgIGlkPSJwYXRoMjEyNi01IiAvPjwvZz48L3N2Zz4K
"""

from typing import Optional

import os
import logging

from openwebui_token_tracking.tracking import TokenTracker
from openwebui_token_tracking.pipes.base_tracked_pipe import _time_to_midnight
import time


class CreditBalance:
    """
    Show credit balance for the current user.

    This class provides functionality to display the remaining daily credits for a user.
    It queries the token tracking database to retrieve credit information and emits an event
    with the credit balance details.

    **Note:** To include the icon for the action, the Function definition in Open WebUI
    needs to include the following header:::

        \"\"\"
        icon_url: data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+CjwhLS0gQ3JlYXRlZCB3aXRoIElua3NjYXBlIChodHRwOi8vd3d3Lmlua3NjYXBlLm9yZy8pIC0tPgoKPHN2ZwogICB3aWR0aD0iMjRtbSIKICAgaGVpZ2h0PSIyNG1tIgogICB2aWV3Qm94PSIwIDAgMjQgMjQiCiAgIHZlcnNpb249IjEuMSIKICAgaWQ9InN2ZzUiCiAgIHhtbDpzcGFjZT0icHJlc2VydmUiCiAgIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgeG1sbnM6c3ZnPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnMKICAgICBpZD0iZGVmczIiIC8+PHRleHQKICAgICB4bWw6c3BhY2U9InByZXNlcnZlIgogICAgIHN0eWxlPSJmb250LXNpemU6My4yMTgzN3B4O2ZvbnQtZmFtaWx5OlZpcmdpbDstaW5rc2NhcGUtZm9udC1zcGVjaWZpY2F0aW9uOlZpcmdpbDtmaWxsOiM2NzY3Njc7ZmlsbC1vcGFjaXR5OjE7c3Ryb2tlLXdpZHRoOjAuNjA4NTQxO3N0cm9rZS1saW5lY2FwOnJvdW5kO3N0cm9rZS1saW5lam9pbjpyb3VuZDtzdHJva2UtZGFzaGFycmF5Om5vbmUiCiAgICAgeD0iMTYuNTE3MTkxIgogICAgIHk9Ii0xLjk1NjE0MTUiCiAgICAgaWQ9InRleHQ0NTciCiAgICAgdHJhbnNmb3JtPSJzY2FsZSgwLjk5MzQyNjk4LDEuMDA2NjE2NSkiPjx0c3BhbgogICAgICAgaWQ9InRzcGFuNDU1IgogICAgICAgc3R5bGU9ImZpbGw6IzY3Njc2NztmaWxsLW9wYWNpdHk6MTtzdHJva2Utd2lkdGg6MC42MDg1NDE7c3Ryb2tlLWRhc2hhcnJheTpub25lIgogICAgICAgeD0iMTYuNTE3MTkxIgogICAgICAgeT0iLTEuOTU2MTQxNSIgLz48L3RleHQ+PGcKICAgICBpZD0iZzE4NjkxIgogICAgIHRyYW5zZm9ybT0ibWF0cml4KDAuODI4MTEzOTgsMCwwLDAuODMxMDI1NzMsMi4zNDAyODg3LDIuMzcwOTM0MSkiCiAgICAgc3R5bGU9InN0cm9rZS13aWR0aDoxLjIwNTQ1Ij48dGV4dAogICAgICAgeG1sOnNwYWNlPSJwcmVzZXJ2ZSIKICAgICAgIHN0eWxlPSJmb250LXNpemU6MTQuMjQ1cHg7Zm9udC1mYW1pbHk6VmlyZ2lsOy1pbmtzY2FwZS1mb250LXNwZWNpZmljYXRpb246VmlyZ2lsO2ZpbGw6IzY3Njc2NztmaWxsLW9wYWNpdHk6MTtzdHJva2U6bm9uZTtzdHJva2Utd2lkdGg6MC43MzM1NjM7c3Ryb2tlLWxpbmVjYXA6cm91bmQ7c3Ryb2tlLWxpbmVqb2luOnJvdW5kO3N0cm9rZS1kYXNoYXJyYXk6bm9uZTtzdHJva2Utb3BhY2l0eToxIgogICAgICAgeD0iMTIuODE3OTE5IgogICAgICAgeT0iMTkuNTEwNDg5IgogICAgICAgaWQ9InRleHQxMTcxIgogICAgICAgdHJhbnNmb3JtPSJzY2FsZSgwLjk5MzQyNjk5LDEuMDA2NjE2NSkiPjx0c3BhbgogICAgICAgICBpZD0idHNwYW4xMTY5IgogICAgICAgICBzdHlsZT0iZm9udC1zdHlsZTpub3JtYWw7Zm9udC12YXJpYW50Om5vcm1hbDtmb250LXdlaWdodDpib2xkO2ZvbnQtc3RyZXRjaDpub3JtYWw7Zm9udC1mYW1pbHk6J0RhcnRtb3V0aCBSdXppY2thJzstaW5rc2NhcGUtZm9udC1zcGVjaWZpY2F0aW9uOidEYXJ0bW91dGggUnV6aWNrYSBCb2xkJztmaWxsOiM2NzY3Njc7ZmlsbC1vcGFjaXR5OjE7c3Ryb2tlOm5vbmU7c3Ryb2tlLXdpZHRoOjAuNzMzNTYzO3N0cm9rZS1kYXNoYXJyYXk6bm9uZTtzdHJva2Utb3BhY2l0eToxIgogICAgICAgICB4PSIxMi44MTc5MTkiCiAgICAgICAgIHk9IjE5LjUxMDQ4OSI+JDwvdHNwYW4+PC90ZXh0PjxyZWN0CiAgICAgICBzdHlsZT0iZmlsbDpub25lO2ZpbGwtb3BhY2l0eToxO3N0cm9rZTojNjc2NzY3O3N0cm9rZS13aWR0aDoxLjkxMzY0O3N0cm9rZS1saW5lY2FwOmJ1dHQ7c3Ryb2tlLWxpbmVqb2luOnJvdW5kO3N0cm9rZS1kYXNoYXJyYXk6bm9uZTtzdHJva2Utb3BhY2l0eToxIgogICAgICAgaWQ9InJlY3QyMDYxIgogICAgICAgd2lkdGg9IjE3LjU4OTg1MSIKICAgICAgIGhlaWdodD0iMjIuMTE0MjA2IgogICAgICAgeD0iMy4yMDUwNzQxIgogICAgICAgeT0iMC45NDI4OTYzNyIgLz48cGF0aAogICAgICAgc3R5bGU9ImZpbGw6bm9uZTtmaWxsLW9wYWNpdHk6MTtzdHJva2U6IzY3Njc2NztzdHJva2Utd2lkdGg6MS45MTM2NDtzdHJva2UtbGluZWNhcDpidXR0O3N0cm9rZS1saW5lam9pbjpyb3VuZDtzdHJva2UtZGFzaGFycmF5Om5vbmU7c3Ryb2tlLW9wYWNpdHk6MSIKICAgICAgIGQ9Ik0gNi40NjI0NTM1LDMuODU4NDUxMSBIIDE3LjUzNzU0NiIKICAgICAgIGlkPSJwYXRoMjEyNiIgLz48cGF0aAogICAgICAgc3R5bGU9ImZpbGw6bm9uZTtmaWxsLW9wYWNpdHk6MTtzdHJva2U6IzY3Njc2NztzdHJva2Utd2lkdGg6MS45MTM2NDtzdHJva2UtbGluZWNhcDpidXR0O3N0cm9rZS1saW5lam9pbjpyb3VuZDtzdHJva2UtZGFzaGFycmF5Om5vbmU7c3Ryb2tlLW9wYWNpdHk6MSIKICAgICAgIGQ9Ik0gNi40NjI0NTM1LDcuMTMyMTU4OSBIIDE3LjUzNzU0NiIKICAgICAgIGlkPSJwYXRoMjEyNi01IiAvPjwvZz48L3N2Zz4K
        \"\"\"

    :param DATABASE_URL_ENV: Environment variable name for the database connection string.
    :type DATABASE_URL_ENV: str

    Attributes:
        valves (Valves): An instance of the Valves inner class.
        is_visible (bool): Flag indicating whether the credit balance is currently visible.

    Methods:
        action: Retrieves and displays the user's credit balance.
    """
    DATABASE_URL_ENV = "DATABASE_URL"

    def __init__(self):
        self.valves = self.Valves()
        self.is_visible = False

    async def action(
        self,
        body: dict,
        __user__=None,
        __metadata__=None,
        __event_emitter__=None,
        __event_call__=None,
    ) -> Optional[dict]:

        await __event_emitter__(
            {
                "type": "status",
                "action": "credit_balance",
                "data": {"description": "Getting credit balance...", "done": False},
            }
        )
        time.sleep(0.5)

        logger = logging.getLogger(__name__)

        tracker_instance = TokenTracker(db_url=os.environ[self.DATABASE_URL_ENV])
        credits_left, _ = tracker_instance.remaining_credits(user=__user__)
        max_credits = tracker_instance.max_credits(user=__user__)

        stats = " | ".join(
            [
                f"Remaining daily credits: {credits_left} / {max_credits}"
                f" (resets in {_time_to_midnight()}).",
            ]
        )

        await __event_emitter__(
            {
                "type": "status",
                "action": "credit_balance",
                "data": {"description": stats, "done": True},
            }
        )
        self.is_visible = True
        logger.debug("credit_balance: %s %s", __user__, stats)
        return body
