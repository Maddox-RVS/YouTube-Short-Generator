from rich.console import Console
from pathlib import Path
import soundfile as sf
import warnings
import whisper
import torch
import sys
import os

class TextToSpeechGenerator:
    def __init__(self, tone: str):
        self.tone = tone

        # --------------------------------------------------------------
        # Suppress stdout and stderr from the TTS library during import
        # --------------------------------------------------------------
        old_stdout_fd = os.dup(1)
        old_stderr_fd = os.dup(2)
        devnull_fd = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull_fd, 1)
        os.dup2(devnull_fd, 2)
        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout = sys.stderr = open(os.devnull, 'w')

        from qwen_tts import Qwen3TTSModel
        self.model = Qwen3TTSModel.from_pretrained(
            'Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign',
            device_map='cpu',
            dtype=torch.float32,
            attn_implementation='sdpa',)
        self.console = Console()
        
        os.dup2(old_stdout_fd, 1)
        os.dup2(old_stderr_fd, 2)
        os.close(old_stdout_fd)
        os.close(old_stderr_fd)
        os.close(devnull_fd)
        sys.stdout, sys.stderr = old_stdout, old_stderr
        # --------------------------------------------------------------

        self.whisper_model = whisper.load_model("base")

    def generate_text_to_speech_audio(self, text: str, output_file: Path):
        if not output_file.parent.exists():
            self.console.print(f'[bold red](tts) Error:[/bold red] Output directory "{output_file.parent}" does not exist.\n')
            return
        
        if not output_file.parent.is_dir():
            self.console.print(f'[bold red](tts) Error:[/bold red] Output path "{output_file.parent}" is not a directory.\n')
            return

        with self.console.status('[bold blue]Generating text-to-speach audio...', spinner='dots12', spinner_style='bold blue'):
            wavs, sr = self.model.generate_voice_design(
                text=text,
                language='English',
                instruct=self.tone,)
            sf.write(output_file, wavs[0], sr)
        self.console.print(f'[green]=> Text-to-speech audio generated successfully and saved to:[/green] [default dim]{output_file}[/default dim]')

    def generate_timestamped_subtitles(self, input_speach_file: Path) -> list[dict]:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with self.console.status('[bold blue]Generating timestamped subtitles...', spinner='dots12', spinner_style='bold blue'):
                result: dict = self.whisper_model.transcribe(str(input_speach_file), word_timestamps=True)
                words: list[dict] = []
                for segment in result["segments"]:
                    for word in segment["words"]:
                        words.append({
                            "word": word["word"].strip(),
                            "start": float(word["start"]),
                            "end": float(word["end"])})
            self.console.print(f'[green]=> Timestamped subtitles generated successfully![/green]')
            return words