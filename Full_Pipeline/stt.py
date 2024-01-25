#!/usr/bin/env -S poetry run python3
from openai import OpenAI
from pydub import AudioSegment
from pydub.audio_segment import NamedTemporaryFile
from pydub.silence import db_to_float
import sounddevice as sd
import soundfile as sf

def rec():
    # Create openai client
    client = OpenAI()

    # Set the recording parameters
    samplerate = 48000  # Sample rate (Hz)
    detection_threshold = 0.05
    samples_count_per_rec = 2

    # Record audio until silence is detected
    myrecording: list[AudioSegment] = []
    mean_sound_level = 0.5

    print("Recording...")
    while True:
        rec = sd.rec(samplerate * samples_count_per_rec, samplerate=samplerate, channels=1)
        sd.wait()

        with NamedTemporaryFile(suffix=".wav") as temp:
            sf.write(temp, rec, samplerate, format="wav")

            # Get the sound level of the audio segment
            segment: AudioSegment = AudioSegment.from_wav(temp)
            myrecording.append(segment)
            sound_level = db_to_float(segment.dBFS)
            print(f"mean:{mean_sound_level}, level:{sound_level}")

            # If the sound level is significantly lower than the previous sound level, break the loop
            if sound_level < mean_sound_level - detection_threshold:
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
        print(f"Audio saved.")

        # Transcribe the audio
        transcription = client.audio.translations.create(model="whisper-1", file=record.file, response_format="verbose_json")
        return transcription.text
    

if __name__ == "__main__":
    print(rec())