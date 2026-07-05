#Modal analysis------------------------------------------
EigenVal = ops.eigen('-genBandArpack', 1)
# print("The main eigen value is", EigenVal)
print("The main period is", 2*np.pi/(EigenVal**0.5))
#---------------------------------------------------------