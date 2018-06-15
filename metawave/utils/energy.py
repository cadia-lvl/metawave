import matplotlib.pyplot as plt
import numpy as np

from .audio import aperiodicity, prep_wav

if __name__ == '__main__':
    ap = '/home/atli/Work/taco/datasets/mini/ismData/wavs/ism_1140_0024314995.wav'
    audio = prep_wav(ap, 22000)
    ap = aperiodicity(audio, 22000)
    print(ap.shape)
    plt.imshow(ap)
    plt.show()
