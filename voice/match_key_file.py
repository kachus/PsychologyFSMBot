import os
import re
from container import root_dir


# это скрипт для моей директории и мак системы (не удаляй!!!) ок ))

# def get_file_path(key: str, voices_path='/Users/evgenia/PycharmProjects/PsychologyBot copy/voice/voice_new'):
#     files = os.listdir(voices_path)
#     pattern = re.compile(re.escape(key) + r'.mp3$', re.IGNORECASE)
#     for file in files:
#         if re.search(pattern, file):
#             file_path = os.path.abspath(os.path.join(voices_path, file))
#             print(f"Key: {key}, File Path: {file_path}")
#             return file_path
#     print(f"Key: {key}, File not found")
#     return None
#
# это скрипт подходит под все системы
def get_file_path(key: str, voice_dir_path='voice', voice_sub_dir='voice_new'):
    """
    Функция получает на вход ключ к словарю, название глобюальнгой папке где хранятся голос и подпакпт в которых хранятся записи
    Функция адаптирована под все ОС
    """
    voices_path = os.path.normpath(os.path.join(root_dir, voice_dir_path, voice_sub_dir))
    files = os.listdir(voices_path)
    pattern = re.compile(re.escape(key) + r'\.mp3$', re.IGNORECASE)
    for file in files:
        if re.search(pattern, file):
            file_path = os.path.abspath(os.path.join(voices_path, file))
            print(f"Key: {key}, File Path: {file_path}")
            return file_path
    print(f"Key: {key}, File not found")
    return None
