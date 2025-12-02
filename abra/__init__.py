"""
Abra - Advanced Brand Research & Analysis
Version 11.1.0

A professional toolkit for brand intelligence and market research using
Google Trends, SerpAPI, and advanced analytics.

Modules:
    config: Configuration and constants
    core: Core PyTrends functionality
    analysis: Analysis engines (SerpAPI, insights, historical, etc.)
    components: Reusable UI components
    ui: Theming and styles
    pages: Application pages/views
    utils: Utility functions
"""

__version__ = "11.1.0"
__author__ = "Abra Team"
__license__ = "MIT"

# Public API exports
from abra.config.constants import (
    COUNTRIES,
    PRODUCT_CATEGORIES,
    CHANNELS,
)

__all__ = [
    "__version__",
    "COUNTRIES",
    "PRODUCT_CATEGORIES",
    "CHANNELS",
]
