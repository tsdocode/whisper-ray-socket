import pyaudio
import io
import requests
import base64

CHUNK = 2048  # Adjust chunk size if needed for better performance
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK_DURATION = 5  # Duration of each chunk in seconds


def transcribe_audio(audio_data):
    URL = "http://127.0.0.1:8000/"  # Replace with the appropriate endpoint
    data = {"data": base64.b64encode(audio_data.read()).decode("utf-8")}
    response = requests.post(URL, json=data)
    return response.text


def realtime_transcription():
    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
    )

    print("Real-time transcription started. Press Ctrl+C to stop.")
    try:
        while True:
            audio_data = b""
            for _ in range(int(RATE / CHUNK * CHUNK_DURATION)):
                audio_data += stream.read(CHUNK)

            import wave

            wav_buffer = io.BytesIO()

            with wave.open(
                wav_buffer, "wb"
            ) as wav_file:  # Note the 'wb' mode for BytesIO
                # Set the parameters as before
                wav_file.setnchannels(1)  # Mono audio
                wav_file.setsampwidth(2)  # Assuming 16-bit audio
                wav_file.setframerate(RATE)

                # Write the frames
                wav_file.writeframes(audio_data)
            # audio_data.write(wav_buffer, format="wav")
            wav_buffer.seek(0)

            transcription = transcribe_audio(wav_buffer)
            print("Transcription:", transcription)
    except KeyboardInterrupt:
        print("Real-time transcription stopped.")

    stream.stop_stream()
    stream.close()
    audio.terminate()


if __name__ == "__main__":
    realtime_transcription()
