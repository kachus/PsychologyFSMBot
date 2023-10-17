import os
import re
from lexicon.lexicon_ru import LEXICON_RU

# v_pat = r'D:\python projects\non_comertial\PsychologyFSMBot\voice\voices'





#это скрипт для моей директории и мак системы (не удаляй!!!)
#
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

def get_file_path(key: str, voices_path=r'D:\python projects\non_comertial\PsychologyFSMBot\voice\voice_new'):
    files = os.listdir(voices_path)
    pattern = re.compile(re.escape(key) + r'\.mp3$', re.IGNORECASE)
    for file in files:
        if re.search(pattern, file):
            file_path = os.path.abspath(os.path.join(voices_path, file))
            print(f"Key: {key}, File Path: {file_path}")
            return file_path
    print(f"Key: {key}, File not found")
    return None
