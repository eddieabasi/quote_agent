"""Shared Pydantic models for the Dockie quote pipeline (session state contract)."""

from typing import List

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


class PriceLineItem(BaseModel):
    """A single row in the pricing breakdown (e.g. base fee, distance charge)."""

    label: str = Field(..., description="Human-readable label for this line item")
    amount: float = Field(..., description="Amount for this line item in currency units")


class QuoteAnalysis(BaseModel):
    """Analysis result: matched scenario and price recommendation."""

    # --- legacy flat fields (kept for backward-compat with export builders) ---
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

    # --- richer fields for generative UI rendering ---
    currency: str = Field(default="USD", description="Currency code")
    base_fee: float | None = Field(default=None, description="Base fee before distance charge")
    per_km_rate: float | None = Field(default=None, description="Rate per km")
    assumed_distance_km: float | None = Field(
        default=None,
        description="Distance used for calculation (stated or assumed)",
    )
    breakdown_lines: List[PriceLineItem] = Field(
        default_factory=list,
        description="Typed line items for the price breakdown table",
    )
    confidence_explanation: str | None = Field(
        default=None,
        description="Short explanation of why confidence is high or medium",
    )
    assumptions: List[str] = Field(
        default_factory=list,
        description="List of assumptions the model made during analysis",
    )
    highlights: List[str] = Field(
        default_factory=list,
        description="2-4 short bullets for quick-scan display on the UI card",
    )
