"""Lopez-Lira & Tang (2023) zero-shot headline prompt, lightly adapted."""
TEMPLATE = (
    "Forget all your previous instructions. Pretend you are a financial expert. You are a financial "
    "expert with stock recommendation experience. Answer YES if good news, NO if bad news, or UNKNOWN "
    "if uncertain in the first line. Then elaborate with one short and concise sentence on the next "
    "line. Is this headline good or bad for the stock price of {company} in the short term?\n\n"
    "Headline: {headline}"
)


def build_prompt(headline: str, company: str) -> str:
    if not headline:
        raise ValueError("headline required")
    return TEMPLATE.format(company=company or "the company", headline=headline)
