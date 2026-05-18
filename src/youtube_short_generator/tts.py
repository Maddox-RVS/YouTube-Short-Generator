'''
Text-to-speech and speech-to-text functionality using AI models.

Provides TextToSpeechGenerator class for generating speech from text using Qwen3 TTS
and generating timestamped subtitles using OpenAI Whisper.
'''

from typing import Optional, Callable, Tuple
from rich.console import RenderableType
from rich.console import Console
from rich.spinner import Spinner
from typing import Optional
from rich.live import Live
from rich.text import Text
from pathlib import Path
import soundfile as sf
import warnings
import sys
import os

class TextToSpeechGenerator:
    '''
    Generate speech audio from text and generate subtitles from audio.
    
    Uses Qwen3 for text-to-speech synthesis and OpenAI Whisper for speech-to-text
    with word-level timestamps. Supports GPU acceleration via CUDA.
    '''
    
    def __init__(self, device: str):
        '''
        Initialize the TextToSpeechGenerator with specified device.
        
        Args:
            device: Device to use ('cuda', 'mps', or 'cpu')
        '''
        import whisper
        import torch

        self.device: str = device
        self._status: Optional[Tuple[RenderableType, bool]] = None
        self.on_status_change: Optional[Callable[[RenderableType, bool], None]] = None
        self.is_running: bool = False

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

        try:
            from qwen_tts import Qwen3TTSModel
            self.model = Qwen3TTSModel.from_pretrained(
                'Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign',
                device_map=self.device,
                dtype=torch.float16 if self.device != 'cpu' else torch.float32,
                attn_implementation='sdpa',)
        except Exception as e:
            os.dup2(old_stdout_fd, 1)
            os.dup2(old_stderr_fd, 2)
            sys.stdout, sys.stderr = old_stdout, old_stderr
            self.status = (f'[bold red](tts) Error loading Qwen3 TTS model:[/bold red] {e}', True)
        finally:
            os.dup2(old_stdout_fd, 1)
            os.dup2(old_stderr_fd, 2)
            os.close(old_stdout_fd)
            os.close(old_stderr_fd)
            os.close(devnull_fd)
            sys.stdout, sys.stderr = old_stdout, old_stderr
        # --------------------------------------------------------------

        self.whisper_model = whisper.load_model('base', device=self.device)

    @property
    def status(self) -> Tuple[RenderableType, bool]:
        return self._status

    @status.setter
    def status(self, value: Tuple[RenderableType, bool]) -> None:
        self._status = value
        if self.on_status_change:
            self.on_status_change(*value)

    def generate_text_to_speech_audio(self, text: str, tone: str, output_file: Path):
        '''
        Generate speech audio from text using Qwen3 TTS.
        
        Args:
            text: Text content to convert to speech
            tone: Emotional tone/style (e.g., "excited", "sarcastic", "dramatic")
            output_file: Path to save the generated WAV file
        '''

        try:
            self.is_running = True

            if not output_file.parent.exists():
                self.status = (f'[bold red](tts) Error:[/bold red] Output directory "{output_file.parent}" does not exist.\n', True)
                return
            
            if not output_file.parent.is_dir():
                self.status = (f'[bold red](tts) Error:[/bold red] Output path "{output_file.parent}" is not a directory.\n', True)
                return

            self.status = (Spinner('dots12', text=Text('Generating text-to-speech audio...', style='bold blue'), style='bold blue'), False)
            wavs, sr = self.model.generate_voice_design(
                text=text,
                language='English',
                instruct=tone,)
            sf.write(output_file, wavs[0], sr)
            self.status = (f'[green]=> Text-to-speech audio generated successfully and saved to:[/green] [default dim]"{output_file}"[/default dim]', True)
        finally:
            self.is_running = False

    def generate_timestamped_subtitles(self, input_speach_file: Path) -> list[dict]:
        '''
        Extract timestamped subtitles from speech audio using Whisper.
        
        Args:
            input_speach_file: Path to the audio file to transcribe
            
        Returns:
            List of dictionaries containing word-level timestamps with keys:
            - word: The transcribed word
            - start: Start time in seconds (float)
            - end: End time in seconds (float)
        '''

        try:
            self.is_running = True

            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                self.status = (Spinner('dots12', text=Text('Generating timestamped subtitles...', style='bold blue'), style='bold blue'), False)
                result: dict = self.whisper_model.transcribe(str(input_speach_file), word_timestamps=True)
                words: list[dict] = []
                for segment in result['segments']:
                    for word in segment['words']:
                        words.append({
                            'word': word['word'].strip(),
                            'start': float(word['start']),
                            'end': float(word['end'])})
                self.status = ('[green]=> Timestamped subtitles generated successfully![/green]', True)
                return words
        finally:
            self.is_running = False