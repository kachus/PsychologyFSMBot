from elevenlabs import generate, save, set_api_key
from environs import Env

from voice.text import TEXT

env: Env = Env()
env.read_env('.env')
set_api_key(env("ELEVEN_API_KEY"))
print()

for key, value in TEXT.items():
    print()
    if isinstance(value, list):
        for num, v in enumerate(value):
            audio = generate(
                text=v,
                voice="Michael",
                model="eleven_multilingual_v2"
            )

            save(audio, filename=f"{key}_{num}.mp3")
    else:
        audio = generate(
            text=value,
            voice="Michael",
            model="eleven_multilingual_v2"
        )

        save(audio, filename=f"{key}.mp3")
