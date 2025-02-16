# Open WebUI Token Tracking

[![Run tests](https://github.com/dartmouth/openwebui-token-tracking/actions/workflows/pytest.yml/badge.svg)](https://github.com/dartmouth/openwebui-token-tracking/actions/workflows/pytest.yml)

A library to support token tracking and limiting in Open WebUI.


## Installation

Install from PyPI using pip:

```
pip install openwebui-token-tracking
```

## Usage

A command-line interface  is provided for convenient setup and management of the token tracking system.

### Initial setup


Assuming Open WebUI's default env variable `DATABASE_URL` pointing to the database:
```
owui-token-tracking database migrate
```

Init base settings

```
owui-token-tracking init
```


### Manage model pricing

```
owui-token-tracking pricing add
```

### Manage credit groups

...