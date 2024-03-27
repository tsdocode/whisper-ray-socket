# File name: serve_quickstart.py
from starlette.requests import Request

from ray import serve


@serve.deployment(
    num_replicas=2, ray_actor_options={"num_cpus": 0.2, "num_gpus": 0}
)
class Sample:
    def __init__(self):
        # Load model
        # self.model = pipeline("translation_en_to_fr", model="t5-small")
        self.content = "Hello there"

    async def __call__(self, http_request: Request) -> str:
        english_text: str = await http_request.json()
        return english_text + self.content


sample_app = Sample.bind()
