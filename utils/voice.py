from faster_whisper import WhisperModel
import tempfile

_model = None


def get_model():
    global _model
    if _model is None:
        _model = WhisperModel(
            "small",
            device="cpu",
            compute_type="int8"
        )
    return _model


def speech_to_text(audio_path):

    model = get_model()

    segments, info = model.transcribe(
        audio_path,
        language="en",
        beam_size=5
    )

    text = ""

    for segment in segments:
        text += segment.text + " "

    return text.strip()


def speech_bytes_to_text(audio_bytes):

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".wav"
    ) as temp_audio:

        temp_audio.write(audio_bytes)

        temp_path = temp_audio.name

    return speech_to_text(temp_path)