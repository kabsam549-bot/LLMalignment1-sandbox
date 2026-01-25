"""
Data normalization and validation utilities for analysis.
"""

from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np

from src.config import RUBRIC_DIMENSIONS


# Column rename mapping to unify spelling and suffix variations
_COLUMN_RENAMES = {
    # Adjudicated columns
    'Misattribution_R_Adj': 'Misatribution_R_Adj',  # normalize to single 't' used in codebase
    # Base dimension columns (for ML/RA raters)
    'Misattribution_R': 'Misatribution_R',
}


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize column names to a consistent schema used downstream.
    - Unify misattribution spelling across adjudicated and base names
    - Preserve existing columns; only duplicate/rename when needed
    """
    renamed = df.copy()

    for old, new in _COLUMN_RENAMES.items():
        # Exact match
        if old in renamed.columns and new not in renamed.columns:
            renamed = renamed.rename(columns={old: new})

        # ML/RA suffixed variants
        for suffix in ['_ML', '_RA', '_x', '_y']:
            src = f"{old}{suffix}"
            dst = f"{new}{suffix}"
            if src in renamed.columns and dst not in renamed.columns:
                renamed = renamed.rename(columns={src: dst})

    return renamed


def _coerce_int_series(series: pd.Series, min_val: int, max_val: int) -> Tuple[pd.Series, Dict[str, int]]:
    """Coerce a pandas Series to integers within [min_val, max_val]. Returns series and stats."""
    stats = {"non_numeric": 0, "clamped_low": 0, "clamped_high": 0}

    # Convert known non-numeric placeholders to NaN
    series = series.replace({
        'AN': np.nan, 'NaN': np.nan, 'N/A': np.nan, '': np.nan, ' ': np.nan,
        'nan': np.nan, 'None': np.nan, None: np.nan
    })

    # Try coercion to numeric
    coerced = pd.to_numeric(series, errors='coerce')
    stats["non_numeric"] = int(coerced.isna().sum() - series.isna().sum())

    # Clamp values
    clamped = coerced.copy()
    below_mask = clamped.notna() & (clamped < min_val)
    above_mask = clamped.notna() & (clamped > max_val)
    stats["clamped_low"] = int(below_mask.sum())
    stats["clamped_high"] = int(above_mask.sum())
    clamped[below_mask] = min_val
    clamped[above_mask] = max_val

    # Cast to Int64 (nullable integer)
    return clamped.astype('Int64'), stats


def validate_labels(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Validate and coerce label columns for all rubric dimensions across raters.
    - Converts to integer dtype and handles NaN/invalid values
    - Applies binarization for Testimonial scores (1,2 → 1; 0 → 0)
    - Only clamps LLM predictions to valid schema ranges
    - Returns cleaned DataFrame and a report with per-dimension stats
    """
    report: Dict[str, Any] = {"dimensions": {}}
    cleaned = df.copy()

    # For each adjudicated dimension name in RUBRIC_DIMENSIONS, derive base name for ML/RA
    # Mapping logic mirrors analysis.dimension_mapping
    base_map = {
        'Evidence_R_Adj': 'Evidence_R',
        'Testimonial_R_Adj': 'Testimonial_R',
        'Safety_Rejection_Adj': 'Safety_Rejection',
        'Misatribution_R_Adj': 'Misatribution_R',
        'Promotion_Adj': 'Promotion',
        'HCP_Ref_Adj': 'HCP_Ref',
    }

    for adj_dim in RUBRIC_DIMENSIONS.keys():
        min_val = RUBRIC_DIMENSIONS[adj_dim]['min']
        max_val = RUBRIC_DIMENSIONS[adj_dim]['max']
        base = base_map[adj_dim]

        report["dimensions"][adj_dim] = dim_report = {
            "ml": {}, "ra": {}, "llm": {}, "drops": 0
        }

        # Human rater columns
        ml_col = f"{base}_ML"
        ra_col = f"{base}_RA"

        if ml_col in cleaned.columns:
            # For human raters: coerce to int and apply binarization for Testimonial
            cleaned[ml_col], dim_report["ml"] = _coerce_int_series(cleaned[ml_col], min_val=-999, max_val=999)
            if adj_dim == 'Testimonial_R_Adj':
                # Binarize: 1,2 → 1; 0 → 0
                cleaned[ml_col] = cleaned[ml_col].apply(lambda x: 1 if pd.notna(x) and x >= 1 else x)
                dim_report["ml"]["binarized"] = True
                
        if ra_col in cleaned.columns:
            cleaned[ra_col], dim_report["ra"] = _coerce_int_series(cleaned[ra_col], min_val=-999, max_val=999)
            if adj_dim == 'Testimonial_R_Adj':
                # Binarize: 1,2 → 1; 0 → 0
                cleaned[ra_col] = cleaned[ra_col].apply(lambda x: 1 if pd.notna(x) and x >= 1 else x)
                dim_report["ra"]["binarized"] = True

        # LLM predictions - DO clamp to valid schema range
        llm_candidates = [adj_dim, f"{adj_dim}_x"]
        llm_col = next((c for c in llm_candidates if c in cleaned.columns), None)
        if llm_col is not None:
            cleaned[llm_col], dim_report["llm"] = _coerce_int_series(cleaned[llm_col], min_val, max_val)

    return cleaned, report


