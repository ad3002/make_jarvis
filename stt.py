from helpers import measure_time
import os
import replicate
import wave
from dotenv import load_dotenv

load_dotenv()

replicate.api_token = os.getenv('REPLICATE_API_TOKEN')

def get_wav_file(current_audio_file):
    wav_file = wave.open(current_audio_file, "w")
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(16000)
    return wav_file

def remove_wake_word(text, wake_word="Атмосфера"):
    wake_word_lc = wake_word.lower()
    text = text.replace(wake_word, "").replace(wake_word_lc, "").strip()
    return text.strip(",")

@measure_time
def trascribe_audio_file(input_audio_file, wake_word="Атмосфера"):
    output = ""
    with open(input_audio_file, 'rb') as file:
        input = {
            "audio": file,
            "batch_size": 6
        }

        output = replicate.run(
            "vaibhavs10/incredibly-fast-whisper:3ab86df6c8f54c11309d4d1f930ac292bad43ace52d10c80d87eb258b3c9f79c",
            input=input
        )
    text = output["text"]
    text = remove_wake_word(text, wake_word)
    return text