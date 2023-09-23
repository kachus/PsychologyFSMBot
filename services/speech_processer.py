import whisper

import torch
import json
model = whisper.load_model('base')
device = "cuda" if torch.cuda.is_available() else "cpu"

def speech_to_voice_with_path(file_path: str) -> str:
    try:
        audio= whisper.load_audio(file_path)
        transcibed_result = model.transcribe(audio)
        return transcibed_result['text']
    except:
        print('could not transcibe audio')
        return False

def speech_to_voice(file) -> str:
    try:
        transcibed_result = model.transcribe(file)
        return transcibed_result['text']
    except:
        print('could not transcibe audio')
        return False





