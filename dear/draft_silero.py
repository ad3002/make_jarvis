import torch
import pvrecorder
import numpy as np
import soundfile as sf

# Параметры
SAMPLE_RATE = 16000  # Частота дискретизации аудио
FRAME_DURATION = 10  # Длительность фрейма в миллисекундах
NUM_FRAMES = int(SAMPLE_RATE * FRAME_DURATION / 1000)  # Количество сэмплов в одном фрейме

USE_ONNX = False
# Загрузка модели Silero VAD
model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                              model='silero_vad',
                              force_reload=True,
                              onnx=USE_ONNX)
(get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks) = utils

# Функция для записи и анализа аудио
def record_and_detect():
    recorder = pvrecorder.PvRecorder(device_index=-1, frame_length=NUM_FRAMES)
    recorder.start()
    print("Recording... Press Ctrl+C to stop.")
    
    try:
        recorded_frames = []
        audio_buffer = np.zeros((0,), dtype=np.int16)
        
        while True:
            frame = recorder.read()  # Читаем фрейм аудио
            frame_np = np.array(frame, dtype=np.int16)
            audio_buffer = np.concatenate((audio_buffer, frame_np))

            # Проверяем наличие речи
            if len(audio_buffer) > NUM_FRAMES:
                audio_chunk = torch.from_numpy(audio_buffer).float() / 32768.0  # Нормализация
                speech_timestamps = get_speech_timestamps(audio_chunk, model, sampling_rate=SAMPLE_RATE)
                print(speech_timestamps)
                if speech_timestamps:
                    print("Speech detected!")
                    recorded_frames.append(frame_np)
                else:
                    print("Silence.")
                
                # Очистка буфера
                audio_buffer = np.zeros((0,), dtype=np.int16)

    except KeyboardInterrupt:
        print("Recording stopped.")
    finally:
        recorder.stop()
        recorder.delete()
    
    # Сохраняем записанные фреймы в файл
    if recorded_frames:
        recorded_audio = np.concatenate(recorded_frames)
        sf.write("recorded_audio.wav", recorded_audio, SAMPLE_RATE)
        print("Audio saved to recorded_audio.wav")

# Запускаем функцию записи и детектирования
if __name__ == "__main__":
    record_and_detect()
