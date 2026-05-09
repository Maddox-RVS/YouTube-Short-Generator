'''
YouTube video and audio download utilities.

This module provides functions to download videos and audio from YouTube
using yt-dlp, with support for format selection and URL validation.
'''

from pathlib import Path
import yt_dlp
import rich
import re

def download_youtube_video(link: str, output_dir: Path, audio_only: bool = False):
    '''
    Download a video or audio from YouTube.
    
    Uses yt-dlp to download best available quality. Supports downloading
    full video or audio-only (MP3) format.
    
    Args:
        link: YouTube URL to download from
        output_dir: Directory path where downloaded content will be saved
        audio_only: If True, download audio only as MP3. If False, download video. (default: False)
    '''

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
            rich.print(f'[bold green]Success:[/bold green] [green]Content saved to[/green] [default dim]"{output_dir}"[/default dim]')
            
    except Exception as e:
        rich.print(f'[bold red]Error:[/bold red] yt-dlp failed: {e}')

def is_valid_youtube_url(url: str) -> bool:
    '''
    Validate whether a string is a valid YouTube URL.
    
    Supports various YouTube URL formats:
    - Regular: youtube.com/watch?v=...
    - Shorts: youtube.com/shorts/...
    - Embedded: youtube.com/embed/...
    - Direct: youtu.be/...
    - Live: youtube.com/live/...
    
    Args:
        url: The URL string to validate
        
    Returns:
        True if the URL matches YouTube URL pattern, False otherwise
    '''
    
    youtube_regex = (
        r'(?:https?://)?'
        r'(?:www\.)?'
        r'(?:youtube\.com|youtu\.be)'
        r'(?:/watch\?v=|/embed/|/shorts/|/live/|/v/|/|)'
        r'[0-9A-Za-z_-]{11}'
        r'(?:[?&]\S*)?')
    return bool(re.fullmatch(youtube_regex, url.strip()))