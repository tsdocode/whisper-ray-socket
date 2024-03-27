import pyaudio
import uuid
from websockets.sync.client import connect

CHUNK = 2048  # Adjust chunk size if needed for better performance
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK_DURATION = 3  # Duration of each chunk in seconds


def realtime_transcription():
    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
    )
    
    client_id = str(uuid.uuid4())

    print("Real-time transcription started. Press Ctrl+C to stop.")
    try:
        while True:
            audio_data = b""
            for _ in range(int(RATE / CHUNK * CHUNK_DURATION)):
                audio_data += stream.read(CHUNK, exception_on_overflow=False)
            
            with connect(f"ws://localhost:8000/{client_id}") as websocket:
                # Send the audio data
                # websocket.send(client_id)
                websocket.send(audio_data)
                
                while True:
                    received = websocket.recv()
                    print(received, end="")
                    print(" ")
                    break

    except KeyboardInterrupt:
        print("Real-time transcription stopped.")

    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()


if __name__ == "__main__":
    realtime_transcription()
