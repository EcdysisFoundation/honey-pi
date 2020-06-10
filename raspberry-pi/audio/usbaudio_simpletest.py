import sounddevice as sd
import matplotlib.pyplot as plt

from scipy.io import wavfile
from scipy import signal
import numpy as np
import io
from scipy.io.wavfile import write


FS = 11000    # sample frequency
REC_TIME = 2  # Seconds


def record():
    sd.default.device = 1
    sd.default.samplerate = FS
    sd.default.channels = 1

    recording = sd.rec(int(REC_TIME * FS), blocking=True)
    # write('output.wav', SF, myrecording)  # Save as WAV file



    N = recording.shape[0]
    print(N, recording.shape)
    L = N / FS
    tuckey_window = signal.tukey(N, 0.01, True)  # generate the Tuckey window, widely open, alpha=0.01
    ysc = recording[:, 0] * tuckey_window  # applying the Tuckey window
    yk = np.fft.rfft(ysc, int(2500*L*2))   # real to complex DFT
    k = np.arange(yk.shape[0])
    freqs = k / L
    print(freqs)
    print(np.abs(yk))
    fig, ax = plt.subplots()
    ax.plot(freqs, np.abs(yk))
    plt.savefig('fft.png')


record()




