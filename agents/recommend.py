"""RecommendAgent: presents the quote recommendation to the user in plain language."""

from google.adk.agents import LlmAgent


RECOMMEND_INSTRUCTION = f"""You are Dockie's recommendation step. The quote request and analysis are in session state.

Quote request: {{quote_request?}}
Quote analysis: {{quote_analysis?}}

Write a short, friendly message to the user that:
1. Summarizes their request (origin → destination, vehicle, delivery type).
2. Gives the estimated price clearly (no surprises).
3. Mentions the breakdown if available.
4. Tells them they can get a PDF or DOCX download in the next step.

Keep it transparent and concise. Do not use tools; just reply with the recommendation text."""

recommend_agent = LlmAgent(
    name="RecommendAgent",
    model="gemini-3.1-flash-lite-preview",
    instruction=RECOMMEND_INSTRUCTION,
    tools=[],  # No tools; only presents from state
)
