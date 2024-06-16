import datetime
from helpers import measure_time
from stt import trascribe_audio_file
from tts import say, interrupt_tts
from llms import get_answer_from_llm, get_random_ice_break

@measure_time
def answer_action(
        current_audio_file,
        st_memory=None,
        lt_memory=None,
        current_transcript=None
    ):
    if not current_transcript:
        print('Detected Атмосфера')
        transcription = trascribe_audio_file(current_audio_file)
    else:
        transcription = current_transcript

    print(transcription)
    answer = get_answer_from_llm(transcription, st_memory=st_memory, lt_memory=lt_memory)

    if st_memory is not None:
        st_memory.append(("user", transcription))
        st_memory.append(("assistant", answer))

    print(answer)

    interrupt_tts()
    say(answer)

@measure_time
def proactive_action(st_memory=None, lt_memory=None):
    answer = get_random_ice_break(st_memory=st_memory, lt_memory=lt_memory)

    if st_memory is not None:
        st_memory.append(("assistant", answer))

    print(answer)
    say(answer)