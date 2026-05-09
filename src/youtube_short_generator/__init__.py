'''
YouTube Short Generator package.

Provides tools to convert videos into YouTube Shorts format (9:16) with AI-generated
voiceover, subtitles, and background music using GPU acceleration.
'''

from .short_generator import ShortGenerator
from .youtube_downloader import download_youtube_video

__all__ = ['ShortGenerator', 'download_youtube_video']