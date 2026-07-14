"""Lopez-Lira & Tang (2023) zero-shot headline prompt, lightly adapted."""
PROMPT_VERSION = "llt-zero-shot-json-v1"

TEMPLATE = (
    "Forget all your previous instructions. Pretend you are a financial expert. You are a financial "
    "expert with stock recommendation experience. Classify the headline as YES if it is good news, "
    "NO if it is bad news, or UNKNOWN if uncertain for the stock price of {company} in the short "
    "term. Return exactly one JSON object with exactly two string fields: "
    "{{\"label\": \"YES|NO|UNKNOWN\", \"reason\": \"one short sentence\"}}.\n\n"
    "Headline: {headline}"
)


def build_prompt(headline: str, company: str) -> str:
    if not headline:
        raise ValueError("headline required")
    return TEMPLATE.format(company=company or "the company", headline=headline)
