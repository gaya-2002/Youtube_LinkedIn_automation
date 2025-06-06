from crewai.tools import BaseTool
import subprocess
import os
import glob

from openai import OpenAI


import glob
import wave
import contextlib
import soundfile as sf
import numpy as np
from scipy.io import wavfile

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

client = OpenAI()



class YouTubeCaptionAudioTool(BaseTool):
    name: str = "YouTube_Caption_Downloader"
    description: str = (
        "Downloads English captions from the given YouTube URL "
    )
    state: any = Field(default=None)
    audio_filename: str = Field(default=None)
    transcript_filename: str= Field(default=None)
    chat_id: any= Field(default=None)

    def __init__(self,state):
        super().__init__(state=state,chat_id=id)
        self.state=state
        self.chat_id=id
        self.audio_filename= self.state.get(self.chat_id,"downloaded_audio_path")
        self.transcript_filename=str(Path(self.state.get(self.chat_id,"Blog_output")).parent/"transcript.txt")
        self.state.set(self.chat_id,"transcript_path",self.transcript_filename)

    def get_wav_duration(self,file_path):
        with contextlib.closing(wave.open(file_path, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            return frames / float(rate)

    def chunk_audio(self,audio_path, chunk_length_sec=60):
        sample_rate, data = wavfile.read(audio_path)
        total_samples = data.shape[0]
        chunk_size = sample_rate * chunk_length_sec

        chunks = []
        for start in range(0, total_samples, chunk_size):
            end = min(start + chunk_size, total_samples)
            chunk_data = data[start:end]
            chunk_path = str( Path(self.audio_filename)/ "chunk_" / f"{len(chunks)}.wav" )
            sf.write(chunk_path, chunk_data, sample_rate)
            chunks.append(chunk_path)
        return chunks

    def _run(self, url: str) -> str:
        
        try:
            os.makedirs(self.audio_filename, exist_ok=True)

            # Output filename template with .wav extension
            output_template = os.path.join(self.audio_filename, "%(title).200s.%(ext)s")

            # Run yt-dlp to download and convert audio to WAV
            subprocess.run([
                "yt-dlp",
                "-x",  # extract audio
                "--audio-format", "wav",  # convert to .wav
                "-o", output_template,  # output path template
                url
            ], check=True)


        except subprocess.CalledProcessError as e:
            return f"Failed to download captions or audio: {e}"


        print("Generating Transcription")

    #Get the first .wav file in the directory
        audio_path = str(glob.glob(os.path.join(self.audio_filename, "*.wav"))[0])

        # Chunk the audio file into 60s segments
        chunks = self.chunk_audio(audio_path, chunk_length_sec=60)

        # Transcribe each chunk
        full_transcription = ""
        for i, chunk_path in enumerate(chunks):
            print(f"Transcribing chunk {i+1}/{len(chunks)}")
            with open(chunk_path, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file
                )
                full_transcription += transcription.text + " "

        
        with open(self.transcript_filename,'w',encoding='utf-8') as f:
            f.write(full_transcription)

        print(f"Transcription: {full_transcription}")

        return full_transcription