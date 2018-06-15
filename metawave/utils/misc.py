import numpy as np

def gaussian(x, mu, sig):
    '''
        Simple univariate gaussian pdf generator
    '''
    if sig == 0:
        return np.array([mu for _ in range(len(x))])
    else: 
        return np.exp(-(x - mu) ** 2 / (2 * sig ** 2))
