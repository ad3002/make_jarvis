import pvporcupine
from pvrecorder import PvRecorder
import argparse
import struct
import os
import struct
import multiprocessing
import replicate

from dotenv import load_dotenv
from stt import get_wav_file
from tts import interrupt_tts
from actions import answer_action, proactive_thread

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--audio_device_index', help='Index of audio device', type=int, default=0)
    parser.add_argument('--output_path', help='Absolute path to recorded audio', default="audio.wav")
    args = parser.parse_args()

    proactive_frequency_sec = 10
    keyword2command = {
        0: "wakeword",
        1: "stopword",
        2: "interrupt"
    }

    load_dotenv()
    api_key = os.getenv('API_KEY')
    replicate.api_token = os.getenv('REPLICATE_API_TOKEN')
    wake_keyword_path = "./wake_word/Атмосфера_ru_windows_v3_0_0.ppn"
    stop_keyword_path = "./wake_word/Хватит_ru_windows_v3_0_0.ppn"
    interrupt_keyword_path = "./wake_word/Достаточно_ru_windows_v3_0_0.ppn"
    model_path = "./wake_word/porcupine_params_ru.pv"

    porcupine = pvporcupine.create(
        access_key=api_key,
        keyword_paths=[wake_keyword_path, stop_keyword_path, interrupt_keyword_path],
        model_path=model_path
    )

    FRAME_DURATION = 32
    SAMPLE_RATE = 16000
    NUM_FRAMES = int(SAMPLE_RATE * FRAME_DURATION / 1000)
    recorder = PvRecorder(
        frame_length=NUM_FRAMES,
        device_index=args.audio_device_index)
    recorder.start()

    current_audio_file = None
    wav_file = None
    if args.output_path is not None:
        current_audio_file = os.path.abspath(args.output_path).replace("\\", "/")
        wav_file = get_wav_file(current_audio_file)

    settings = {
        "proactive_frequency_sec": proactive_frequency_sec,
        "wav_file": wav_file,
        "current_audio_file_name": current_audio_file,
        "memory_debug_thread": False,
        "proactive_actions_thread": False
    }

    print("Listening... (press Ctrl+C to exit)")
    event = multiprocessing.Event()
    sound_process = None
    ice_break = multiprocessing.Process(target=proactive_thread, args=(current_audio_file))
    ice_break.start()

    try:
        while True:
            pcm = recorder.read()
            result = porcupine.process(pcm)

            if wav_file is not None:
                wav_file.writeframes(struct.pack("h" * len(pcm), *pcm))

            if result >= 0:
                if wav_file is not None:
                    wav_file.close()
                print('Wake word detected: ', keyword2command[result])
                if keyword2command[result] == 'wakeword':
                    sound_process = multiprocessing.Process(target=answer_action, args=(current_audio_file))
                    sound_process.start()
                elif keyword2command[result] == 'stopword':
                    print('Stopping ...')
                    event.set()
                    if sound_process is not None:
                        sound_process.join()
                    ice_break.join()
                    break
                elif keyword2command[result] == 'interrupt':
                    interrupt_tts()
                    event.set()
                    if sound_process is not None:
                        sound_process.join()
                    ice_break.join()
                else:
                    print(f"Unknown event type: {print('Stopping ...')}")
                os.unlink(current_audio_file)
                wav_file = get_wav_file(current_audio_file)
    except KeyboardInterrupt:
        if sound_process is not None:
            event.set()
            sound_process.join()
            ice_break.join()
        print('Stopping ...')
    finally:
        recorder.stop()
        recorder.delete()
        porcupine.delete()
        if wav_file is not None:
            wav_file.close()