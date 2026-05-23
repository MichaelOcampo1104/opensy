##################################################################################################################
# Generate_lognrmrand
#
# SubRoutine to generate a log-normally distributed random variable for a specified mean and standard deviation.
#
##################################################################################################################
#
# Input Arguments:
#------------------
# meanX 		Mean value of the variable X
# stdlnX 		Standard deviation of the logarithmic values of the variable X 
# xRandom		The subroutine output --> random variable
#
# Written by: Dr. Ahmed Elkady, University of Southampton, UK
#
##################################################################################################################

import numpy as np

def generate_lognrmrand(mean_x: float, std_ln_x: float) -> float:
    """Generate a log-normally distributed random variable for a specified mean
    and logarithmic standard deviation.
    """
    mean_ln_x = np.log(mean_x)
    return float(np.random.lognormal(mean_ln_x, std_ln_x))
