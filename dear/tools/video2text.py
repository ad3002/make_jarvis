import openai
import os
import argparse
from pydub import AudioSegment
import math
import subprocess
from dotenv import load_dotenv
import logging
from tqdm import tqdm
import time

# Загрузка переменных окружения из файла .env
load_dotenv()

# Инициализация клиента OpenAI
api_key = os.getenv("OPENAI_KEY")
client = openai.OpenAI(api_key=api_key)

def convert_to_mp3(input_file, output_file):
    logging.info(f"Конвертация {input_file} в MP3...")
    command = [
        "ffmpeg",
        "-i", input_file,
        "-vn",
        "-ar", "44100",
        "-ac", "2",
        "-b:a", "192k",
        output_file
    ]
    with open(os.devnull, 'wb') as devnull:
        subprocess.run(command, check=True, stdout=devnull, stderr=devnull)
    logging.info("Конвертация завершена")

def transcribe_audio(audio_file_path):
    logging.info(f"Начало транскрибирования файла: {audio_file_path}")
    audio = AudioSegment.from_file(audio_file_path)
    
    segment_length = 25 * 60 * 1000
    segments = math.ceil(len(audio) / segment_length)
    
    full_transcript = ""
    
    with tqdm(total=segments, desc="Прогресс транскрибирования", unit="сегмент") as pbar:
        for i in range(segments):
            logging.info(f"Обработка сегмента {i+1} из {segments}")
            start = i * segment_length
            end = (i + 1) * segment_length
            segment = audio[start:end]
            
            temp_filename = f"temp_segment_{i}.mp3"
            segment.export(temp_filename, format="mp3")
            
            with open(temp_filename, "rb") as audio_file:

                transcription = client.audio.transcriptions.create(
                            model="whisper-1", 
                            file=audio_file
                            )
                transcript = transcription.text
            
            full_transcript += transcript + " "
            
            os.remove(temp_filename)
            
            pbar.update(1)
            
            # Имитация дополнительной обработки для более плавного прогресс-бара
            for _ in range(10):
                time.sleep(0.1)
                pbar.update(0)
    
    logging.info("Транскрибирование завершено")
    return full_transcript.strip()

def main():
    parser = argparse.ArgumentParser(description="Транскрибирование аудио/видео файла с помощью OpenAI Whisper API")
    parser.add_argument("input_file", help="Путь к входному аудио/видео файлу")
    parser.add_argument("output_file", help="Путь к выходному файлу с транскрипцией")
    args = parser.parse_args()

    logging.info(f"Начало обработки файла: {args.input_file}")

    _, ext = os.path.splitext(args.input_file)
    if ext.lower() not in ['.mp3', '.wav', '.m4a']:
        temp_audio = "temp_audio.mp3"
        convert_to_mp3(args.input_file, temp_audio)
        input_file = temp_audio
    else:
        input_file = args.input_file

    transcript = transcribe_audio(input_file)

    with open(args.output_file, "w", encoding="utf-8") as f:
        f.write(transcript)

    logging.info(f"Транскрипция сохранена в файл: {args.output_file}")

    if input_file != args.input_file:
        os.remove(input_file)
        logging.info("Временный аудиофайл удален")

    logging.info("Обработка завершена")

if __name__ == "__main__":
    main()