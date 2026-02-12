import numpy as np
import pandas as pd
from arch import arch_model

def run_v3_governance_engine(df):
    """
    V3 UPGRADE: Adaptive Regime Gating
    - Replaces fixed -1.5 Z-score with a 10th percentile liquidity floor.
    - Replaces fixed vol thresholds with 90th percentile GARCH surface.
    - Implements Epistemic Modesty via NaN-Halt.
    """
    # 1. Epistemic Guard: Fail-Closed on missing data
    if df[['sp_ret', 'net_liquidity']].isnull().any().any():
        print("VETO: Incomplete Data Stream. Fail-Closed.")
        return True

    # 2. Adaptive Liquidity Floor (10th Percentile)
    # Instead of -1.5, we veto when liquidity is in the bottom 10% of the last year
    df['liq_floor'] = df['net_liquidity'].rolling(252).quantile(0.10)
    
    # 3. GARCH(1,1) Volatility Surface
    # Using an expanding window or long rolling window for stability
    returns = df['sp_ret'].tail(1000) * 100 # Focus on recent regime for fit
    am = arch_model(returns, vol='Garch', p=1, q=1, dist='Normal')
    res = am.fit(disp='off')
    
    # Forecast/Extract current conditional volatility
    latest_vol = res.conditional_volatility[-1] / 100
    vol_threshold = df['sp_ret'].rolling(252).std().quantile(0.90)

    # 4. The V3 Decision Matrix (Logic Upgrade)
    # Veto triggers if:
    # A) Liquidity is at a local 1-year low AND 
    # B) GARCH Vol is higher than 90% of the year's realized vol
    
    current_liq = df['net_liquidity'].iloc[-1]
    current_floor = df['liq_floor'].iloc[-1]
    
    is_liquidity_crisis = current_liq <= current_floor
    is_volatility_clustering = latest_vol > vol_threshold

    if is_liquidity_crisis and is_volatility_clustering:
        print(f"VETO: Regime Shift Detected. Liquidity Floor Hit: {current_liq:.2f}")
        return True # HALT
        
    print(f"PASS: Signals Nominal. Vol: {latest_vol:.4f} | Liq: {current_liq:.2f}")
    return False # PROCEED
