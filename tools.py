"""Tools that write quote data to session state for the Dockie pipeline."""

from google.adk.tools import FunctionTool
from google.adk.tools import ToolContext

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
    tool_context: ToolContext | None = None,
) -> str:
    """Save the quote analysis (matched scenario and price) to session state. Call this after you have determined the best matching scenario and estimated price.

    Args:
        matched_scenario: Name or ID of the matched pricing scenario.
        estimated_price: Estimated price in currency units.
        breakdown: Optional human-readable price breakdown.
        confidence: Optional confidence level (e.g. high, medium).
        tool_context: Injected by the framework; used to access session state.
    """
    if tool_context is None:
        return "Error: no session context available."
    analysis = QuoteAnalysis(
        matched_scenario=matched_scenario,
        estimated_price=estimated_price,
        breakdown=breakdown,
        confidence=confidence,
    )
    tool_context.state[QUOTE_ANALYSIS_KEY] = analysis.model_dump()
    return "Quote analysis saved. The recommendation will be shown to the user next."


# Tool instances for use by LlmAgents
submit_quote_request_tool = FunctionTool(submit_quote_request)
submit_quote_analysis_tool = FunctionTool(submit_quote_analysis)
