"""Model configuration for the Dockie quote pipeline.

Tier defaults:
  LITE_MODEL     — lightweight conversational turns (gather, recommend)
  STANDARD_MODEL — structured output with richer reasoning (analyze)

Per-agent overrides via env vars let you swap one agent's model without
touching the code:
  DOCKIE_GATHER_MODEL, DOCKIE_ANALYZE_MODEL, DOCKIE_RECOMMEND_MODEL

To swap the entire fleet to a new lite/standard model, set:
  DOCKIE_LITE_MODEL, DOCKIE_STANDARD_MODEL
"""

import os

LITE_MODEL     = os.getenv("DOCKIE_LITE_MODEL",     "gemini-3.1-flash-lite-preview")
STANDARD_MODEL = os.getenv("DOCKIE_STANDARD_MODEL", "gemini-3.1-flash-lite-preview")

GATHER_MODEL    = os.getenv("DOCKIE_GATHER_MODEL",    LITE_MODEL)
ANALYZE_MODEL   = os.getenv("DOCKIE_ANALYZE_MODEL",   STANDARD_MODEL)
RECOMMEND_MODEL = os.getenv("DOCKIE_RECOMMEND_MODEL", LITE_MODEL)
