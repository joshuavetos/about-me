import os
import yfinance as yf
import pandas as pd
import numpy as np
from arch import arch_model
from fredapi import Fred

class VetosProportionalController:
    """
    VETOS v6.0: Proportional Risk Controller
    Implements Recursive GARCH Mean-Reversion and Cross-Asset 'Bond Trap' Detection.
    """
    def __init__(self):
        # Retrieve key from environment variable to prevent credential leakage
        self.api_key = os.getenv("FRED_API_KEY")
        if not self.api_key:
            raise ValueError("Configuration Error: FRED_API_KEY not found in environment.")
        self.fred = Fred(api_key=self.api_key)

    def run_engine(self, start_date: str, end_date: str):
        """
        Executes the systemic risk audit across Equity, Duration, and Liquidity.
        """
        # Multi-Asset Stack: SPY (Equity), TLT (Bonds), DX-Y.NYB (USD)
        tickers = ["SPY", "TLT", "DX-Y.NYB"]
        raw_data = yf.download(tickers, start=start_date, end=end_date, auto_adjust=True)
        
        # Clean MultiIndex and normalize column headers
        df = raw_data['Close'].rename(columns={"DX-Y.NYB": "DXY"}).dropna()
        rets = df.pct_change().dropna()

        # 1. Recursive GARCH Mean-Reversion (Volatility Targeting)
        # Calculates current conditional volatility vs. 5-year rolling median
        garch_input = rets['SPY'] * 100
        am = arch_model(garch_input, vol='Garch', p=1, q=1, dist='Normal')
        res = am.fit(disp='off')
        
        df['current_vol'] = (res.conditional_volatility / 100) * np.sqrt(252)
        df['target_vol'] = df['current_vol'].rolling(window=1260, min_periods=252).median().fillna(0.15)

        # 2. Proportional Scaling (Exposure Gating)
        # risk_weight = target_vol / current_vol (capped at 1.0)
        df['prop_weight'] = (df['target_vol'] / df['current_vol']).clip(0, 1.0)

        # 3. Bond Trap Detection (Systemic Liquidity Kill-Switch)
        # Monitors Dollar/Equity coupling for signs of a liquidity vacuum
        df['corr_spy_dxy'] = rets['SPY'].rolling(63).corr(rets['DXY'])
        
        # Binary Halt: Deep Dollar coupling + Volatility Expansion
        df['trap_signal'] = (df['corr_spy_dxy'].abs() > 0.80) & (df['current_vol'] > df['target_vol'])

        # 4. Final Risk Determination
        # Fail-closed logic: Move to 0% exposure if the Bond Trap is active
        df['final_weight'] = np.where(df['trap_signal'], 0.0, df['prop_weight'])
        
        return df[['final_weight', 'current_vol', 'target_vol', 'trap_signal']]

if __name__ == "__main__":
    # Operational Check
    try:
        controller = VetosProportionalController()
        print("VETOS Engine Initialized: Environment Authenticated.")
    except ValueError as e:
        print(f"Initialization Failed: {e}")
