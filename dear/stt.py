from helpers import time_it
import os
import wave

def get_wav_file(current_audio_file):
    wav_file = wave.open(current_audio_file, "w")
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(16000)
    return wav_file

@time_it
def wav_to_mp3(file_name, outpit_file_name):
    command = f"ffmpeg -loglevel quiet -y -i {file_name} {outpit_file_name}"
    os.system(command)

def remove_wake_word(text, wake_word="Милый"):
    wake_word_lc = wake_word.lower()
    text = text.replace(wake_word, "").replace(wake_word_lc, "").strip()
    return text.strip(",")

@time_it
def transcribe_audio_file(client, inpit_audio_file, wake_word="Милый"):
    inpit_mp3_file = inpit_audio_file.replace(".wav", ".mp3")
    wav_to_mp3(inpit_audio_file, inpit_mp3_file)
    audio_data = open(inpit_mp3_file, "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_data
        )
    text = transcription.text
    # text = remove_wake_word(transcription.text, wake_word)
    return text