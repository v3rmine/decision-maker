#!/usr/bin/env -S poetry run python3
from openai import OpenAI
import sounddevice as sd
import soundfile as sf

# Create openai client
client = OpenAI()

# Set the recording parameters
duration = 5
samplerate = 48000  # Sample rate (Hz)
temp = open("temp.wav", 'w+b')

print(f"Record for {duration}s")
rec = sd.rec(samplerate * duration, samplerate=samplerate, channels=1)
sd.wait()
sf.write(temp, rec, samplerate)
print(f"Recording finished in {temp.name}.")

# Transcribe the audio
transcription = client.audio.transcriptions.create(model="whisper-1", file=temp, response_format="verbose_json")
# Print the transcription
print(transcription.text)