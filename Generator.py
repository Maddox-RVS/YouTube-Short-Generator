import subprocess

from moviepy import CompositeAudioClip, CompositeVideoClip, TextClip, VideoClip, VideoFileClip, AudioFileClip
from moviepy.video.fx.Margin import Margin
from tts import TextToSpeechGenerator
from rich.console import Console
import moviepy.video.fx as vfx
from typing import Optional
from rich.live import Live
from rich.text import Text
from PIL import ImageFont
from pathlib import Path
import tempfile
import torch
import time

class ShortGenerator:
    def __init__(self, 
                 video_file: Path, 
                 audio_file: Path, 
                 taxt_overlay_file: Path, 
                 output_file: Path):
        self.tempdir: tempfile.TemporaryDirectory = tempfile.TemporaryDirectory()
        self.video_file: Path = video_file
        self.audio_file: Path = audio_file
        self.text_overlay_file: Path = taxt_overlay_file
        self.output_file: Path = output_file
        self.tts_generator: Optional[TextToSpeechGenerator] = None
        self.console = Console()
        self.video_codec: str = 'libx264'

    def _get_video_codec(self) -> str:
        video_encoding_method: str = 'libx264'
        video_encoding_message: str = ''
        with self.console.status('[bold blue]Detecting available video encoding method...', spinner='dots12', spinner_style='bold blue'):
            if torch.cuda.is_available():
                video_encoding_message = '[green]=> Using GPU hardware encoding (h264_nvenc)[/green]'
                video_encoding_method = 'h264_nvenc'
            else:
                video_encoding_message = '[green]=> Using CPU software encoding (libx264)[/green]'
                video_encoding_method = 'libx264'
        self.console.print(f'{video_encoding_message}')
        return video_encoding_method

    def _convert_to_mp4(self, input_file: Path) -> Path:
        if input_file.suffix.lower() == '.mp4':
            return input_file

        temp_output: Path = Path(self.tempdir.name) / f'{input_file.stem}_converted.mp4'
        with VideoFileClip(str(input_file)) as video:
            video.write_videofile(str(temp_output), codec=self.video_codec, audio_codec='aac', logger=None)
        return temp_output

    def _convert_to_mp3(self, input_file: Path) -> Path:
        if input_file.suffix.lower() == '.mp3':
            return input_file

        temp_output: Path = Path(self.tempdir.name) / f'{input_file.stem}_converted.mp3'
        with AudioFileClip(str(input_file)) as audio:
            audio.write_audiofile(str(temp_output), bitrate='192k', logger=None)
        return temp_output

    def _open_text_overlay(self, lines_shown=5, delay=0.05) -> str:
        with open(self.text_overlay_file, 'r') as f:
            lines = f.readlines()

        with Live(console=self.console, refresh_per_second=20, transient=True) as live:
            for i in range(len(lines)):
                window = lines[max(0, i - lines_shown):i + 1]

                display = Text()
                display.append('Opening and reading overlay text file:\n', style='blue bold')
                display.append(''.join(window), style='dim')

                live.update(display)
                time.sleep(delay)

        self.console.print('[green]=> Overlay text file read successfully![/green]')
        return ''.join(lines)

    def _edit_into_short_format(self, 
                                input_video_file: Path, 
                                input_audio_file: Path, 
                                input_tts_audio_file: Path, 
                                subtitles: list[dict],
                                output_file: Path,
                                font_path: Path,
                                subtitle_color: str,
                                audio_volume=1.0,
                                keep_video_audio=False):
        with VideoFileClip(input_video_file) as final_clip:

            # ----------------------------------------------------------------------------------------------
            # Fit the duration of the video to match the TTS audio duration if less than TTS audio duration
            # ----------------------------------------------------------------------------------------------
            with AudioFileClip(str(input_tts_audio_file)) as tts_clip:
                tts_audio_duration = tts_clip.duration
                if final_clip.duration < tts_audio_duration:
                    with self.console.status('[bold blue]Fitting video to {tts_audio_duration} seconds...', spinner='dots12', spinner_style='bold blue'):
                        final_clip = final_clip.with_effects([vfx.Loop(duration=tts_audio_duration)])
                    self.console.print(f'[green]=> Video duration increased to match TTS audio duration of {tts_audio_duration:.2f} seconds![/green]')
            # ----------------------------------------------------------------------------------------------

            # ------------------------------------
            # Crop the video to 9:16 aspect ratio
            # ------------------------------------
            with self.console.status('[bold blue]Cropping video to 9:16 aspect ratio...', spinner='dots12', spinner_style='bold blue'):
                w, h = final_clip.size

                target_width = int(h * 9 / 16)
                if target_width % 2 != 0:
                    target_width -= 1

                if h % 2 != 0:
                    h -= 1

                x1 = (w - target_width) / 2
                x2 = x1 + target_width

                final_clip = final_clip.cropped(x1=x1, y1=0, x2=x2, y2=h)
            self.console.print('[green]=> Finished cropping video to 9:16 aspect ratio![/green]')
            # ------------------------------------

            # --------------------------------------------------------------------
            # Remove original audio from input video if keep_video_audio is False
            # --------------------------------------------------------------------
            if not keep_video_audio:
                with self.console.status('[bold blue]Removing original audio from video...', spinner='dots12', spinner_style='bold blue'):
                    final_clip = final_clip.without_audio()
                self.console.print('[green]=> Original audio removed from video![/green]')
            # --------------------------------------------------------------------

            # ----------------------------------------------------------------------------------------------
            # Mix the TTS audio with the background music, applying the specified volume level to the music
            # ----------------------------------------------------------------------------------------------
            with self.console.status('[bold blue]Mixing TTS audio with background audio...', spinner='dots12', spinner_style='bold blue'):
                audio: AudioFileClip = AudioFileClip(str(input_audio_file)).with_volume_scaled(audio_volume)
                tts_audio: AudioFileClip = AudioFileClip(str(input_tts_audio_file))
                mixed_audio = CompositeAudioClip([audio, tts_audio]) if not keep_video_audio else CompositeAudioClip([audio, tts_audio, final_clip.audio])
                final_clip = final_clip.with_audio(mixed_audio)
            self.console.print('[green]=> Finished mixing TTS audio with background audio![/green]')
            # ----------------------------------------------------------------------------------------------

            # -----------------------------
            # Apply subtitles to the video
            # -----------------------------
            with self.console.status('[bold blue]Applying subtitles to video...', spinner='dots12', spinner_style='bold blue'):
                final_clip: VideoClip = final_clip
                vw, vh = final_clip.size
                bounce_duration: float = 0.12
                
                def _make_word_clip(word: str, start: float, end: float, stroke_color: str, stroke_width: int = 6) -> TextClip:
                    def _get_fitting_font_size(text: str, max_width: int, max_font_size: int = 140) -> int:
                        for size in range(max_font_size, 10, -1):
                            font = ImageFont.truetype(str(font_path), size)
                            bbox = font.getbbox(text)
                            text_width = bbox[2] - bbox[0] + stroke_width * 2
                            if text_width <= max_width:
                                return size
                        return 10  # fallback minimum

                    font_size: int = _get_fitting_font_size(word, vw - 40)  # 40px padding either side

                    def _get_scale(t: float) -> float:
                        if t > bounce_duration: return 1.0
                        progress = t / bounce_duration
                        base = 0.5 + (0.65 * progress)
                        result = base if progress < 0.75 else (1.15 - 0.15 * ((progress - 0.75) / 0.25))
                        return max(result, 0.5)
                    
                    text_clip: TextClip = TextClip(
                        font=str(font_path),
                        text=word,
                        method='caption',
                        size=(vw, vh),
                        font_size=font_size,
                        color='white',
                        stroke_color=stroke_color,
                        stroke_width=stroke_width,
                        text_align='center')
                    text_clip = text_clip.with_position('center')
                    text_clip = text_clip.with_start(start)
                    text_clip = text_clip.with_duration(end - start)

                    animated_clip = text_clip.resized(lambda t: _get_scale(t))
                    return animated_clip
                
                def _make_subtitle(word: dict) -> VideoClip:
                    return _make_word_clip(
                        word=word['word'],
                        start=word['start'],
                        end=word['end'],
                        stroke_color=subtitle_color,
                        stroke_width=6)
                
                subtitle_clips: list[VideoClip] = [_make_subtitle(w) for w in subtitles]
                final_clip = CompositeVideoClip([final_clip] + subtitle_clips)
            self.console.print('[green]=> Finished applying subtitles to video![/green]')
            # -----------------------------

            # ----------------------------------------------------------------------------------------------------------------
            # Cut the duration of the video to match the TTS audio duration (in case video is longer than TTS audio duration)
            # ----------------------------------------------------------------------------------------------------------------
            with self.console.status('[bold blue]Cutting video to {tts_audio_duration} seconds...', spinner='dots12', spinner_style='bold blue'):
                final_clip = final_clip.subclipped(0, tts_audio_duration)
            self.console.print(f'[green]=> Video duration cut to match TTS audio duration of {tts_audio_duration:.2f} seconds![/green]')
            # ----------------------------------------------------------------------------------------------------------------

            with self.console.status('[bold blue]Exporting video...', spinner='dots12', spinner_style='bold blue'):
                final_clip.write_videofile(str(output_file), codec=self.video_codec, audio_codec='aac', logger=None)
            self.console.print(f'[green]=> Video exported successfully![/green]')
            audio.close()
            tts_audio.close()

    def _get_device(self) -> str:
        device: str = 'cpu'
        device_selection_message: str = ''
        with self.console.status('[bold blue]Detecting available device...', spinner='dots12', spinner_style='bold blue'):
            if torch.cuda.is_available():
                device_count = torch.cuda.device_count()
                device_name = torch.cuda.get_device_name(0)
                device_selection_message = f'[green]=> CUDA GPU detected:[/green] [default dim]{device_name} ({device_count} GPU{"s" if device_count > 1 else ""})[/default dim]'
                device = 'cuda'
            elif torch.backends.mps.is_available():
                device_selection_message = '[green]=> Apple Silicon (MPS) detected[/green]'
                device = 'mps'
            else:
                device_selection_message = '[green]=> No GPU detected, using CPU[/green]'
                device = 'cpu'
        self.console.print(f'{device_selection_message}')
        return device

    def generate_short(self, audio_volume=1.0, keep_video_audio=False, tone='Regular Guy', font_path=Path('Dosis-Bold.ttf'), subtitle_color='#FF0000'):
        self.console.print(f'[bold green]------------------------[/bold green]')
        self.console.print(f'[bold green]YouTube Short Generator[/bold green]')
        self.console.print(f'[bold green]------------------------[/bold green]')
        self.console.print('[bold green]Processing video...[/bold green]')

        # Detect best available video codec based on hardware capabilities (h264_nvenc for GPU, libx264 for CPU)
        self.video_codec = self._get_video_codec()

        # Convert/encode input video as mp4
        with self.console.status('[bold blue]Ensuring video is proper format...', spinner='dots12', spinner_style='bold blue'):
            self.video_file = self._convert_to_mp4(self.video_file)
        self.console.print('[green]=> Validated video format![/green]')

        # Convert/encode input audio as mp3
        with self.console.status('[bold blue]Ensuring audio is proper format...', spinner='dots12', spinner_style='bold blue'):
            self.audio_file = self._convert_to_mp3(self.audio_file)
        self.console.print('[green]=> Validated audio format![/green]')

        # Read text from text overlay file
        text_overlay: str = self._open_text_overlay()

        # Generate TTS audio based on the text overlay and specified tone, then save to temporary directory
        device: str = self._get_device()
        self.console.print(f'[bold blue]Initializing Text-to-Speech generator...', end='\r')
        if not self.tts_generator: self.tts_generator = TextToSpeechGenerator(device, tone)
        if self.tts_generator.tone != tone: self.tts_generator = TextToSpeechGenerator(device, tone)
        self.console.print(f'[green]=> Text-to-Speech generator initialized with tone:[/green] [default dim]"{tone}"[/default dim]')
        tts_audio_file: Path = Path(self.tempdir.name) / 'tts_audio.wav'
        self.tts_generator.generate_text_to_speech_audio(text_overlay, tts_audio_file)

        # Transcribe the generated TTS audio to get timestamped subtitles
        subtitles: list[dict] = self.tts_generator.generate_timestamped_subtitles(tts_audio_file)

        # Edit the input video into the short format, applying the TTS audio, background music, and subtitles, then save to output path
        self._edit_into_short_format(
            input_video_file=self.video_file,
            input_audio_file=self.audio_file,
            input_tts_audio_file=tts_audio_file,
            output_file=self.output_file,
            subtitles=subtitles,
            audio_volume=audio_volume,
            font_path=font_path,
            keep_video_audio=keep_video_audio,
            subtitle_color=subtitle_color)

        self.console.print(f'[bold green]Finished processing video. Output saved to:[/bold green] [default dim]"{self.output_file}"[/default dim]')
        self.console.print(f'[bold green]------------------------[/bold green]')

    def __del__(self):
        self.tempdir.cleanup()  