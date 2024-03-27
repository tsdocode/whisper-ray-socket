import base64
import io

from faster_whisper import WhisperModel
from ray import serve
from starlette.requests import Request


@serve.deployment(
    num_replicas=2, ray_actor_options={"num_cpus": 2, "num_gpus": 0}
)
class FasterWhisperServer:
    def __init__(self):
        # Load model
        self.pipeline = WhisperModel("distil-large-v2", compute_type="int8")

    async def __call__(self, http_request: Request) -> str:
        data: str = await http_request.json()

        audio_bytes = base64.b64decode(data["data"])

        audio_file = io.BytesIO(audio_bytes)

        segments, info = self.pipeline.transcribe(
            audio_file, "en", beam_size=1
        )
        text = "".join(segment.text for segment in segments)
        return text


faster_whisper_app = FasterWhisperServer.bind()
