import os
import re
from lexicon.lexicon_ru import LEXICON_RU

v_pat = r'D:\python projects\non_comertial\PsychologyFSMBot\voice\voices'


def get_file_path(key: str, voices_path=r'D:\python projects\non_comertial\PsychologyFSMBot\voice\voices'):
    files = os.listdir(voices_path)
    pattern = re.compile(re.escape(key) + r'\.mp3$', re.IGNORECASE)
    for file in files:
        if re.search(pattern, file):
            file_path = os.path.abspath(os.path.join(voices_path, file))
            print(f"Key: {key}, File Path: {file_path}")
            return file_path
    print(f"Key: {key}, File not found")
    return None
