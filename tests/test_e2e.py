import pyaudio
import uuid
import websockets
import asyncio

CHUNK = 1024  # Adjust chunk size if needed for better performance
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK_DURATION = 2  # Duration of each chunk in seconds

async def send_audio_data(client_id, audio_data):
    async with websockets.connect(f"ws://192.168.1.8:8000/{client_id}") as websocket:
        await websocket.send(audio_data)
        received = await websocket.recv()
        
        if received:
            print(received, end="", flush=True)


def realtime_transcription():
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    client_id = str(uuid.uuid4())

    print("Real-time transcription started. Press Ctrl+C to stop.")
    try:
        while True:
            audio_data = b""
            for _ in range(int(RATE / CHUNK * CHUNK_DURATION)):
                try:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    audio_data += data
                except Exception as e:
                    print(f"Error reading audio stream: {e}")
                    break
            
            asyncio.run(send_audio_data(client_id, audio_data))

    except KeyboardInterrupt:
        print("Real-time transcription stopped.")
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()

if __name__ == "__main__":
    realtime_transcription()
