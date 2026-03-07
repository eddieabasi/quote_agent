"""Shared Pydantic models for the Dockie quote pipeline (session state contract)."""

from pydantic import BaseModel, Field


class QuoteRequest(BaseModel):
    """User's quote request: route, vehicle, and delivery needs."""

    origin: str = Field(..., description="Pickup or origin address/location")
    destination: str = Field(..., description="Delivery destination address/location")
    vehicle_type: str = Field(
        ...,
        description="Type of vehicle (e.g. van, truck, bike)",
    )
    delivery_type: str = Field(
        default="standard",
        description="Delivery speed: standard or express",
    )
    item_to_ship: str | None = Field(
        default=None,
        description="Description of the item(s) to be shipped",
    )
    notes: str | None = Field(default=None, description="Optional delivery notes")


class QuoteAnalysis(BaseModel):
    """Analysis result: matched scenario and price recommendation."""

    matched_scenario: str = Field(
        ...,
        description="Name or ID of the matched pricing scenario",
    )
    estimated_price: float = Field(
        ...,
        description="Estimated price in currency units",
    )
    breakdown: str | None = Field(
        default=None,
        description="Optional human-readable price breakdown",
    )
    confidence: str | None = Field(
        default=None,
        description="Optional confidence level (e.g. high, medium)",
    )
