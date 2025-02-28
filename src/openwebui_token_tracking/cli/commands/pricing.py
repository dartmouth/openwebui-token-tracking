import click
import json
from openwebui_token_tracking import models
import openwebui_token_tracking.model_pricing


@click.group(name="pricing")
def pricing():
    """Manage pricing structures."""
    pass


@pricing.command(name="list")
@click.option("--database-url", envvar="DATABASE_URL")
@click.option("--provider", help="Only return models of this provider, e.g., 'openai'")
def list_pricing(database_url: str, provider: str | None):
    """List all model pricing in the database.

    DATABASE-URL is expected to be in SQLAlchemy format.
    """
    models = openwebui_token_tracking.model_pricing.list_model_pricing(
        database_url=database_url, provider=provider
    )
    for model in models:
        click.echo(model)


@pricing.command(name="get")
@click.argument("model-id")
@click.option("--database-url", envvar="DATABASE_URL")
@click.option("--provider", help="Provider of the model, e.g., 'openai'")
def get_pricing(database_url: str, model_id: str, provider: str | None):
    """Get pricing for a specific model.

    DATABASE-URL is expected to be in SQLAlchemy format.
    MODEL-ID is the model identifier (e.g., 'gpt-4').

    If --provider is not specified, returns all models with matching ID
    across providers.
    """
    models = openwebui_token_tracking.model_pricing.get_model_pricing(
        database_url=database_url,
        model_id=model_id,
        provider=provider,
    )
    for model in models:
        click.echo(model)


@pricing.command(name="update")
@click.argument("model-id", required=False)
@click.option(
    "--database-url",
    envvar="DATABASE_URL",
    required=True,
    help="Database URL in SQLAlchemy format",
)
@click.option("--provider", help="Provider of the model, e.g., 'openai'")
@click.option(
    "--json",
    "json_file",
    type=click.File("r"),
    help="Read update data from a JSON file",
)
@click.option(
    "--name",
    help="Human-readable model name, e.g., 'GPT-4o (Cloud, Paid) 2024-08-06'",
)
@click.option(
    "--input-cost-credits",
    type=int,
    help="Cost in credits for PER-INPUT-TOKENS input tokens",
)
@click.option(
    "--per-input-tokens",
    type=int,
    help="Number of input tokens per INPUT-COST-CREDITS",
)
@click.option(
    "--output-cost-credits",
    type=int,
    help="Cost in credits for PER-OUTPUT-TOKENS output tokens",
)
@click.option(
    "--per-output-tokens",
    type=int,
    help="Number of output tokens per OUTPUT-COST-CREDITS",
)
def update_pricing(
    database_url: str,
    model_id: str | None,
    provider: str | None,
    json_file: click.File | None,
    name: str | None,
    input_cost_credits: int | None,
    per_input_tokens: int | None,
    output_cost_credits: int | None,
    per_output_tokens: int | None,
):
    """Update pricing for one or more models.

    Updates can be specified in two ways:

    1. Single model update: Provide MODEL-ID, --provider, and field values
       Example: pricing update gpt-4 --provider openai --name "New Name"

    2. Bulk update via JSON: Use --json without MODEL-ID
       Example: pricing update --json updates.json

       The JSON file should contain an array of objects with this schema:
       {
           "id": "string",           # Required
           "provider": "string",     # Required
           "name": "string",
           "input_cost_credits": integer,
           "per_input_tokens": integer,
           "output_cost_credits": integer,
           "per_output_tokens": integer
       }
    """
    if json_file:
        if model_id or any(
            [
                name,
                input_cost_credits,
                per_input_tokens,
                output_cost_credits,
                per_output_tokens,
            ]
        ):
            raise click.UsageError(
                "Cannot combine --json with individual field updates"
            )
        try:
            updates_list = json.load(json_file)
            if not isinstance(updates_list, list):
                updates_list = [updates_list]

            # Validate and process each update
            for update in updates_list:
                if not isinstance(update, dict):
                    raise click.UsageError("Each update must be an object")
                if "id" not in update:
                    raise click.UsageError("Each update must include 'id'")
                if "provider" not in update:
                    raise click.UsageError("Each update must include 'provider'")

                model_id = update.pop("id")
                provider = update.pop("provider")

                allowed_fields = {
                    "name",
                    "input_cost_credits",
                    "per_input_tokens",
                    "output_cost_credits",
                    "per_output_tokens",
                }
                invalid_fields = set(update.keys()) - allowed_fields
                if invalid_fields:
                    raise click.UsageError(
                        f"Invalid update fields: {', '.join(invalid_fields)}\n"
                        f"Allowed fields are: {', '.join(allowed_fields)}"
                    )

                print(database_url, model_id, provider, update)
                openwebui_token_tracking.model_pricing.update_model_pricing(
                    database_url=database_url,
                    model_id=model_id,
                    provider=provider,
                    updates=update,
                )

        except json.JSONDecodeError as e:
            raise click.UsageError(f"Invalid JSON file: {e}")
    else:
        if not model_id:
            raise click.UsageError("MODEL_ID is required when not using --json")
        if not provider:
            raise click.UsageError("--provider is required when not using --json")

        # Build update dict with only provided values
        updates = {}
        if name is not None:
            updates["name"] = name
        if input_cost_credits is not None:
            updates["input_cost_credits"] = input_cost_credits
        if per_input_tokens is not None:
            updates["per_input_tokens"] = per_input_tokens
        if output_cost_credits is not None:
            updates["output_cost_credits"] = output_cost_credits
        if per_output_tokens is not None:
            updates["per_output_tokens"] = per_output_tokens

        if not updates:
            raise click.UsageError("No updates specified")

        return openwebui_token_tracking.model_pricing.update_model_pricing(
            database_url=database_url,
            model_id=model_id,
            provider=provider,
            updates=updates,
        )


@pricing.command(name="upsert")
@click.argument("model-id", required=False)
@click.option(
    "--database-url",
    envvar="DATABASE_URL",
    required=True,
    help="Database URL in SQLAlchemy format",
)
@click.option("--provider", help="Provider of the model, e.g., 'openai'")
@click.option(
    "--json",
    "json_file",
    type=click.File("r"),
    help="Read model data from a JSON file",
)
@click.option(
    "--name",
    help="Human-readable model name, e.g., 'GPT-4 (Cloud, Paid) 2024-08-06'",
)
@click.option(
    "--input-cost-credits",
    type=int,
    help="Cost in credits for PER-INPUT-TOKENS input tokens",
)
@click.option(
    "--per-input-tokens",
    type=int,
    help="Number of input tokens per INPUT-COST-CREDITS",
)
@click.option(
    "--output-cost-credits",
    type=int,
    help="Cost in credits for PER-OUTPUT-TOKENS output tokens",
)
@click.option(
    "--per-output-tokens",
    type=int,
    help="Number of output tokens per OUTPUT-COST-CREDITS",
)
def upsert_pricing(
    database_url: str,
    model_id: str | None,
    provider: str | None,
    json_file: click.File | None,
    name: str | None,
    input_cost_credits: int | None,
    per_input_tokens: int | None,
    output_cost_credits: int | None,
    per_output_tokens: int | None,
):
    """Create or update pricing for one or more models.

    Models can be specified in two ways:
    1. Single model: Provide MODEL-ID, --provider, and all required fields
       Example: pricing upsert gpt-4 --provider openai --name "GPT-4" --input-cost-credits 8
               --per-input-tokens 1000 --output-cost-credits 16 --per-output-tokens 1000

    2. Bulk upsert via JSON: Use --json without MODEL-ID
       Example: pricing upsert --json models.json
       The JSON file should contain an array of objects with this schema:
       {
           "id": "string",           # Required
           "provider": "string",     # Required
           "name": "string",         # Required
           "input_cost_credits": integer,  # Required
           "per_input_tokens": integer,    # Required
           "output_cost_credits": integer, # Required
           "per_output_tokens": integer    # Required
       }
    """
    if json_file:
        if model_id or provider:
            raise click.UsageError(
                "Cannot combine --json with individual model parameters"
            )
        try:
            models_list = json.load(json_file)
            if not isinstance(models_list, list):
                models_list = [models_list]

            required_fields = {
                "id",
                "provider",
                "name",
                "input_cost_credits",
                "per_input_tokens",
                "output_cost_credits",
                "per_output_tokens",
            }

            # Validate and process each model
            for model in models_list:
                if not isinstance(model, dict):
                    raise click.UsageError("Each entry must be an object")

                missing_fields = required_fields - set(model.keys())
                if missing_fields:
                    raise click.UsageError(
                        f"Missing required fields: {', '.join(missing_fields)}"
                    )

                invalid_fields = set(model.keys()) - required_fields
                if invalid_fields:
                    raise click.UsageError(
                        f"Invalid fields: {', '.join(invalid_fields)}"
                    )

                model_id = model.pop("id")
                provider = model.pop("provider")

                openwebui_token_tracking.model_pricing.upsert_model_pricing(
                    database_url=database_url,
                    provider=provider,
                    model_id=model_id,
                    **model,
                )

        except json.JSONDecodeError as e:
            raise click.UsageError(f"Invalid JSON file: {e}")
    else:
        if not model_id:
            raise click.UsageError("MODEL-ID is required when not using --json")
        if not provider:
            raise click.UsageError("--provider is required when not using --json")

        # Check that all required fields are provided
        required_fields = {
            "name": name,
            "input_cost_credits": input_cost_credits,
            "per_input_tokens": per_input_tokens,
            "output_cost_credits": output_cost_credits,
            "per_output_tokens": per_output_tokens,
        }
        missing_fields = [
            field for field, value in required_fields.items() if value is None
        ]

        if missing_fields:
            raise click.UsageError(
                f"Missing required fields: {', '.join(missing_fields)}\n"
                "All fields are required when upserting a model"
            )

        return openwebui_token_tracking.model_pricing.upsert_model_pricing(
            database_url=database_url,
            provider=provider,
            model_id=model_id,
            name=name,
            input_cost_credits=input_cost_credits,
            per_input_tokens=per_input_tokens,
            output_cost_credits=output_cost_credits,
            per_output_tokens=per_output_tokens,
        )


@pricing.command(name="delete")
@click.argument("model-id")
@click.option("--database-url", envvar="DATABASE_URL")
@click.option("--provider", help="Provider of the model, e.g., 'openai'")
@click.option(
    "-y",
    "--yes",
    "auto_confirm",
    is_flag=True,
    help="Automatically answer yes to confirmation prompt",
)
def delete_pricing(
    database_url: str, model_id: str, provider: str | None, auto_confirm: bool
):
    """Delete pricing for a specific model.

    DATABASE-URL is expected to be in SQLAlchemy format.
    MODEL-ID is the model identifier (e.g., 'gpt-4').

    If --provider is not specified, will prompt for confirmation before
    deleting all models with matching ID across providers.
    """
    models = openwebui_token_tracking.model_pricing.get_model_pricing(
        database_url=database_url,
        model_id=model_id,
        provider=provider,
    )

    if not models:
        click.echo("No matching models found")
        return

    if not auto_confirm:
        click.echo("Will delete the following models:")
        for model in models:
            click.echo(f"  {model}")
        if not click.confirm("Continue?"):
            click.echo("Aborted")
            return

    return openwebui_token_tracking.model_pricing.delete_model_pricing(
        database_url=database_url,
        model_id=model_id,
        provider=provider,
    )


@pricing.command(name="add")
@click.option("--database-url", envvar="DATABASE_URL")
@click.option(
    "--json",
    "json_file",
    type=click.File("r"),
    help="Read multiple models from a JSON file",
)
@click.option("--provider", help="Provider of the model, e.g., 'openai'")
@click.option(
    "--id",
    help="Model ID according to the model provider's API spec, "
    "e.g., 'gpt-4o-2024-08-06'",
)
@click.option(
    "--name",
    help="Human-readable model name, e.g., 'GPT-4o (Cloud, Paid) 2024-08-06'",
)
@click.option(
    "--input-cost-credits",
    type=int,
    help="Cost in credits for PER-INPUT-TOKENS input tokens",
)
@click.option(
    "--per-input-tokens",
    type=int,
    default=1_000_000,
    help="Number of input tokens per INPUT-COST-CREDITS",
)
@click.option(
    "--output-cost-credits",
    type=int,
    help="Cost in credits for PER-OUTPUT-TOKENS output tokens",
)
@click.option(
    "--per-output-tokens",
    type=int,
    default=1_000_000,
    help="Number of output tokens per OUTPUT-COST-CREDITS",
)
def add_pricing(
    database_url: str,
    json_file: click.File | None,
    provider: str | None,
    id: str | None,
    name: str | None,
    input_cost_credits: int | None,
    output_cost_credits: int | None,
    per_input_tokens: int = 1_000_000,
    per_output_tokens: int = 1_000_000,
):
    """Add pricing for one or more models to the database at DATABASE-URL.

    DATABASE-URL is expected to be in SQLAlchemy format.

    There are two ways to use this command:

    1. Single model: Provide all model details via options
       Example: pricing add --provider openai --id gpt-4 ...

    2. Bulk add: Provide a JSON file with --json
       Example: pricing add --json models.json

       The JSON file should contain an array of objects with the schema:
       {
           "provider": "string",
           "id": "string",
           "name": "string",
           "input_cost_credits": integer,
           "per_input_tokens": integer,
           "output_cost_credits": integer,
           "per_output_tokens": integer
       }
    """
    if json_file:
        model_pricing_data = json.load(json_file)
        model_pricing = [models.ModelPricingSchema(**m) for m in model_pricing_data]
    else:
        if not all([provider, id, name, input_cost_credits, output_cost_credits]):
            raise click.UsageError(
                "When not using --json, all options except per_*_tokens are required"
            )
        model_pricing = [
            models.ModelPricingSchema(
                provider=provider,
                id=id,
                name=name,
                input_cost_credits=input_cost_credits,
                per_input_tokens=per_input_tokens,
                output_cost_credits=output_cost_credits,
                per_output_tokens=per_output_tokens,
            )
        ]

    return openwebui_token_tracking.model_pricing.add_model_pricing(
        database_url=database_url,
        model_pricing=model_pricing,
    )
