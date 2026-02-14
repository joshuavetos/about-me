import numpy as np
from scipy.stats import differential_entropy

def verify_signal_integrity(data_stream):
    """
    Firewall for Synthetic/Manipulated Data.
    Veto fires if Information Complexity (Entropy) is lost.
    """
    noise = np.diff(data_stream)
    counts, _ = np.histogram(noise, bins=10, density=True)
    ent_ratio = differential_entropy(counts + 1e-6) / 2.5
    
    # Audit Result
    is_safe = ent_ratio > 0.40
    return is_safe, ent_ratio
