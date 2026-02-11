import numpy as np
    import pandas as pd
    from arch import arch_model
    from fredapi import Fred
    
    def run_upgraded_engine(df, FRED_API_KEY, START, END):
        # 1. State Restoration: Ensure baseline columns exist
        df['sp_ret'] = df['sp500'].pct_change()
        df['volatility'] = df['sp_ret'].rolling(6).std()
    
        # 2. High-Freq Liquidity Injection (Net Liquidity = WALCL - TGA - RRP)
        fred = Fred(api_key=FRED_API_KEY)
        print("Fetching weekly liquidity components (TGA, RRP)...")
        tga = fred.get_series('WTREGEN', observation_start=START, observation_end=END)
        rrp = fred.get_series('RRPONTSYD', observation_start=START, observation_end=END)
    
        # Resample and calculate Net Liquidity Z-score
        tga_m = tga.resample('ME').last()
        rrp_m = rrp.resample('ME').last()
        df['net_liquidity'] = df['fed_assets'] - tga_m - rrp_m
        df['net_liquidity_z'] = (df['net_liquidity'] - df['net_liquidity'].rolling(12).mean()) / df['net_liquidity'].rolling(12).std()
    
        # 3. GARCH(1,1) Volatility Surface Upgrade
        print("Fitting GARCH(1,1) model for conditional volatility...")
        garch_data = df['sp_ret'].dropna() * 100
        am = arch_model(garch_data, vol='Garch', p=1, q=1, dist='Normal')
        res = am.fit(disp='off')
        df.loc[garch_data.index, 'garch_volatility'] = res.conditional_volatility / 100
    
        # 4. Decision Gate: Fail-Closed Condition
        df['quarantine_signal'] = (df['garch_volatility'] > df['volatility'].rolling(12).mean()) | (df['net_liquidity_z'] < -1.5)
    
        print("
Upgrade Complete. Invariants Restored.")
        return df[['net_liquidity_z', 'garch_volatility', 'quarantine_signal']]
    
