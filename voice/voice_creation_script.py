from elevenlabs import generate, save, set_api_key
from environs import Env

from voice.text_edited import TEXT
# from voice.text import TEXT

env: Env = Env()
env.read_env('.env')
set_api_key(env("ELEVEN_API_KEY"))


for key, value in TEXT.items():
    print()
    if isinstance(value, list):
        for num, v in enumerate(value):
            audio = generate(
                text=v,
                voice="Thomas",
                model="eleven_multilingual_v2"
            )

            save(audio, filename=f"{key}_{num}.mp3")
    else:
        audio = generate(
            text=value,
            voice="Thomas",
            model="eleven_multilingual_v2"
        )

        save(audio, filename=f"{key}.mp3")
