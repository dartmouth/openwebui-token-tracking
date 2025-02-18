# Open WebUI Token Tracking

[![Run tests](https://github.com/dartmouth/openwebui-token-tracking/actions/workflows/pytest.yml/badge.svg)](https://github.com/dartmouth/openwebui-token-tracking/actions/workflows/pytest.yml)

A library to support token tracking and limiting in [Open WebUI](https://openwebui.com/).


## Basic concept

The token tracking mechanism relies on [Open WebUI's pipes](https://docs.openwebui.com/pipelines/pipes/) feature.


```{warning}
You have to use pipes for all models whose token usage you want to track, even the ones that would normally be supported natively by Open WebUI, i.e., those with an OpenAI or Ollama-compatible API.

Fortunately, this library also offers the implementations of pipes for all major model providers!
```

The basic workflow is:

- User attempts to send message to LLM via pipe
- Token tracker checks if user has exceeded their token allowance
  - If maximum token allowance has been hit or exceeded, no message is sent
  - If tokens are remaining, message is sent
- After the LLM's response is received, the consumed prompt and response tokens are recorded and charged to the user's account


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
- 🚀 A robust command-line interface to manage credit groups


## Installation

Install from PyPI using pip:

```
pip install openwebui-token-tracking
```

## Usage

To get tracking, you need to first initialize the system in your Open WebUI database. Then you need to set up the pipes for the models you wish to track.
You can optionally create credit groups and assign users to them.

A command-line interface  is provided for convenient setup and management of the token tracking system. The pipes are set up through Open WebUI's interface (see below).

### Initial setup

Assuming Open WebUI's default env variable `DATABASE_URL` pointing to the database, you can go with all default settings:

```
owui-token-tracking init
```

This will:

1. Migrate the Open WebUI database to include the token tracking tables
2. Add pricing information for all major model providers currently supported by this library (as of the time of release)
3. Initialize a baseline token credit allowance for all users of 1000 credits (corresponds to 1 USD)

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




### Manage credit groups

...

## Documentation

Documentation is available [online](https://dartmouth.github.io/openwebui-token-tracking/).

To build the documentation locally:

```bash
pip install -e ".[docs]"
sphinx-build -b html docs/source/ docs/build/html
```