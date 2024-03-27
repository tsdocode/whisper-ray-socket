from pydub import AudioSegment
import io
import requests
import base64


def split_wav_and_transcribe(wav_file, chunk_duration_ms=30000):
    audio = AudioSegment.from_wav(wav_file)
    total_duration_ms = len(audio)
    chunk_start = 0
    chunk_number = 1

    while chunk_start < total_duration_ms:
        chunk_end = min(chunk_start + chunk_duration_ms, total_duration_ms)
        chunk_audio = audio[chunk_start:chunk_end]

        # Export the chunk to a byte buffer
        wav_buffer = io.BytesIO()
        chunk_audio.export(wav_buffer, format="wav")
        wav_buffer.seek(0)

        # Transcribe the chunk using the Google Cloud Speech-to-Text API
        response = transcribe_audio(wav_buffer)

        print(f"Transcription for chunk {chunk_number}:")
        print(response.text)

        chunk_start = chunk_end
        chunk_number += 1


def transcribe_audio(wav_buffer):
    URL = "http://127.0.0.1:8000/"
    data = {"data": base64.b64encode(wav_buffer.read()).decode("utf-8")}
    response = requests.post(URL, json=data)
    return response


if __name__ == "__main__":
    input_wav_file = "record_out_4.wav"  # Change this to your WAV file
    split_wav_and_transcribe(input_wav_file)
