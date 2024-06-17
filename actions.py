import time
import random
from helpers import measure_time
from stt import trascribe_audio_file
from tts import say, interrupt_tts
from llms import get_answer_from_llm, get_random_ice_break

# @measure_time
def answer_action(
        current_audio_file,
        current_transcript=None
    ):
    if not current_transcript:
        print('Detected Атмосфера')
        transcription = trascribe_audio_file(current_audio_file)
    else:
        transcription = current_transcript

    print(transcription)
    answer = get_answer_from_llm(transcription)


    print(answer)

    interrupt_tts()
    say(answer, current_audio_file)

# @measure_time
def proactive_action(current_audio_file):
    answer = get_random_ice_break()

    print(answer)
    say(answer, current_audio_file)

def proactive_thread(current_audio_file):
    min_freq = 10
    max_freq = min_freq * 2
    while True:
        time.sleep(random.randint(min_freq, max_freq))
        proactive_action(current_audio_file)