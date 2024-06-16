import pvporcupine
from pvrecorder import PvRecorder
import argparse
import wave
import struct
from datetime import datetime
import os
from dotenv import load_dotenv
import time
from pydub import AudioSegment
import base64
import replicate

load_dotenv()

api_key = os.getenv('API_KEY')
replicate.api_token = os.getenv('REPLICATE_API_TOKEN')

keyword_path = "./wake_word/Атмосфера_ru_windows_v3_0_0.ppn"
model_path = "./wake_word/porcupine_params_ru.pv"

def measure_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Функция '{func.__name__}' выполнялась {end_time - start_time:.6f} секунд")
        return result
    return wrapper

# @measure_time
# def convert_wav_to_mp3(input_file):
#     audio = AudioSegment.from_wav(input_file)
#     mp3_data = BytesIO()
#     audio.export(mp3_data, format="mp3")
#     mp3_data.seek(0)
#     return mp3_data

@measure_time
def trascribe_audio_file(input_audio_file):
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
    return output

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--audio_device_index', help='Index of audio device', type=int, default=0)
    parser.add_argument('--output_path', help='Absolute path to recorded audio', default="audio.wav")
    args = parser.parse_args()

    current_audio_file = None
    if args.output_path is not None:
        current_audio_file = os.path.abspath(args.output_path)

    porcupine = pvporcupine.create(
        access_key=api_key,
        keyword_paths=[keyword_path],
        model_path=model_path
    )

    recorder = PvRecorder(
        frame_length=porcupine.frame_length,
        device_index=args.audio_device_index)
    recorder.start()

    wav_file = None
    if current_audio_file is not None:
        wav_file = wave.open(current_audio_file, "w")
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)

    print('Listening ... (press Ctrl+C to exit)')

    try:
        while True:
            pcm = recorder.read()
            result = porcupine.process(pcm)

            if wav_file is not None:
                wav_file.writeframes(struct.pack("h" * len(pcm), *pcm))

            if result >= 0:
                print('[%s] Detected Атмосфера' % (str(datetime.now())))
                print(trascribe_audio_file(current_audio_file))
    except KeyboardInterrupt:
        print('Stopping ...')
    finally:
        recorder.delete()
        porcupine.delete()
        if wav_file is not None:
            wav_file.close()