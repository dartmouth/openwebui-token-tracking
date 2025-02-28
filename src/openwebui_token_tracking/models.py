from pydantic import BaseModel


class ModelPricingSchema(BaseModel):
    provider: str
    """Provider of the AI model (e.g., 'openai', 'anthropic')"""
    id: str
    """Identifier of the model (e.g., 'gpt-4', 'claude-3')"""
    name: str
    """Display name of the model"""
    input_cost_credits: int
    """Number of credits charged for input tokens"""
    per_input_tokens: int
    """Number of input tokens per credit charge (e.g., 1000000 tokens per `input_cost_credits`)"""
    output_cost_credits: int
    """Number of credits charged for output tokens"""
    per_output_tokens: int
    """Number of output tokens per credit charge (e.g., 1000000 tokens per `output_cost_credits`)"""
