# Open WebUI Token Tracking

[![Run tests](https://github.com/dartmouth/openwebui-token-tracking/actions/workflows/pytest.yml/badge.svg)](https://github.com/dartmouth/openwebui-token-tracking/actions/workflows/pytest.yml)

A library to support token tracking and limiting in [Open WebUI](https://openwebui.com/).


## Basic concept

The token tracking mechanism relies on [Open WebUI's pipes](https://docs.openwebui.com/pipelines/pipes/) feature.


```{warning}
You have to use pipes for all models whose token usage you want to track, even the ones that would normally be supported natively by Open WebUI, i.e., those with an OpenAI or Ollama-compatible API.

Fortunately, this library also offers the implementations of pipes for all major model providers!
```

In order to avoid differentiating between input and output tokens (which are usually priced quite differently), we use an abstraction from tokens called _credits_. Credits are determined by calculating the actual cost of the tokens. We recommend using a conversion rate of 1000 credits per 1 USD, but you can set this to whatever you prefer.

The library supports two kinds of allowances:

- Basic or group-based allowances:
  - A user gets a daily allowance of credits for all available models
  - The total allowance is the sum of a base allowance plus additional allowances through group memberships
  - Example:
    - Every user gets an allowance of 1000 credits per day.
    - Every user who is a member of the group "power users" gets an additional 2000 credits per day.
- Sponsored allowances:
  - These are allowances that a sponsor grants for specific models. Sponsored allowances have a daily credit limit (similar, but separate from the group-based daily limit) and a total credit limit.
  - A sponsored allowance relies on the setup of "thin" Workspace Models, one for each base model that the sponsored allowance should be valid for
  - Example:
    - The "AI Department" wants to grant its members additional credits for GPT-4o and Claude Sonnet.
    - To control cost, the total grant should not exceed 100000 credits.
    - To ensure equitable access for all team members, the daily limit within the sponsored allowance is set to 20 credits.
    - Once the sponsored allowance and the corresponding Workspace Models are set up, members of the AI Department see additional options in their model dropdown list: "AI Department - GPT 4o" and "AI Department - Claude Sonnet"
    - They can now use their separate allowance for these two models, in addition to the basic allowance for all other models (see above)

```{warning}
Since Workspace Models cannot be used as a base model for other Workspace Models, sponsored allowances cannot be used to build other Workspace Models!
```

The basic workflow for a general token allowance is:

- User attempts to send message to LLM via pipe.
- Token tracker checks if user has exceeded their token allowance.
  - If maximum token allowance has been hit or exceeded, no message is sent.
  - If tokens are remaining, message is sent.
- After the LLM's response is received, the consumed prompt and response tokens are recorded and charged to the user's account, and the sponsored allowance, if applicable.


```{hint}
Since we don't necessarily know the number of response tokens ahead of time, the message is still sent out as long as the user has at least one token credit remaining. Different logic can be implemented by subclassing `TokenTracker`, if you need it. And we welcome pull requests!
```

Some of the features offered by this library:

- 💸 An abstraction for tokens called "credits" to handle differently priced tokens depending on the model and the modality (input versus output)
- ⏱️ Tracked pipes for all major LLM providers
- 🛠️ A simple class hierarchy to implement your own logic for token tracking or limiting
- 🗂️ Database migration to automatically initialize all required tables in Open WebUI's database on a separate migration branch
- 💰 Limiting users' token usage by assigning them a basic token credit allowance
- 🏦 Token credit groups to easily assign additional allowances to multiple users
- 🎁 Sponsored allowances that only apply to certain models
- 🚀 A robust command-line interface to manage credit groups and sponsored allowances


## Installation

Install from PyPI using pip:

```
pip install openwebui-token-tracking
```

## Usage

To start tracking, you need to first initialize the system in your Open WebUI database. Then, you need to set up the pipes for the models you wish to track.
You can optionally create credit groups and assign users to them. Sponsored allowances require additional setup.

A command-line interface  is provided for convenient setup and management of the token tracking system. The pipes are set up through Open WebUI's interface (see below).

### Initial setup

Assuming Open WebUI's default env variable `DATABASE_URL` pointing to the database, you can go with all default settings:

```
owui-token-tracking init
```

This will:

1. Migrate the Open WebUI database to include the token tracking tables
2. Add pricing information for all major model providers currently supported by this library (as of the time of release)
3. Initialize a baseline daily token credit allowance for all users of 1000 credits (corresponds to 1 USD)

You can provide your own pricing information in this step by passing the option `--json` and the name of a JSON file with the following structure:

```json
[
    {
        "provider": "openai",
        "id": "gpt-4o-2024-08-06",
        "name": "GPT-4o (Cloud, Paid) 2024-08-06",
        "input_cost_credits": 3750,
        "per_input_tokens": 1000000,
        "output_cost_credits": 15000,
        "per_output_tokens": 1000000
    },
        {
        "provider": "anthropic",
        "id": "claude-3-5-haiku-20241022",
        "name": "Claude 3.5 Haiku (Cloud, Paid) 2024-10-22",
        "input_cost_credits": 1000,
        "per_input_tokens": 1000000,
        "output_cost_credits": 5000,
        "per_output_tokens": 1000000
    }
]
```


### Setting up a tracked pipe

Models need to be connected through pipes to inject the necessary tracking code. A base class for a tracked pipe is provided in `openwebui_token_tracking.pipes.BaseTrackedPipe`. We currently offer implementations for Anthropic, Google, Mistral, and OpenAI.

```{hint}
APIs that are fully OpenAI-compatible, i.e., they not only provide the same endpoints, but they also use the same input and output scheme, can use the OpenAI implementation of the tracked pipe. An example is [Text Generation Inference Messages API](https://huggingface.co/docs/text-generation-inference/en/messages_api).
```

To set up the tracked pipe, add a Function to Open WebUI. **Important:** The function name needs to match the value of `provider` in the pricing table (case-insensitive, e.g., `Anthropic`). You can then define the tracked pipe like so:

```python
"""
title: Anthropic Pipe
author: Simon Stone
requirements: openwebui-token-tracking
version: 0.1.0
"""

from openwebui_token_tracking.pipes.anthropic import AnthropicTrackedPipe

Pipe = AnthropicTrackedPipe

```

Each pipe offers Valves to enter an API key or an API base url. Make sure to fill in the required values before activating the pipe.

### Base allowance

You can find the base allowance in Open WebUI's database in the table `token_tracking_base_settings`. By default, it is initialized with 1000 credits.

### Credit groups

You can manage credit groups through `openwebui-token-tracking`'s command-line interface. For example, to create a credit group:

```
owui-token-tracking credit-group create "my credit group" 2000 "my credit group granting an additional 2000 credits"
```

You can then add users to the credit group:

```
owui-token-tracking credit-group add-user my_user_id 'my credit group'
```

```{hint}
To find a user's ID in the Open WebUI database, you can also use the CLI:

    owui-token-tracking user find --name my_user_name

```


### Sponsored allowances
... coming soon


## Documentation

Documentation is available [online](https://dartmouth.github.io/openwebui-token-tracking/).

To build the documentation locally:

```bash
pip install -e ".[docs]"
sphinx-build -b html docs/source/ docs/build/html
```