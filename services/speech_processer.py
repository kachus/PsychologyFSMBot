from pathlib import Path

import whisper
from aiogram import Bot
from aiogram.types import Message
import torch


model = whisper.load_model('base')
device = "cuda" if torch.cuda.is_available() else "cpu"


def speech_to_voice_with_path(file_path: str) -> str or tuple:
    try:
        audio = whisper.load_audio(file_path)
        transcibed_result = model.transcribe(audio, language='ru')
        return transcibed_result['text']
    except Exception as e:
        print('could not transcibe audio')
        return e.args

#
# def speech_to_voice(file) -> str:
#     try:
#         transcibed_result = model.transcribe(file, language='ru')
#         return transcibed_result['text']
#     except:
#         print('could not transcibe audio')
#         return False

async def download_file_from_chat(bot:Bot,
                        message: Message) -> str: #returns file path
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_on_disk = Path(Path.cwd(), 'user_voices', f"{file_id}.ogg")
    await bot.download_file(file_path, destination=file_on_disk.as_posix())
    print(speech_to_voice_with_path(file_path=file_on_disk))  # FIXME добавить апдейт в бд текст из аудио
    return file_on_disk
    # os.remove(path=file_on_disk)
