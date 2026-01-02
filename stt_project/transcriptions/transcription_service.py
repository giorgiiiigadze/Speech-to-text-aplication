import whisper
from .services import generate_tag

_model = None

def transcribe_audio(file_path: str):
    global _model

    if _model is None:
        _model = whisper.load_model("base", device="cpu")

    result = _model.transcribe(file_path, fp16=False)

    text = result["text"].strip()
    tag = generate_tag(text)

    return text, tag
