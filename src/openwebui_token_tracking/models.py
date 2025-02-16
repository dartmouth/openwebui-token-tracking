from pydantic import BaseModel


class ModelPricingSchema(BaseModel):
    provider: str
    id: str
    name: str
    input_cost_credits: int
    per_input_tokens: int
    output_cost_credits: int
    per_output_tokens: int
