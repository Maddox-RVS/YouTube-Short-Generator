from youtube_downloader import download_youtube_video
from pathlib import Path
import typer
import rich
import re
import click

# Create app with custom context to support -h
app = typer.Typer(
    help="YouTube Short Toolbox - Generate YouTube Shorts with AI",
    context_settings={"help_option_names": ["-h", "--help"]},
    add_completion=False)

def is_valid_hex_color(value: str) -> bool:
    return bool(re.match(r'^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$', value))

def validate_video_format(video_file: Path) -> bool:
    valid_formats = ['.mp4', '.mov', '.avi', '.mkv']
    return video_file.suffix.lower() in valid_formats

def validate_music_format(music_file: Path) -> bool:
    valid_formats = ['.mp3', '.wav', '.aac', '.flac']
    return music_file.suffix.lower() in valid_formats

@app.command(short_help='Generate a YouTube Short from video, audio, and text')
def create(
    video: str = typer.Option(..., '-v', '--video', help='Path to input video'),
    audio: str = typer.Option(..., '-a', '--audio', help='Path to background music'),
    text: str = typer.Option(..., '-t', '--text', help='Path to text overlay file (plain text)'),
    output: str = typer.Option(..., '-o', '--output', help='Path to save output'),
    volume: float = typer.Option(1.0, '--volume', help='Volume level for background music (default: 1.0)'),
    keep_video_audio: bool = typer.Option(False, '--keep-video-audio', help='Keep original audio from the video'),
    tone: str = typer.Option('Regular Guy', '--tone', help='Tone for text overlay (e.g., "sarcastic", "excited", "dramatic")'),
    subtitle_color: str = typer.Option('#FF0000', '-c', '--subtitle-color', help='Color for subtitles in hex format (default: #FF0000)'),):

    from Generator import ShortGenerator
    
    video_file: Path = Path(video)
    audio_file: Path = Path(audio)
    text_overlay_file: Path = Path(text)
    output_file: Path = Path(output)

    if not all([video_file.exists(), audio_file.exists()]):
        rich.print('[bold red]Error:[/bold red] Video or audio file does not exist.\n')
        raise typer.Exit()
    
    if not all([video_file.is_file(), audio_file.is_file(), text_overlay_file.is_file()]):
        rich.print('[bold red]Error:[/bold red] Video or audio path is not a file.\n')
        raise typer.Exit()
    
    if not validate_video_format(video_file):
        rich.print('[bold red]Error:[/bold red] Invalid video format. Supported formats are .mp4, .mov, .avi, .mkv.\n')
        raise typer.Exit()
    
    if not validate_music_format(audio_file):
        rich.print('[bold red]Error:[/bold red] Invalid audio format. Supported formats are .mp3, .wav, .aac, .flac.\n')
        raise typer.Exit()
    
    if not is_valid_hex_color(subtitle_color):
        rich.print('[bold red]Error:[/bold red] Invalid subtitle color. Please provide a valid hex color code (e.g., #FF0000).\n')
        raise typer.Exit()
    
    generator = ShortGenerator(video_file, audio_file, text_overlay_file, output_file)
    generator.generate_short(audio_volume=volume, 
                             keep_video_audio=keep_video_audio, 
                             tone=tone, 
                             font_path=Path('Dosis-Bold.ttf'),
                             subtitle_color=subtitle_color)

@app.command(short_help='Download a YouTube video/audio from a URL')
def download(
    link: str = typer.Option(..., '-l', '--link', help='The URL to download'),
    output: str = typer.Option('.', '-o', '--output', help='Directory to save the downloaded video'),
    audio_only: bool = typer.Option(False, '-a', '--audio-only', help='Download audio only'),):
    
    output_dir: Path = Path(output)

    if not output_dir.exists():
        rich.print(f'[bold red]Error:[/bold red] Output directory "{output_dir}" does not exist.\n')
        raise typer.Exit()
    
    if not output_dir.is_dir():
        rich.print(f'[bold red]Error:[/bold red] Output path "{output_dir}" is not a directory.\n')
        raise typer.Exit()
    
    download_youtube_video(link, output_dir, audio_only=audio_only)

if __name__ == '__main__':
    app()
