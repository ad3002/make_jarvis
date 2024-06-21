import openai
import os
import argparse
from pydub import AudioSegment
import math
import subprocess
from dotenv import load_dotenv

load_dotenv()

# Инициализация клиента OpenAI
api_key = os.getenv("OPENAI_KEY")
client = openai.OpenAI(api_key=api_key)

def convert_to_mp3(input_file, output_file):
    command = [
        "ffmpeg",
        "-i", input_file,
        "-vn",
        "-ar", "44100",
        "-ac", "2",
        "-b:a", "192k",
        output_file
    ]
    subprocess.run(command, check=True)

def transcribe_audio(audio_file_path):
    # Загрузка аудиофайла
    audio = AudioSegment.from_file(audio_file_path)
    
    # Длительность сегмента в миллисекундах (25 минут)
    segment_length = 25 * 60 * 1000
    
    # Разделение аудио на сегменты
    segments = math.ceil(len(audio) / segment_length)
    
    full_transcript = ""
    
    for i in range(segments):
        # Извлечение сегмента
        start = i * segment_length
        end = (i + 1) * segment_length
        segment = audio[start:end]
        
        # Сохранение сегмента во временный файл
        temp_filename = f"temp_segment_{i}.mp3"
        segment.export(temp_filename, format="mp3")
        
        # Открытие и отправка файла в API
        with open(temp_filename, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            transcript = response["text"]
        
        # Добавление транскрипции к полному тексту
        full_transcript += transcript + " "
        
        # Удаление временного файла
        os.remove(temp_filename)
    
    return full_transcript.strip()

def main():
    parser = argparse.ArgumentParser(description="Транскрибирование аудио/видео файла с помощью OpenAI Whisper API")
    parser.add_argument("input_file", help="Путь к входному аудио/видео файлу")
    parser.add_argument("output_file", help="Путь к выходному файлу с транскрипцией")
    args = parser.parse_args()

    # Проверяем расширение файла
    _, ext = os.path.splitext(args.input_file)
    if ext.lower() not in ['.mp3', '.wav', '.m4a']:
        print("Конвертирование файла в MP3...")
        temp_audio = "temp_audio.mp3"
        convert_to_mp3(args.input_file, temp_audio)
        input_file = temp_audio
    else:
        input_file = args.input_file

    print("Начало транскрибирования...")
    transcript = transcribe_audio(input_file)

    # Сохранение транскрипции в файл
    with open(args.output_file, "w", encoding="utf-8") as f:
        f.write(transcript)

    print(f"Транскрипция сохранена в файл: {args.output_file}")

    # Удаление временного аудиофайла, если он был создан
    if input_file != args.input_file:
        os.remove(input_file)

if __name__ == "__main__":
    main()
