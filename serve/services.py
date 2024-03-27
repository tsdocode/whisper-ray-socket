import io
import wave
import requests
import base64


RAY_PROXY_URL = "http://127.0.0.1:8000/"


def convert_bytes_to_io(bytes_data, channels=1, sampwidth=2, framerate=48000):
    """
    Convert bytes data to an io.BytesIO buffer containing WAV audio.

    :param bytes_data: The raw audio data as bytes.
    :param channels: Number of audio channels. Default is 1 (mono audio).
    :param sampwidth: Sample width in bytes. Default is 2 (16-bit audio).
    :param framerate: Frame rate or sample rate of the audio. Default is 48000 Hz.
    :return: An io.BytesIO buffer containing the WAV audio data.
    """
    wav_buffer = io.BytesIO()

    with wave.open(wav_buffer, "wb") as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sampwidth)
        wav_file.setframerate(framerate)
        wav_file.writeframes(bytes_data)

    wav_buffer.seek(0)  # Rewind the buffer for reading
    return wav_buffer


def process_vad(bytes_data, chunk_meta):
    bytes_data = convert_bytes_to_io(bytes_data, **chunk_meta)
    URL = RAY_PROXY_URL + "vad"
    data = {
        "data": base64.b64encode(bytes_data.read()).decode("utf-8"),
        "meta": {"framerate": chunk_meta["framerate"]},
    }
    response = requests.post(URL, json=data)
    return response.json()


def process_asr(bytes_data, chunk_meta):
    bytes_data = convert_bytes_to_io(bytes_data, **chunk_meta)
    URL = RAY_PROXY_URL + "asr"
    data = {"data": base64.b64encode(bytes_data.read()).decode("utf-8")}
    response = requests.post(URL, json=data)
    return response.text
