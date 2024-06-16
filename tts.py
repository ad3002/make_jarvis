import os
import replicate
import winsound
import requests
import signal
from dotenv import load_dotenv

load_dotenv()

replicate.api_token = os.getenv('REPLICATE_API_TOKEN')

def prepare_text(text):
    escaped_text = text.replace('"', '\\"')
    return escaped_text

def say(text):
    text = prepare_text(text)
    output = replicate.run(
        "lucataco/xtts-v2:684bc3855b37866c0c65add2ff39c78f3dea3f4ff103a436465326e0f438d55e",
        input={
            "text": text,
            "speaker": "https://replicate.delivery/pbxt/Jt79w0xsT64R1JsiJ0LQRL8UcWspg5J4RFrU6YwEKpOT1ukS/male.wav",
            "language": "ru",
            "cleanup_voice": False
        }
    )
    audio_file = "output.wav"
    response = requests.get(output)
    with open(audio_file, "wb") as f:
        f.write(response.content)
    winsound.PlaySound(audio_file, winsound.SND_FILENAME)
    os.remove(audio_file)

def interrupt_tts():
    os.kill(os.getpid(), signal.SIGINT)

def tts_thread(text):
    try:
        say(text)
    except Exception as e:
        print(f'TTS interrupted: {e}')