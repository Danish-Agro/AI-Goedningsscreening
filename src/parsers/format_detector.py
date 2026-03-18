#!/usr/bin/env python3
"""
Format Detector for SoilOptix lab Excel files.

Inspects an uploaded Excel file and returns the appropriate parser instance.
Raises FormatNotRecognizedError with a seller-friendly message if the format
cannot be identified.
"""

import pandas as pd
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from parsers.soiloptix_parser import SoilOptixParser


class FormatNotRecognizedError(Exception):
    """Raised when the Excel format does not match any known layout."""
    pass


# ---------------------------------------------------------------------------
# SoilOptix column-oriented format
# ---------------------------------------------------------------------------
# Layout (0-indexed rows, cols):
#   Row  2, col 1  → Kundenr
#   Row  5, col 1  → label "Ordre nr" / ordrenummer
#   Row  6, col 1  → label "Analyse nr"
#   Row  7, col 1  → label "Prøvebetegnelse"
#   Row  8, col 1  → label "Field ID"
#   Row  9, col 1  → label "Marknummer"
#   Row 10         → parameter header row
#   Row 11+, col 0/1/2 → parameter names ("Rt", "Fosfor", …)
#   Rows 11+, col 3+ → numeric sample data (one sample per column)
# ---------------------------------------------------------------------------

_SOILOPTIX_METADATA_LABELS = {
    "analyse nr",
    "field id",
    "marknummer",
}

_SOILOPTIX_PARAMETER_LABELS = {
    "rt",
    "fosfor",
    "kalium",
    "magnesium",
}

# Minimum rows needed: ROW_DATA_START (11) + 4 required parameters
_SOILOPTIX_MIN_ROWS = 15
_SOILOPTIX_MIN_COLS = 4   # at least one data column (col 3)
_SOILOPTIX_LABEL_COLS = range(3)  # search label columns 0, 1, 2
_SOILOPTIX_METADATA_ROWS = range(4, 11)  # rows 4-10 contain metadata labels
_SOILOPTIX_PARAM_ROWS = range(11, min(25, _SOILOPTIX_MIN_ROWS + 12))


def _cell_str(df: pd.DataFrame, row: int, col: int) -> str:
    """Return lowercase stripped string for a cell, or '' if missing/NaN."""
    try:
        val = df.iloc[row, col]
        if pd.isna(val):
            return ""
        return str(val).strip().lower()
    except (IndexError, KeyError):
        return ""


def _score_soiloptix(df: pd.DataFrame) -> int:
    """
    Return a confidence score for SoilOptix column-oriented format.
    Higher is more confident. Threshold for acceptance: 3.
    """
    score = 0

    if df.shape[0] < _SOILOPTIX_MIN_ROWS or df.shape[1] < _SOILOPTIX_MIN_COLS:
        return 0

    # Check metadata label rows (4-10) across label columns
    found_meta = set()
    for row in _SOILOPTIX_METADATA_ROWS:
        for col in _SOILOPTIX_LABEL_COLS:
            cell = _cell_str(df, row, col)
            for label in _SOILOPTIX_METADATA_LABELS:
                if label in cell:
                    found_meta.add(label)
    score += len(found_meta)  # up to 3 points

    # Check parameter label rows (11-24) across label columns
    found_params = set()
    for row in _SOILOPTIX_PARAM_ROWS:
        for col in _SOILOPTIX_LABEL_COLS:
            cell = _cell_str(df, row, col)
            for label in _SOILOPTIX_PARAMETER_LABELS:
                if cell == label or cell.startswith(label + " "):
                    found_params.add(label)
    score += len(found_params)  # up to 4 points

    # Check that column 3 has at least one numeric value in parameter rows
    has_numeric = False
    for row in _SOILOPTIX_PARAM_ROWS:
        try:
            val = df.iloc[row, 3]
            if not pd.isna(val):
                float(str(val).replace(",", "."))
                has_numeric = True
                break
        except (ValueError, IndexError):
            pass
    if has_numeric:
        score += 1

    return score


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def detect_and_create_parser(filepath: str):
    """
    Load the Excel file, detect its format, and return an initialised parser.

    Parameters
    ----------
    filepath : str
        Path to the uploaded .xlsx / .xls file.

    Returns
    -------
    SoilOptixParser
        A parser instance with the file already loaded (load() has been called).

    Raises
    ------
    FormatNotRecognizedError
        If no known format matches the file. The message is suitable for
        display directly to the seller.
    """
    path = Path(filepath)

    try:
        df = pd.read_excel(path, header=None)
    except Exception as exc:
        raise FormatNotRecognizedError(
            f"Filen kunne ikke åbnes som Excel ({exc}). "
            "Kontrollér at filen er en gyldig .xlsx- eller .xls-fil."
        ) from exc

    soiloptix_score = _score_soiloptix(df)

    if soiloptix_score >= 3:
        # Lazy import to avoid circular dependency
        from parsers.soiloptix_parser import SoilOptixParser
        parser = SoilOptixParser(filepath)
        parser.df = df   # reuse already-loaded DataFrame
        return parser

    # -----------------------------------------------------------------------
    # Format not recognised — build a helpful error message
    # -----------------------------------------------------------------------
    rows, cols = df.shape
    hints = []

    if rows < _SOILOPTIX_MIN_ROWS:
        hints.append(f"filen har kun {rows} rækker (forventet mindst {_SOILOPTIX_MIN_ROWS})")
    if cols < _SOILOPTIX_MIN_COLS:
        hints.append(f"filen har kun {cols} kolonner (forventet mindst {_SOILOPTIX_MIN_COLS})")

    # Check which expected labels are missing
    all_cells = set()
    for row in range(min(30, rows)):
        for col in _SOILOPTIX_LABEL_COLS:
            val = _cell_str(df, row, col)
            if val:
                all_cells.add(val)

    missing_meta = _SOILOPTIX_METADATA_LABELS - {
        label for label in _SOILOPTIX_METADATA_LABELS
        if any(label in c for c in all_cells)
    }
    if missing_meta:
        hints.append(
            "mangler forventede felter: " + ", ".join(f'"{m}"' for m in sorted(missing_meta))
        )

    hint_str = "; ".join(hints) if hints else "layoutet matcher ikke noget kendt format"

    raise FormatNotRecognizedError(
        f"Filformatet kunne ikke genkendes ({hint_str}). "
        "Understøttede formater: SoilOptix kolonneformat (AGROLAB). "
        "Kontrollér at du uploader den uændrede Excel-fil fra laboratoriet."
    )
