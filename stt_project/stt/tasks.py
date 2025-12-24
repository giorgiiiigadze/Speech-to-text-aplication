from celery import shared_task
from pydub import AudioSegment
import numpy as np
import json
import os

from .models import AudioFile

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={"max_retries": 3})
def generate_waveform_task(self, audio_id, points=120):
    audio = AudioFile.objects.get(id=audio_id)

    try:
        sound = AudioSegment.from_file(audio.file.path)
        samples = np.array(sound.get_array_of_samples())

        if sound.channels == 2:
            samples = samples.reshape((-1, 2)).mean(axis=1)

        samples = np.abs(samples)
        max_val = np.max(samples)

        if max_val == 0:
            waveform = [0] * points
        else:
            samples = samples / max_val
            chunk_size = len(samples) // points
            waveform = [
                float(np.max(samples[i:i + chunk_size]))
                for i in range(0, len(samples), chunk_size)
            ][:points]

        waveforms_dir = os.path.join(os.path.dirname(audio.file.path), "waveforms")
        os.makedirs(waveforms_dir, exist_ok=True)

        waveform_file_path = os.path.join(
            waveforms_dir, f"{audio.id}_waveform.json"
        )

        with open(waveform_file_path, "w") as f:
            json.dump(waveform, f)

        audio.waveform_file.name = f"audio/waveforms/{audio.id}_waveform.json"
        audio.status = "done"

    except Exception as e:
        print("TASK ERROR:", e)
        audio.status = "error"

    finally:
        audio.save()
