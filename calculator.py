import pandas as pd

def calculator(max_t:int,
               L:float,
               P0:float,
               g:float,
               r_avg:float,
               K0:float,
               S0:float,
               alpha:float=1.0):
    """
    Run the KiwiSaver + Life Cover offset projection for t=0..max_t
    
    Parameters
    ----------
    max_t : int
        Number of years to project (inclusive, starting at t=0).
    L : float
        Base life cover amount.
    P0 : float
        Baseline premium at t=0.
    g : float
        Annual premium escalation rate (decimal, e.g. 0.03 for 3%).
    r_avg : float
        Annual return % vs average capital base (decimal, e.g. 0.05011).
    K0 : float
        Initial KiwiSaver balance at t=0.
    S0 : float
        Annual salary contribution (assumed constant for all years here).
    alpha : float, optional
        Offset ratio (default 1.0 for dollar-for-dollar offset).
    
    Returns
    -------
    pd.DataFrame with columns for each year's metrics.
    """
    rows = []
    Kt = K0
    for t in range(max_t+1):
        # Premium escalation
        Pt = P0 * (1+g)**t
        
        # Offset and effective cover
        Ot = min(alpha * Kt, L)
        Et = max(0.0, L - Ot)
        
        # Premium with offset and saving
        P_off_t = Pt * (Et/L)
        dPt = Pt - P_off_t
        Vt = dPt
        
        # Annual return using average capital base method
        avg_capital_base = Kt + 0.5*(S0 + Vt)
        return_t = r_avg * avg_capital_base
        
        # End balance
        Kt1 = Kt + S0 + Vt + return_t
        
        rows.append({
            "t": t,
            "KiwiSaver Start Balance": Kt,
            "Baseline Premium": Pt,
            "Offset": Ot,
            "Effective Cover": Et,
            "Premium w/ Offset": P_off_t,
            "Premium Saving": dPt,
            "Voluntary Contribution": Vt,
            "Annual Salary Contribution": S0,
            "Annual Investment Return": return_t,
            "KiwiSaver End Balance": Kt1
        })
        
        Kt = Kt1  # update for next year
    
    return pd.DataFrame(rows)


# Test run for 2 years with your sample parameters
df_test = calculator(max_t=2,
                     L=500_000,
                     P0=1800,
                     g=0.03,
                     r_avg=0.05011,
                     K0=120_000,
                     S0=6800,
                     alpha=1.0)

