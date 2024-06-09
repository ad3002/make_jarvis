from datetime import datetime
from helpers import time_it
from helpers import time_it
from tts import do_tts, interrupt_tts
from stt import transcribe_audio_file
from llms import get_answer_from_llm, get_random_ice_break

@time_it
def answer_action(llm_client, 
                 current_audio_file, 
                 st_memory=None, 
                 lt_memory=None,
                 current_transcript=None,
                 ):
    if not current_transcript:
        print(f'[{datetime.now()}] detected Милый')
        transcription = transcribe_audio_file(llm_client, current_audio_file)
    else:
        transcription = current_transcript
    print(transcription)
    anwser = get_answer_from_llm(llm_client, transcription, st_memory=st_memory, lt_memory=lt_memory)

    if st_memory is not None:
        st_memory.append(("user", transcription))
        st_memory.append(("assistant", anwser))

    print(anwser)
    interrupt_tts()
    do_tts(anwser)

@time_it
def proactive_action(llm_client, st_memory=None, lt_memory=None):
    anwser = get_random_ice_break(llm_client, st_memory=st_memory, lt_memory=lt_memory)

    if st_memory is not None:
        st_memory.append(("assistant", anwser))
    
    print(anwser)
    do_tts(anwser)

