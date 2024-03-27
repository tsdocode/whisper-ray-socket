# Assuming the services module and BufferManager class are already defined as in your provided code
from services import process_vad


class BufferManager:
    def __init__(self, timeout=3) -> None:
        self.buffer = bytearray()
        self.timeout = timeout

    async def add_chunk(self, chunk, chunk_meta):
        ask_buffer = None
        channels = chunk_meta["channels"]
        getsampwidth = chunk_meta["sampwidth"]
        framerate = chunk_meta["framerate"]

        concat_buffer = self.buffer
        concat_buffer.extend(chunk)

        voice_activity = await process_vad(concat_buffer, chunk_meta)

        print(voice_activity)
        
        if len(voice_activity) == 0:
            self.buffer = bytearray()
        else:
            last_voice_event = voice_activity[-1]

            last_voice_index = int(
                last_voice_event["end"] * channels * getsampwidth * (framerate / 16000)
            )
            print(last_voice_index)
            if last_voice_index == len(concat_buffer):
                self.buffer = concat_buffer
            else:
                ask_buffer = self.buffer[:last_voice_index]
                self.buffer = concat_buffer[last_voice_index:]

        timeout_index = self.timeout * channels * getsampwidth * framerate
        
        print(timeout_index)
        if len(self.buffer) > timeout_index:
            print("Timeout split")
            ask_buffer = self.buffer[:timeout_index]
            self.buffer = self.buffer[timeout_index:]

        return ask_buffer