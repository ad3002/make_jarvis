import pvporcupine
from pvrecorder import PvRecorder
import argparse
import os
import struct
import tempfile

from dotenv import load_dotenv
from openai import OpenAI
from stt import get_wav_file
from agent import Agent
from tts import interrupt_tts

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--audio_device_index', help='Index of input audio device.', type=int, default=0)
    parser.add_argument('--audio_buffer_file', help='Absolute path to recorded audio.', default="./data/current.wav")
    args = parser.parse_args()

    audio_buffer_file_name = args.audio_buffer_file
    audio_device_index = args.audio_device_index
    pvporcupine_sensitivities = 0.9
    proactive_frequency_sec = 10
    keyword2command = {
        0: 'wakeword',
        1: 'stopword',
        2: 'interrupt',
    }

    load_dotenv()
    api_key = os.getenv('API_KEY')
    openai_key = os.getenv('OPENAI_KEY')
    wake_keyword_path = "./wake_word/Милый_ru_mac_v3_0_0.ppn"
    stop_keyword_path = "./wake_word/Хватит_ru_mac_v3_0_0.ppn"
    interrupt_path = "./wake_word/Достаточно_ru_mac_v3_0_0.ppn"
    model_path = "./wake_word/porcupine_params_ru.pv"

    llm_client = OpenAI(api_key=openai_key)

    porcupine = pvporcupine.create(
            access_key=api_key,
            model_path=model_path,
            keyword_paths=[wake_keyword_path, stop_keyword_path, interrupt_path],
            sensitivities=[pvporcupine_sensitivities, pvporcupine_sensitivities, pvporcupine_sensitivities])

    # NUM_FRAMES = porcupine.frame_length
    FRAME_DURATION = 32
    SAMPLE_RATE = 16000
    NUM_FRAMES = int(SAMPLE_RATE * FRAME_DURATION / 1000)
    recorder = PvRecorder(
        frame_length=NUM_FRAMES,
        device_index=audio_device_index)
    recorder.start()

    current_audio_file_name = os.path.abspath(audio_buffer_file_name)
    wav_file = get_wav_file(current_audio_file_name)

    settings = {
        "proactive_frequency_sec": proactive_frequency_sec,
        "wav_file": wav_file,
        "current_audio_file_name": current_audio_file_name,
        "memory_debug_thread": False,
        "proactive_actions_thread": False,
    }

    agent = Agent(llm_client, settings)
    agent.start()

    # vad = webrtcvad.Vad()
    # vad.set_mode(1)  # Устанавливаем режим VAD (0-3), где 3 - самый чувствительный


    try:
        while agent.is_alive():
            pcm = recorder.read()
            result = porcupine.process(pcm)

            wav_file.writeframes(struct.pack("h" * len(pcm), *pcm))

            # audio_frame = np.array(pcm, dtype=np.int16).tobytes()
            # print("Processing ...")
            # print(audio_frame)

            # is_speech = vad.is_speech(audio_frame, SAMPLE_RATE)

            # if is_speech:
            #     wav_file.writeframes(struct.pack("h" * len(pcm), *pcm))
            #     print("Speech detected!")

            if result >= 0:
                print("Wake word detected:", keyword2command[result])
                
                # wav = read_audio(current_audio_file_name, sampling_rate=SAMPLE_RATE)
                # print(wav)
                # speech_tim    estamps = get_speech_timestamps(wav, model, sampling_rate=SAMPLE_RATE)
                # print(speech_timestamps)

                # input("Continue?")

                current_audio_content = open(current_audio_file_name, "rb").read()
                temp_audio_file_name = tempfile.mktemp(suffix=".wav")
                with open(temp_audio_file_name, "wb") as f:
                    f.write(current_audio_content)

                agent.add_event({'type': keyword2command[result], 'result': None, 'current_audio_file_name': temp_audio_file_name})
                
                if wav_file is not None:
                    wav_file.close()
                os.unlink(current_audio_file_name)
                wav_file = get_wav_file(current_audio_file_name)

    except KeyboardInterrupt:
        print('Stopping ...')
        agent.stop()
    finally:
        recorder.stop()
        recorder.delete()
        porcupine.delete()
        if wav_file is not None:
            wav_file.close()
