from youtube_downloader import download_youtube_video
from Generator import ShortGenerator
from pathlib import Path
import argparse
import rich
import re

def is_valid_hex_color(value: str) -> bool:
    return bool(re.match(r'^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$', value))

def validate_video_format(video_file: Path) -> bool:
    valid_formats = ['.mp4', '.mov', '.avi', '.mkv']
    return video_file.suffix.lower() in valid_formats

def validate_music_format(music_file: Path) -> bool:
    valid_formats = ['.mp3', '.wav', '.aac', '.flac']
    return music_file.suffix.lower() in valid_formats

def main():
    parser = argparse.ArgumentParser(description='YouTube Short Toolbox')
    subparsers = parser.add_subparsers(dest='command', required=True, help='Available commands')

    create_parser = subparsers.add_parser('create', help='Generate a YouTube Short')
    create_parser.add_argument('-v', '--video', type=str, required=True, help='Path to input video')
    create_parser.add_argument('-a', '--audio', type=str, required=True, help='Path to background music')
    create_parser.add_argument('--volume', type=float, default=1.0, required=False, help='Volume level for background music (default: 1.0)')
    create_parser.add_argument('--keep-video-audio', required=False, action='store_true', help='Keep original audio from the video')
    create_parser.add_argument('-t', '--text', type=str, required=True, help='Path to text overlay file (plain text)')
    create_parser.add_argument('-o', '--output', type=str, required=True, help='Path to save output')
    create_parser.add_argument('--tone', type=str, required=False, default='Regular Guy', help='Tone for text overlay (e.g., "sarcastic", "excited", "dramatic")')
    create_parser.add_argument('-c', '--subtitle-color', type=str, required=False, default='#FF0000', help='Color for subtitles in hex format (default: #FF0000)')

    download_parser = subparsers.add_parser('download', help='Download a youtube video from a link')
    download_parser.add_argument('-l', '--link', type=str, help='The URL to download')
    download_parser.add_argument('-o', '--output', type=str, required=True, default='.', help='Directory to save the downloaded video')
    download_parser.add_argument('-a', '--audio-only', required=False, action='store_true', help='Download audio only')

    args: argparse.Namespace = parser.parse_args()

    if args.command == 'create': handle_create(args)
    elif args.command == 'download': handle_download(args)

def handle_create(args: argparse.Namespace):
    video_file: Path = Path(args.video)
    audio_file: Path = Path(args.audio)
    text_overlay_file: Path = Path(args.text)
    output_file: Path = Path(args.output)
    audio_volume: float = args.volume
    keep_video_audio: bool = args.keep_video_audio
    tone: str = args.tone
    subtitle_color: str = args.subtitle_color

    if not all([video_file.exists(), audio_file.exists()]):
        rich.print('[bold red]Error:[/bold red] Video or audio file does not exist.\n')
        return
    
    if not all([video_file.is_file(), audio_file.is_file(), text_overlay_file.is_file()]):
        rich.print('[bold red]Error:[/bold red] Video or audio path is not a file.\n')
        return
    
    if not validate_video_format(video_file):
        rich.print('[bold red]Error:[/bold red] Invalid video format. Supported formats are .mp4, .mov, .avi, .mkv.\n')
        return
    
    if not validate_music_format(audio_file):
        rich.print('[bold red]Error:[/bold red] Invalid audio format. Supported formats are .mp3, .wav, .aac, .flac.\n')
        return
    
    if not is_valid_hex_color(subtitle_color):
        rich.print('[bold red]Error:[/bold red] Invalid subtitle color. Please provide a valid hex color code (e.g., #FF0000).\n')
        return
    
    generator = ShortGenerator(video_file, audio_file, text_overlay_file, output_file)
    generator.generate_short(audio_volume=audio_volume, 
                             keep_video_audio=keep_video_audio, 
                             tone=tone, 
                             font_path=Path('Dosis-Bold.ttf'),
                             subtitle_color=subtitle_color)
    
def handle_download(args: argparse.Namespace):
    link: str = args.link
    output_dir: Path = Path(args.output)

    if not output_dir.exists():
        rich.print(f'[bold red]Error:[/bold red] Output directory "{output_dir}" does not exist.\n')
        return
    
    if not output_dir.is_dir():
        rich.print(f'[bold red]Error:[/bold red] Output path "{output_dir}" is not a directory.\n')
        return
    
    download_youtube_video(link, output_dir, audio_only=args.audio_only)

if __name__ == '__main__':
    main()
