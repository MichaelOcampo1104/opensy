import numpy as np

def generate_lognrmrand(mean_x: float, std_ln_x: float) -> float:
    """Generate a log-normally distributed random variable for a specified mean
    and logarithmic standard deviation.
    """
    mean_ln_x = np.log(mean_x)
    return float(np.random.lognormal(mean_ln_x, std_ln_x))
