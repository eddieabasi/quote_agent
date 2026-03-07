"""Tools that write quote data to session state for the Dockie pipeline."""

from typing import List

from google.adk.tools import FunctionTool
from google.adk.tools import ToolContext

from models import PriceLineItem
from models import QuoteAnalysis
from models import QuoteRequest

# State keys used across agents
QUOTE_REQUEST_KEY = "quote_request"
QUOTE_ANALYSIS_KEY = "quote_analysis"


def submit_quote_request(
    origin: str,
    destination: str,
    vehicle_type: str,
    delivery_type: str = "standard",
    item_to_ship: str | None = None,
    notes: str | None = None,
    tool_context: ToolContext | None = None,
) -> str:
    """Save the user's quote request to session state. Call this only when you have collected origin, destination, vehicle type, and delivery type from the user.

    Args:
        origin: Pickup or origin address/location.
        destination: Delivery destination address/location.
        vehicle_type: Type of vehicle (e.g. van, truck, bike).
        delivery_type: Delivery speed: standard or express.
        item_to_ship: Description of what the user wants to ship (e.g. furniture, documents, pallet).
        notes: Optional delivery notes.
        tool_context: Injected by the framework; used to access session state.
    """
    if tool_context is None:
        return "Error: no session context available."
    req = QuoteRequest(
        origin=origin,
        destination=destination,
        vehicle_type=vehicle_type,
        delivery_type=delivery_type,
        item_to_ship=item_to_ship,
        notes=notes,
    )
    tool_context.state[QUOTE_REQUEST_KEY] = req.model_dump()
    return "Quote request saved. The next step will analyze it and provide a price estimate."


def submit_quote_analysis(
    matched_scenario: str,
    estimated_price: float,
    breakdown: str | None = None,
    confidence: str | None = None,
    currency: str = "USD",
    base_fee: float | None = None,
    per_km_rate: float | None = None,
    assumed_distance_km: float | None = None,
    breakdown_labels: List[str] | None = None,
    breakdown_amounts: List[float] | None = None,
    confidence_explanation: str | None = None,
    assumptions: List[str] | None = None,
    highlights: List[str] | None = None,
    tool_context: ToolContext | None = None,
) -> str:
    """Save the quote analysis (matched scenario and price) to session state. Call this after you have determined the best matching scenario and estimated price.

    Args:
        matched_scenario: Name or ID of the matched pricing scenario.
        estimated_price: Estimated total price in currency units.
        breakdown: Short human-readable summary of the breakdown (e.g. "Base $45 + 10 km × $1.20 = $57.00").
        confidence: Confidence level: "high" or "medium".
        currency: Currency code (default "USD").
        base_fee: Base fee before distance charge.
        per_km_rate: Rate per km.
        assumed_distance_km: Distance used for calculation (stated or assumed).
        breakdown_labels: Labels for each price line item, in order (e.g. ["Base fee", "Distance charge", "Total"]).
        breakdown_amounts: Amounts for each price line item, in the same order as breakdown_labels.
        confidence_explanation: Short explanation of confidence level.
        assumptions: List of assumptions made during analysis.
        highlights: 2-4 short bullets for quick-scan display on the UI card.
        tool_context: Injected by the framework; used to access session state.
    """
    if tool_context is None:
        return "Error: no session context available."

    parsed_lines = [
        PriceLineItem(label=label, amount=amount)
        for label, amount in zip(breakdown_labels or [], breakdown_amounts or [])
    ]

    analysis = QuoteAnalysis(
        matched_scenario=matched_scenario,
        estimated_price=estimated_price,
        breakdown=breakdown,
        confidence=confidence,
        currency=currency,
        base_fee=base_fee,
        per_km_rate=per_km_rate,
        assumed_distance_km=assumed_distance_km,
        breakdown_lines=parsed_lines,
        confidence_explanation=confidence_explanation,
        assumptions=assumptions or [],
        highlights=highlights or [],
    )
    tool_context.state[QUOTE_ANALYSIS_KEY] = analysis.model_dump()
    return "Quote analysis saved. The recommendation will be shown to the user next."


# Tool instances for use by LlmAgents
submit_quote_request_tool = FunctionTool(submit_quote_request)
submit_quote_analysis_tool = FunctionTool(submit_quote_analysis)
