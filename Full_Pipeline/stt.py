#!/usr/bin/env -S poetry run python3
from openai import OpenAI
from pydub import AudioSegment
from pydub.audio_segment import NamedTemporaryFile
from pydub.silence import db_to_float
import sounddevice as sd
import soundfile as sf

# Create openai client
client = OpenAI()

# Set the recording parameters
samplerate = 48000  # Sample rate (Hz)

# Record audio until silence is detected
myrecording: list[AudioSegment] = []
mean_sound_level = 0.5

print("Recording...")
for i in range(5):
    rec = sd.rec(samplerate * 2, samplerate=samplerate, channels=1)
    sd.wait()

    with NamedTemporaryFile(suffix=".wav") as temp:
        sf.write(temp, rec, samplerate, format="wav")

        # Get the sound level of the audio segment
        segment: AudioSegment = AudioSegment.from_wav(temp)
        myrecording.append(segment)
        sound_level = db_to_float(segment.dBFS)
        print(mean_sound_level, sound_level)

        # If the sound level is significantly lower than the previous sound level, break the loop
        if sound_level < mean_sound_level - 0.05:
            break
        else:
            mean_sound_level = (sound_level + mean_sound_level) / 2

print("Recording finished.")

# Save the recorded audio to a file
audio = AudioSegment.empty()
for segment in myrecording:
    audio += segment

with NamedTemporaryFile(suffix=".wav") as record:
    audio.export(record, format="wav")
    print(f"Audio saved")

    # Transcribe the audio
    transcription = client.audio.translations.create(model="whisper-1", file=record.file, response_format="verbose_json")
    # Print the transcription
    print(transcription)