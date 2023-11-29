import subprocess
import sys

# Provide audio file as the first argument to this script.
print(sys.argv[1])

ffmpeg_cmd = f"ffmpeg -i {sys.argv[1]} -ar 16000 -ac 1 -c:a pcm_s16le talk.wav"
subprocess.run(ffmpeg_cmd.split())

WHISPER_BASE_PATH = "../whisper.cpp"
whisper_cmd = f"{WHISPER_BASE_PATH}/main -m {WHISPER_BASE_PATH}/models/ggml-base.en.bin -f talk.wav -otxt -pp"
subprocess.run(whisper_cmd.split())

# TODO pipe this to the summariser now. Needs another prompt.
