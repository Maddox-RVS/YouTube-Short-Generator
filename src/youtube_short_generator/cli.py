'''
Command-line interface for YouTube Short Generator.

Provides CLI commands to create YouTube Shorts from videos and download content
from YouTube with AI-generated voiceover and subtitles.
'''

from .youtube_downloader import download_youtube_video
from rich.console import Console
from rich.live import Live
from pathlib import Path
import typer
import rich
import re

console = Console()

app = typer.Typer(
    help="YouTube Short Toolbox - Generate YouTube Shorts with AI",
    context_settings={"help_option_names": ["-h", "--help"]},
    add_completion=False)

def is_valid_hex_color(value: str) -> bool:
    '''
    Validate if a string is a valid hexadecimal color code.
    
    Args:
        value: Color string to validate (e.g., "#FF0000" or "#FFF")
        
    Returns:
        True if valid hex color, False otherwise
    '''

    return bool(re.match(r'^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$', value))

def validate_video_format(video_file: Path) -> bool:
    '''
    Check if video file has a supported format.
    '''

    valid_formats = ['.mp4', '.mov', '.avi', '.mkv']
    return video_file.suffix.lower() in valid_formats

def validate_music_format(music_file: Path) -> bool:
    '''
    Check if audio file has a supported format.
    '''
    
    valid_formats = ['.mp3', '.wav', '.aac', '.flac']
    return music_file.suffix.lower() in valid_formats

@app.command(short_help='Generate a YouTube Short from video, audio, and text')
def create(
    video: str = typer.Option(..., '-v', '--video', help='Path to input video'),
    audio: str = typer.Option(..., '-a', '--audio', help='Path to background music'),
    text: str = typer.Option(..., '-t', '--text', help='Path to text overlay file (plain text)'),
    output: str = typer.Option(..., '-o', '--output', help='Path to save output'),
    volume: float = typer.Option(1.0, '--volume', help='Volume level for background music'),
    keep_video_audio: bool = typer.Option(False, '--keep-video-audio', help='Keep original audio from the video'),
    tone: str = typer.Option('Excited', '--tone', help='Tone for text overlay (e.g., "sarcastic", "excited", "dramatic")'),
    subtitle_color: str = typer.Option('#FF0000', '-c', '--subtitle-color', help='Color for subtitles in hex format'),):
    '''
    Generate a YouTube Short by combining video, background music, and text-to-speech voiceover.
    
    Processes input video into 9:16 aspect ratio, generates AI voiceover from text,
    adds timestamped subtitles, and mixes with background music.
    '''

    from youtube_short_generator import ShortGenerator
    
    video_file: Path = Path(video)
    audio_file: Path = Path(audio)
    text_overlay_file: Path = Path(text)
    output_file: Path = Path(output)

    if not all([video_file.exists(), audio_file.exists()]):
        console.print('[bold red]Error:[/bold red] Video or audio file does not exist.\n')
        raise typer.Exit()
    
    if not all([video_file.is_file(), audio_file.is_file(), text_overlay_file.is_file()]):
        console.print('[bold red]Error:[/bold red] Video or audio path is not a file.\n')
        raise typer.Exit()
    
    if not validate_video_format(video_file):
        console.print('[bold red]Error:[/bold red] Invalid video format. Supported formats are .mp4, .mov, .avi, .mkv.\n')
        raise typer.Exit()
    
    if not validate_music_format(audio_file):
        console.print('[bold red]Error:[/bold red] Invalid audio format. Supported formats are .mp3, .wav, .aac, .flac.\n')
        raise typer.Exit()
    
    if not is_valid_hex_color(subtitle_color):
        console.print('[bold red]Error:[/bold red] Invalid subtitle color. Please provide a valid hex color code (e.g., #FF0000).\n')
        raise typer.Exit()
    
    import importlib.resources
    try:
        font_dir: Path = importlib.resources.files('youtube_short_generator').parent / 'youtube_short_generator'
        font_path: Path = font_dir / 'Dosis-Bold.ttf'
    except: font_path = Path('Dosis-Bold.ttf')

    console.print('[bold green]------------------------[/bold green]')
    console.print('[bold green]YouTube Short Generator[/bold green]')
    console.print('[bold green]------------------------[/bold green]')
    console.print('[bold green]Processing video...[/bold green]')

    generator = ShortGenerator(video_file, audio_file, text_overlay_file, output_file)
    
    with Live(console=console, refresh_per_second=20, transient=True) as live:
        def on_status_change(renderable, permanent):
            if permanent: live.console.print(renderable)
            else: live.update(renderable)

        generator.on_status_change = on_status_change

        generator.generate_short(audio_volume=volume, 
                                keep_video_audio=keep_video_audio, 
                                tone=tone, 
                                font_path=font_path,
                                subtitle_color=subtitle_color)

    console.print(f'[bold green]Finished processing video. Output saved to:[/bold green] [default dim]"{output_file}"[/default dim]')
    console.print('[bold green]------------------------[/bold green]')

@app.command(short_help='Download a YouTube video/audio from a URL')
def download(
    link: str = typer.Option(..., '-l', '--link', help='The URL to download'),
    output: str = typer.Option('.', '-o', '--output', help='Directory to save the downloaded video'),
    audio_only: bool = typer.Option(False, '-a', '--audio-only', help='Download audio only'),):
    '''
    Download a video or audio from YouTube.
    
    Args:
        link: YouTube URL to download
        output: Directory to save the downloaded file
        audio_only: If True, download audio only (MP3)
    '''
    
    output_dir: Path = Path(output)

    if not output_dir.exists():
        console.print(f'[bold red]Error:[/bold red] Output directory "{output_dir}" does not exist.\n')
        raise typer.Exit()
    
    if not output_dir.is_dir():
        console.print(f'[bold red]Error:[/bold red] Output path "{output_dir}" is not a directory.\n')
        raise typer.Exit()
    
    download_youtube_video(link, output_dir, audio_only=audio_only)

if __name__ == '__main__':
    app()
