import sounddevice as sd
import soundfile as sf
from faster_whisper import WhisperModel

# Load model only once
model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8"
)


def record_audio(
    filename="recording.wav",
    duration=5,
    samplerate=16000
):
    recording = sd.rec(
        int(duration * samplerate),
        samplerate=samplerate,
        channels=1,
        dtype="float32"
    )

    sd.wait()

    sf.write(
        filename,
        recording,
        samplerate
    )

    return filename


def speech_to_text(audio_path):

    segments, info = model.transcribe(
        audio_path,
        language="en",
        beam_size=5
    )

    text = ""

    for segment in segments:
        text += segment.text + " "

    return text.strip()

import tempfile


def speech_bytes_to_text(audio_bytes):

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".wav"
    ) as temp_audio:

        temp_audio.write(audio_bytes)

        temp_path = temp_audio.name

    return speech_to_text(temp_path)