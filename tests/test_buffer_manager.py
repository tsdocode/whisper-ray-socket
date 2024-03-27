import wave
from serve.services import process_asr
from serve.buffer_management import BufferManager


def test_vad_with_wav_file(wav_file_path):
    # Open the WAV file
    with wave.open(wav_file_path, "rb") as wav_file:
        # Create an instance of BufferManager
        buffer_manager = BufferManager()

        # Define chunk size (number of frames per chunk)
        chunk_size = 48000 * 3  # You can adjust the chunk size as needed

        frame_rate = wav_file.getframerate()

        print(f"FRAME RATE: {frame_rate}")

        # Read and process chunks from the WAV file
        chunk = wav_file.readframes(chunk_size)

        while chunk:
            # Add chunk to BufferManager and check for voice activity

            asr_buffer = buffer_manager.add_chunk(
                chunk,
                dict(
                    channels=wav_file.getnchannels(),
                    sampwidth=wav_file.getsampwidth(),
                    framerate=wav_file.getframerate(),
                ),
            )

            if asr_buffer:
                print(f"Buffer to asr: {len(asr_buffer)}")

                asr_result = process_asr(
                    asr_buffer,
                    dict(
                        channels=wav_file.getnchannels(),
                        sampwidth=wav_file.getsampwidth(),
                        framerate=wav_file.getframerate(),
                    ),
                )

                print(asr_result)
                # Print the result (you can also handle it differently based on your needs)

            # Read the next chunk
            chunk = wav_file.readframes(chunk_size)


# Specify the path to your WAV file
wav_file_path = "record_out_2.wav"
test_vad_with_wav_file(wav_file_path)
