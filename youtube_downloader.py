from pathlib import Path
import yt_dlp
import rich
import re

def download_youtube_video(link: str, output_dir: Path, audio_only: bool = False):
    url = link.strip()
    
    ydl_opts = {
        'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
        'quiet': False,
        'no_warnings': True,
        'noplaylist': True,
    }

    if audio_only:
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    else:
        ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            rich.print(f'[bold green]Downloading:[/bold green] {url}...')
            ydl.download([url])
            rich.print(f'[bold green]Success:[/bold green] Content saved to {output_dir}\n')
            
    except Exception as e:
        rich.print(f'[bold red]Error:[/bold red] yt-dlp failed: {e}')

def is_valid_youtube_url(url: str) -> bool:
    youtube_regex = (
        r'(?:https?://)?'
        r'(?:www\.)?'
        r'(?:youtube\.com|youtu\.be)'
        r'(?:/watch\?v=|/embed/|/shorts/|/live/|/v/|/|)'
        r'[0-9A-Za-z_-]{11}'
        r'(?:[?&]\S*)?')
    return bool(re.fullmatch(youtube_regex, url.strip()))