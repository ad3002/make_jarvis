import webrtcvad
import pvrecorder
import numpy as np
import soundfile as sf

# Параметры
SAMPLE_RATE = 16000  # Частота дискретизации аудио
FRAME_DURATION = 30  # Длительность фрейма в миллисекундах
NUM_FRAMES = int(SAMPLE_RATE * FRAME_DURATION / 1000)  # Количество сэмплов в одном фрейме

# Создаем объект VAD
vad = webrtcvad.Vad()
vad.set_mode(2)  # Устанавливаем режим VAD (0-3), где 3 - самый чувствительный

# Функция для записи и анализа аудио
def record_and_detect():
    recorder = pvrecorder.PvRecorder(device_index=-1, frame_length=NUM_FRAMES)
    recorder.start()
    print("Recording... Press Ctrl+C to stop.")
    
    try:
        recorded_frames = []
        while True:
            frame = recorder.read()  # Читаем фрейм аудио
            audio_frame = np.array(frame, dtype=np.int16).tobytes()  # Конвертируем в байты
            
            is_speech = vad.is_speech(audio_frame, SAMPLE_RATE)  # Проверяем на голосовую активность
            
            if is_speech:
                print("Speech detected!")
                recorded_frames.append(frame)
            else:
                print("Silence.")
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
