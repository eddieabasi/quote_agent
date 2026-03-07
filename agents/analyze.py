"""AnalyzeAgent: matches the quote request to likely cases and produces a price recommendation."""

from ag_ui_adk import AGUIToolset
from google.adk.agents import LlmAgent
from google.genai import types

from config import ANALYZE_MODEL
from tools import submit_quote_analysis_tool

# Pricing scenarios for v1.
LIKELY_CASES = """
Pricing scenarios (pick the best match):
| Scenario ID     | Vehicle | Type     | Base  | Per-km |
|-----------------|---------|----------|-------|--------|
| van_standard    | van     | standard | $45   | $1.20  |
| van_express     | van     | express  | $65   | $1.80  |
| truck_standard  | truck   | standard | $80   | $2.00  |
| truck_express   | truck   | express  | $120  | $2.50  |
| bike_standard   | bike    | standard | $15   | $0.50  |
| bike_express    | bike    | express  | $25   | $0.80  |

If no distance is given, assume 10 km for a typical urban delivery and note that assumption.
Round estimated_price to 2 decimal places.
"""

ANALYZE_INSTRUCTION = f"""You are the pricing analysis step for Dockie, a logistics quoting platform.

The user's quote request is in session state:
{{quote_request?}}

{LIKELY_CASES}

Follow these steps exactly:

1. Pick the matching scenario for the vehicle_type + delivery_type combination.
2. Compute the total: base_fee + (distance_km × per_km_rate).
3. Call submit_quote_analysis ONCE with ALL of the following fields populated:

   — Legacy summary fields (required for downstream export):
   • matched_scenario  — scenario ID from the table above
   • estimated_price   — calculated total as a float
   • breakdown         — one-line human-readable summary, e.g. "Base $45 + 10 km × $1.20 = $57.00"
   • confidence        — "high" if both vehicle and delivery type matched exactly, else "medium"

   — Rich UI fields (required for the generative UI card):
   • currency          — always "USD"
   • base_fee          — base fee as a float
   • per_km_rate       — per-km rate as a float
   • assumed_distance_km — distance used (stated or assumed), as a float
   • breakdown_labels  — list of label strings, one per line item, e.g.
                         ["Base fee", "Distance (10 km × $1.20)", "Total"]
   • breakdown_amounts — list of floats in the same order as breakdown_labels, e.g.
                         [45.0, 12.0, 57.0]
   • confidence_explanation — one sentence explaining why confidence is high or medium
   • assumptions       — list of strings describing what the model assumed (e.g. distance, vehicle suitability)
   • highlights        — exactly 3 short bullets for the summary card, e.g.
                         ["Van · Express delivery", "Est. 10 km urban route", "Price: $69.00"]

4. After submit_quote_analysis succeeds, call the display_quote_analysis frontend tool with
   the SAME values (all legacy + rich fields, using breakdown_labels / breakdown_amounts).
   This is what renders the UI card. Do NOT skip it.

Do not add any conversational text — the UI handles presentation.
"""

analyze_agent = LlmAgent(
    name="AnalyzeAgent",
    model=ANALYZE_MODEL,
    instruction=ANALYZE_INSTRUCTION,
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2,
    ),
    tools=[
        submit_quote_analysis_tool,
        AGUIToolset(),
    ],
)
