import sounddevice as sd
from scipy.io import wavfile
import io

SF = 44100    # sample frequency
REC_TIME = 5  # Seconds


def record(device):
    sd.default.device = device
    myrecording = sd.rec(int(REC_TIME * SF), samplerate=SF, channels=1)
    sd.wait()

    # Create a virtual file to read into MQTT later.
    aud_file = io.BytesIO()
    wavfile.write(aud_file, SF, myrecording)
    # Reset the file seek to 0
    aud_file.seek(0)

