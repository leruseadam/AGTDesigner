#!/usr/bin/env python3
"""
Compatibility wrapper for the unified font sizing system.

All actual logic now lives in `src.core.generation.unified_font_sizing`.
This module exists only so older imports like `core.generation.unified_font_sizing`
continue to work without duplicating any logic or configuration.
"""

from src.core.generation.unified_font_sizing import *  # noqa: F401,F403
