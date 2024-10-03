import whisper
import pyaudio
import wave
import sys
import tempfile
import time
import torch
from ctypes import *

device = "cuda" if torch.cuda.is_available() else "cpu"
model = whisper.load_model("small", device=device)
print(f"Model is loaded on: {device}")

def benchmark(func):
    """
    Decorator to measure the time taken by a function to execute.

    Args:
        func (function): The function to be benchmarked.

    Returns:
        function: A wrapper function that runs the original function and prints the execution time.
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"{func.__name__} took {elapsed_time:.2f} seconds to run")
        return result
    return wrapper

def py_error_handler(filename, line, function, err, fmt):
    """
    Suppresses ALSA errors to prevent warnings during audio recording.

    Args:
        filename (str): The name of the file where the error occurred.
        line (int): The line number of the error.
        function (str): The name of the function where the error occurred.
        err (int): Error code.
        fmt (str): The error message format.

    Returns:
        None
    """
    return

@benchmark
def transcribe_directly():
    """
    Records audio from the microphone, saves it to a WAV file, and transcribes the audio to text
    using the Whisper model.

    This function sets up an audio stream, handles ALSA warnings, and records until the user 
    presses Enter. After recording, it transcribes the recorded audio using Whisper.

    The transcription is performed in French.

    Returns:
        str: The transcribed text from the recorded audio.
    """

    temp_file = tempfile.NamedTemporaryFile(suffix=".wav")

    sample_rate = 16000
    bits_per_sample = 16
    chunk_size = 1024
    audio_format = pyaudio.paInt16
    channels = 1

    wav_file = wave.open('recording.wav', 'wb')
    wav_file.setnchannels(channels)
    wav_file.setsampwidth(bits_per_sample // 8)
    wav_file.setframerate(sample_rate)

    def callback(in_data, frame_count, time_info, status):
        """
        Callback function for handling audio stream data.

        Args:
            in_data (bytes): Audio data from the microphone.
            frame_count (int): Number of frames in the audio data.
            time_info (dict): Dictionary containing timing information.
            status (int): Status flag.

        Returns:
            tuple: (None, pyaudio.paContinue) to continue the audio stream.
        """
        wav_file.writeframes(in_data)
        return None, pyaudio.paContinue

    # Suppress ALSA warnings (https://stackoverflow.com/a/13453192)
    ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

    c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
    asound = cdll.LoadLibrary('libasound.so')
    asound.snd_lib_error_set_handler(c_error_handler)

    audio = pyaudio.PyAudio()
    stream = audio.open(format=audio_format,
                        channels=channels,
                        rate=sample_rate,
                        input=True,
                        frames_per_buffer=chunk_size,
                        stream_callback=callback)

    input("Press Enter to stop recording...")

    stream.stop_stream()
    stream.close()
    audio.terminate()
    wav_file.close()

    result = model.transcribe('recording.wav', language="french")
    temp_file.close()

    return str(result["text"].strip())

if __name__ == "__main__":
    print(transcribe_directly())