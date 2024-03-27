from faster_whisper import WhisperModel


asr_pipeline = WhisperModel("distil-large-v2", compute_type="int8")

segments, info = asr_pipeline.transcribe(
    "/Users/sangtnguyen/Coding/Personal/asr-example/VoiceStreamAI/audio_files/afe86a5f-1be9-4938-a911-da833abf5a1a_0.wav",
    beam_size=1,
    max_new_tokens=256,
)

for segment in segments:
    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
