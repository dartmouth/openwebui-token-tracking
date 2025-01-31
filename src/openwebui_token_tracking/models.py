from pydantic import BaseModel


class ModelPricingSchema(BaseModel):
    id: str
    name: str
    input_cost_credits: int
    per_input_tokens: int
    output_cost_credits: int
    per_output_tokens: int


DEFAULT_MODEL_PRICING = [
    ModelPricingSchema(
        id="openai.gpt-4o-2024-08-06",
        name="GPT-4o (Cloud, Paid) 2024-08-06",
        input_cost_credits=3.75 * 1000,
        per_input_tokens=1_000_000,
        output_cost_credits=15 * 1000,
        per_output_tokens=1_000_000,
    ),
    ModelPricingSchema(
        id="openai.gpt-4o-mini-2024-07-18",
        name="GPT-4o Mini (Cloud, Paid) 2024-07-18",
        input_cost_credits=0.30 * 1000,
        per_input_tokens=1_000_000,
        output_cost_credits=1.2 * 1000,
        per_output_tokens=1_000_000,
    ),
    ModelPricingSchema(
        id="anthropic.claude-3-5-haiku-20241022",
        name="Claude 3.5 Haiku (Cloud, Paid) 2024-10-22",
        input_cost_credits=1 * 1000,
        per_input_tokens=1_000_000,
        output_cost_credits=5 * 1000,
        per_output_tokens=1_000_000,
    ),
    ModelPricingSchema(
        id="anthropic.claude-3-5-sonnet-20241022",
        name="Claude 3.5 Sonnet (Cloud, Paid) 2024-10-22",
        input_cost_credits=3 * 1000,
        per_input_tokens=1_000_000,
        output_cost_credits=15 * 1000,
        per_output_tokens=1_000_000,
    ),
    ModelPricingSchema(
        id="google_genai.gemini-1.5-flash-002",
        name="Gemini 1.5 Flash (Cloud, Paid) 2024-09-01",
        input_cost_credits=0.075 * 1000,
        per_input_tokens=1_000_000,
        output_cost_credits=0.3 * 1000,
        per_output_tokens=1_000_000,
    ),
    ModelPricingSchema(
        id="google_genai.gemini-1.5-pro-002",
        name="Gemini 1.5 Pro (Cloud, Paid) 2024-09-01",
        input_cost_credits=1.25 * 1000,
        per_input_tokens=1_000_000,
        output_cost_credits=5 * 1000,
        per_output_tokens=1_000_000,
    ),
    ModelPricingSchema(
        id="mistral.pixtral-large-2411",
        name="Pixtral Large (Cloud, Paid) 2024-11-01",
        input_cost_credits=2 * 1000,
        per_input_tokens=1_000_000,
        output_cost_credits=6 * 1000,
        per_output_tokens=1_000_000,
    ),
    ModelPricingSchema(
        id="mistral.mistral-small-2409",
        name="Mistral Small (Cloud, Paid) 2024-09-01",
        input_cost_credits=0.2 * 1000,
        per_input_tokens=1_000_000,
        output_cost_credits=0.6 * 1000,
        per_output_tokens=1_000_000,
    ),
    ModelPricingSchema(
        id="meta.llama-3-2-11b-vision-instruct",
        name="Llama 3.2 11b (Local, Free)",
        input_cost_credits=0 * 1000,
        per_input_tokens=1_000_000,
        output_cost_credits=0 * 1000,
        per_output_tokens=1_000_000,
    ),
]
