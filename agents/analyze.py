"""AnalyzeAgent: matches the quote request to likely cases and produces a price recommendation."""

from google.adk.agents import LlmAgent

from tools import submit_quote_analysis_tool

# Likely cases (scenarios) for v1: placeholder pricing by vehicle and delivery type.
LIKELY_CASES = """
Likely pricing scenarios (use the best match):
- van + standard: base $45, then $1.20/km. Scenario ID: van_standard
- van + express: base $65, then $1.80/km. Scenario ID: van_express
- truck + standard: base $80, then $2.00/km. Scenario ID: truck_standard
- truck + express: base $120, then $2.50/km. Scenario ID: truck_express
- bike + standard: base $15, then $0.50/km. Scenario ID: bike_standard
- bike + express: base $25, then $0.80/km. Scenario ID: bike_express

If the user did not specify distance, assume a typical urban distance (e.g. 10 km) and state that in the breakdown. Round the final price to 2 decimal places.
"""

ANALYZE_INSTRUCTION = f"""You are the analysis step for Dockie quotes. The user's quote request is in session state.

Quote request (from state): {{quote_request?}}

It contains: origin, destination, vehicle_type, delivery_type, and optional notes.

{LIKELY_CASES}

Determine the best matching scenario, estimate the price (you may infer a typical distance if not stated), and then call submit_quote_analysis exactly once with:
- matched_scenario: the scenario ID from the list above
- estimated_price: the calculated total (number)
- breakdown: a short human-readable breakdown (e.g. "Base $45 + 10 km × $1.20 = $57.00")
- confidence: "high" if vehicle and delivery type match a scenario, otherwise "medium"
"""

analyze_agent = LlmAgent(
    name="AnalyzeAgent",
    model="gemini-3.1-flash-lite-preview",
    instruction=ANALYZE_INSTRUCTION,
    tools=[submit_quote_analysis_tool],
)
