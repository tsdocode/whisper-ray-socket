import asyncio
import io
import logging
import wave
from queue import Empty

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from faster_whisper import WhisperModel
from ray import serve

logger = logging.getLogger("ray.serve")

fastapi_app = FastAPI()


@serve.deployment(
    num_replicas=2, ray_actor_options={"num_cpus": 2, "num_gpus": 0}
)
@serve.ingress(fastapi_app)
class ASRSocketServer:
    def __init__(self):
        self.clients = {}
        # Load model
        # self.model = pipeline("translation_en_to_fr", model="t5-small")
        self.loop = asyncio.get_running_loop()
        self.pipeline = WhisperModel("distil-large-v2", compute_type="int8")

    def generate_transcribe(self, data, stream_chunks=[]):
        wav_buffer = io.BytesIO()

        with wave.open(
            wav_buffer, "wb"
        ) as wav_file:  # Note the 'wb' mode for BytesIO
            # Set the parameters as before
            wav_file.setnchannels(1)  # Mono audio
            wav_file.setsampwidth(2)  # Assuming 16-bit audio
            wav_file.setframerate(16000)

            # Write the frames
            wav_file.writeframes(data)
        # audio_data.write(wav_buffer, format="wav")
        wav_buffer.seek(0)
        segments, info = self.pipeline.transcribe(
            wav_buffer, "en", beam_size=1
        )

        stream_chunks[:] = [segments]

    async def consume_streamer(self, streamer):
        while True:
            try:
                for segment in streamer:
                    logger.info(f'Yielding token: "{segment.text}"')
                    yield segment.text
                break
            except Empty:
                await asyncio.sleep(0.001)

    @fastapi_app.websocket("/")
    async def handle_request(self, ws: WebSocket) -> None:
        await ws.accept()

        conversation = ""
        try:
            while True:
                data = await ws.receive_bytes()
                streamer = []

                await self.loop.run_in_executor(
                    None, self.generate_transcribe, data, streamer
                )
                response = ""

                print("Transcribe Done")
                async for text in self.consume_streamer(streamer[0]):
                    await ws.send_text(text)
                    response += text
                await ws.send_text("<<Response Finished>>")
                conversation += response
        except WebSocketDisconnect:
            print("Client disconnected.")


faster_whisper_app = ASRSocketServer.bind()
