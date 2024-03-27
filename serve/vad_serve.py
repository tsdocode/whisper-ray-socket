import base64
import io
import torch

from ray import serve
from starlette.requests import Request

from vad_utils import read_audio, get_speech_timestamps


@serve.deployment(
    num_replicas=1, ray_actor_options={"num_cpus": 2, "num_gpus": 0}
)
class VADServer:
    def __init__(self):
        # Load model
        model, _ = torch.hub.load(
            repo_or_dir="snakers4/silero-vad",
            model="silero_vad",
            force_reload=True,
            onnx=False,
        )

        self.model = model

    async def __call__(self, http_request: Request) -> str:
        data: str = await http_request.json()

        audio_bytes = base64.b64decode(data["data"])
        framerate = data["meta"]["framerate"]

        print(framerate)

        audio_file = io.BytesIO(audio_bytes)

        audio_file = read_audio(audio_file)

        return get_speech_timestamps(
            audio_file,
            self.model,
            0.46,  # speech prob threshold
            framerate,  # sample rate
            300,  # min speech duration in ms
            20,  # max speech duration in seconds
            600,  # min silence duration
            512,  # window size
            200,  # spech pad ms
        )


vad_app = VADServer.bind()
