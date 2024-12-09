import numpy as np
from typing import List, Dict

def format_currency(value: float) -> str:
    """Format a number as currency."""
    return f"${value:,.2f}"

def format_percentage(value: float) -> str:
    """Format a number as percentage."""
    return f"{value * 100:.1f}%"

def calculate_summary_statistics(values: List[float]) -> Dict[str, float]:
    """Calculate summary statistics for a list of values."""
    return {
        "mean": np.mean(values),
        "median": np.median(values),
        "std": np.std(values),
        "min": np.min(values),
        "max": np.max(values)
    }
