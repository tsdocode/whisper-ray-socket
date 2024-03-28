import asyncio
import io
import logging
import wave
from queue import Empty

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from faster_whisper import WhisperModel
from buffer_management import BufferManager
from ray import serve
from services import process_asr
from uuid import uuid4

logger = logging.getLogger("ray.serve")

fastapi_app = FastAPI()


@serve.deployment(num_replicas=1, ray_actor_options={"num_cpus": 2, "num_gpus": 0})
@serve.ingress(fastapi_app)
class ASRServer:
    def __init__(self):
        # Load model
        self.buffer = {}

    @fastapi_app.websocket("/{client_id}")
    async def handle_request(self, ws: WebSocket, client_id) -> None:
        await ws.accept()
        
        if client_id not in self.buffer:
            self.buffer[client_id] = BufferManager()

        try:
            while True:
                # client_id = await ws.receive_text()
                # if client_id not in self.buffer:
                #     self.buffer[client_id] = BufferManager()
                
                data = await ws.receive_bytes()
                
                meta = dict(
                    channels=2,
                    sampwidth=2,
                    framerate=16000,
                )

                asr_chunk = await self.buffer[client_id].add_chunk(data, meta)
                
                print(len(self.buffer[client_id].buffer))
                
                if asr_chunk:
                    print("ASR CHUNK")
                    print(len(asr_chunk))
                    text = await process_asr(asr_chunk, meta)
                    
                    print(text)
                    await ws.send_text(text)
                else:
                    await ws.send_text(" ")
        except WebSocketDisconnect:
            print("Client disconnected.")
            # self.buffer.pop(client_id)


asr_app = ASRServer.bind()
