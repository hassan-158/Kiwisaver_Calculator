import pandas as pd
import numpy as np
from typing import List, Tuple

# Hidden constant: Funeral/impact buffer (not exposed in UI)
FUNERAL_AND_BUFFER = 100_000  # fixed and used only internally

def calculator_phaseout(max_t:int,
                        L:float,
                        P0:float,
                        g:float,
                        r_avg:float,
                        K0:float,
                        si: float,
                        S0:float,
                        alpha:float=1.0) -> Tuple[pd.DataFrame, int]:
    """
    Phase-out model: KiwiSaver offsets cover and premium savings are reinvested into KiwiSaver.
    Returns dataframe and the year index (relative, 1-based) when cover reaches 0 (or None).
    """
    rows = []
    Kt = float(K0)
    full_cover_t = np.inf

    for t in range(max_t+1):
        Pt = float(P0) * (1.0 + g)**t

        Ot = min(alpha * Kt, L)
        Et = max(0.0, L - Ot)

        P_off_t = Pt * (Et / L) if L > 0 else 0.0
        dPt = Pt - P_off_t
        Vt = dPt

        St = float(S0) * (1.0 + si)**t
        avg_capital_base = Kt + 0.5 * (St + Vt)
        return_t = r_avg * avg_capital_base

        Kt1 = Kt + St + Vt + return_t

        rows.append({
            "year": t + 1,
            "KiwiSaver Start Balance": Kt,
            "Baseline Premium": Pt,
            "Offset": Ot,
            "Effective Cover": Et,
            "Premium w/ Offset": P_off_t,
            "Premium Saving": dPt,
            "Voluntary Contribution": Vt,
            "Annual Salary Contribution": St,
            "Annual Investment Return": return_t,
            "KiwiSaver End Balance": Kt1
        })

        Kt = Kt1
        if Kt >= L and full_cover_t == np.inf:
            full_cover_t = t + 1

    df = pd.DataFrame(rows)
    if full_cover_t == np.inf:
        full_cover_t = None
    return df, full_cover_t


def responsibility_for_age(age: int) -> float:
    """Total remaining responsibility for a child of a given age until 18."""
    total = 0.0
    for a in range(age, 18):
        if 0 <= a <= 15:
            total += 35_000
        elif 16 <= a <= 17:
            total += 50_000
    return total


def calculator_total_wealth(
    max_t: int,
    L: float,  # initial gap only, funeral handled below
    P0: float,
    g: float,
    r_avg: float,
    K0: float,
    si: float,
    S0: float,
    property_value: float,
    cash: float,
    managed_funds: float,
    other_assets: float,
    liabilities: float,
    child_ages: list,
    asset_growth_rate: float,
    debt_shrink_rate: float
):
    """
    Total-Wealth life cover projection.
    Returns DataFrame with start/end-of-year values for assets, liabilities, responsibilities,
    and required cover before any phase-outs.
    Also returns the first year where Required Cover is fully offset (full_cover_t).
    """
    # Initialize start-of-year values
    Kt = K0
    assets_t = property_value + cash + managed_funds + other_assets
    debt_t = liabilities

    rows = []
    full_cover_t = np.inf

    for t in range(max_t + 1):
        # ------------------ Start-of-Year Values ------------------
        assets_start = assets_t
        debt_start = debt_t
        responsibilities_start = sum([responsibility_for_age(age + t) for age in child_ages])
        total_wealth_start = Kt + assets_start
        total_liabilities_start = debt_start + responsibilities_start + FUNERAL_AND_BUFFER
        required_cover_start = max(0.0, total_liabilities_start - total_wealth_start)

        # ------------------ Premiums and offsets ------------------
        Pt = P0 * (1 + g) ** t
        offset = min(Kt, required_cover_start)
        effective_cover = required_cover_start - offset
        premium_with_offset = Pt * (effective_cover / max(1, required_cover_start)) if required_cover_start > 0 else 0.0
        premium_saving = Pt - premium_with_offset
        voluntary_contribution = premium_saving

        # ------------------ Salary contribution and KiwiSaver growth ------------------
        St = S0 * (1 + si) ** t
        avg_capital_base = Kt + 0.5 * (St + voluntary_contribution)
        return_t = r_avg * avg_capital_base
        Kt1 = Kt + St + voluntary_contribution + return_t  # end-of-year KiwiSaver balance

        # ------------------ End-of-Year Updates ------------------
        assets_end = assets_t * (1 + asset_growth_rate)
        debt_end = debt_t * (1 - debt_shrink_rate)
        responsibilities_end = sum([responsibility_for_age(age + t + 1) for age in child_ages])

        # ------------------ Append row ------------------
        rows.append({
            "year": t + 1,
            "KiwiSaver Start Balance": Kt,
            "Total Assets Start": assets_start,
            "Total Liabilities Start": debt_start,
            "Responsibilities Start": responsibilities_start,
            "Baseline Premium": Pt,
            "Required Cover": required_cover_start,
            "Premium w/ Required Cover": premium_with_offset,
            "Premium Saving": premium_saving,
            "Voluntary Contribution": voluntary_contribution,
            "Annual Salary Contribution": St,
            "Annual Investment Return": return_t,
            "KiwiSaver End Balance": Kt1,
            "Total Assets": assets_end,
            "Total Liabilities": debt_end,
            "Responsibilities": responsibilities_end
        })

        # ------------------ Determine full_cover_t ------------------
        # Check after Kt1 growth applied: this marks the first year the cover is fully offset
        gap_next = max(0.0, debt_end + responsibilities_end + FUNERAL_AND_BUFFER - (Kt1 + assets_end))
        if gap_next <= 0.0 and full_cover_t == np.inf:
            full_cover_t = t + 1  # 1-based index (first fully covered year)

        # Prepare for next year
        Kt = Kt1
        assets_t = assets_end
        debt_t = debt_end

    if full_cover_t == np.inf:
        full_cover_t = None

    return pd.DataFrame(rows), full_cover_t