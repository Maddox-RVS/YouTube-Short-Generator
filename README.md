# YouTube Short Generator

![Python](https://img.shields.io/badge/python-3.13+-blue.svg)
![License](https://img.shields.io/badge/license-AGPL--3.0%20%2B%20additional%20terms-blue.svg)
![PyPI](https://img.shields.io/pypi/v/youtube-short-generator.svg)
![Downloads](https://img.shields.io/pypi/dm/youtube-short-generator.svg)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20macOS%20%7C%20linux-blue)
![GPU](https://img.shields.io/badge/GPU-NVIDIA%20CUDA%20optional-76B900?logo=nvidia&logoColor=white)

Transform videos into engaging YouTube Shorts (9:16 aspect ratio) with **AI-generated narration**, **word-level animated subtitles**, and **background music mixing**. Features GPU acceleration for lightning-fast video processing.

## Attribution

This project is created by MaddoxRVS. GitHub: https://github.com/Maddox-RVS

## Features

- **Automatic aspect ratio conversion**: Crops videos to 9:16 (YouTube Shorts format)
- **AI-powered narration**: Text-to-speech with multiple emotional tones (excited, sarcastic, dramatic, etc.)
- **Animated subtitles**: Word-by-word bouncing text with customizable colors
- **Audio mixing**: Blend background music with AI narration at adjustable volume levels
- **GPU acceleration**: NVIDIA CUDA support for 10-50x faster video encoding
- **YouTube downloader**: Built-in utilities to download videos from YouTube
- **Library and CLI**: Use as a Python module or command-line tool
- **Customizable**: Control tone, colors, volume, and more

## Installation

### System Requirements

- **Python**: 3.13 or higher
- **FFmpeg**: Required for video/audio processing
  - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) or use `winget install ffmpeg`
  - **macOS**: `brew install ffmpeg`
  - **Linux**: `apt install ffmpeg` or `dnf install ffmpeg`
- **NVIDIA GPU** (optional): For GPU acceleration, install [NVIDIA CUDA Toolkit 11.8+](https://developer.nvidia.com/cuda-downloads)

### Pip Installation

```bash
pip install youtube-short-generator
```

### Development Installation

Clone the repository and install in editable mode:

```bash
git clone https://github.com/Maddox-RVS/YouTube-Short-Generator.git
cd YouTube-Short-Generator
pip install -e .
```

## Quick Start

### CLI Usage

#### Create a YouTube Short

```bash
youtube-short-generator create \
  --video input.mp4 \
  --audio background_music.mp3 \
  --text narration.txt \
  --output short.mp4
```

**Required arguments:**
- `-v, --video`: Input video file (supports .mp4, .mov, .avi, .mkv, .webm)
- `-a, --audio`: Background music/audio file (supports .mp3, .wav, .aac, .flac, .m4a)
- `-t, --text`: Text file containing the narration script
- `-o, --output`: Output file path for the generated short

**Optional arguments:**
- `--volume`: Background audio volume (0.0-2.0, default: 1.0)
- `--keep-video-audio`: Keep original video audio in the mix
- `--tone`: TTS narration tone/emotion (default: `Regular Guy`)
  - Examples: `excited`, `sarcastic`, `dramatic`, `whisper`, `cheerful`
- `-c, --subtitle-color`: Subtitle text color as hex code (default: `#FF0000` red)
- `-f, --font`: Path to custom font file for subtitles

**Full example with all options:**

```bash
youtube-short-generator create \
  -v clip.mp4 \
  -a bgm.mp3 \
  -t script.txt \
  -o output_short.mp4 \
  --volume 0.7 \
  --tone excited \
  -c "#00FF00" \
  --keep-video-audio
```

#### Download from YouTube

Download videos or audio from YouTube for processing:

```bash
# Download full video
youtube-short-generator download \
  --link "https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  --output ./downloads

# Download audio only (MP3)
youtube-short-generator download \
  --link "https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  --output ./downloads \
  --audio
```

**Arguments:**
- `-l, --link`: YouTube URL to download
- `-o, --output`: Directory to save the downloaded content
- `-a, --audio`: (Optional flag) Download audio only as MP3

### Python Library Usage

Use the package as a Python library in your own projects:

```python
from youtube_short_generator import ShortGenerator, download_youtube_video
from pathlib import Path

# Create a short from existing files
generator = ShortGenerator(
    video_file=Path('input_video.mp4'),
    audio_file=Path('background_music.mp3'),
    taxt_overlay_file=Path('narration.txt'),
    output_file=Path('my_short.mp4')
)

# Generate with custom settings
generator.generate_short(
    tone='excited',           # AI narration tone
    subtitle_color='#FF00FF', # Magenta subtitles
    audio_volume=0.6,         # 60% background music volume
    keep_video_audio=False    # Don't include original audio
)

# Download from YouTube
download_youtube_video(
    link='https://youtube.com/watch?v=...',
    output_dir=Path('./downloads'),
    audio_only=False  # Set to True for audio-only download
)
```

## Advanced Configuration

### Supported Narration Tones

The TTS engine supports various emotional tones. Try different tones to find the right style for your content:

- `Regular Guy` (default) - Neutral, calm delivery
- `excited` - Enthusiastic, high energy
- `sarcastic` - Witty, sarcastic tone
- `dramatic` - Theatrical, dramatic delivery
- `whisper` - Soft, intimate whisper
- `cheerful` - Happy, positive mood

### Font Customization

Provide your own font file for subtitle text:

```bash
youtube-short-generator create \
  -v video.mp4 -a music.mp3 -t script.txt -o output.mp4 \
  -f /path/to/my_custom_font.ttf
```

The package includes Dosis Bold as the default font, but any TrueType font (.ttf) will work.

## Performance

### GPU Acceleration

If you have an NVIDIA GPU, the application automatically detects it and uses hardware-accelerated video encoding (**h264_nvenc**) instead of CPU encoding (**libx264**).

GPU support is not enabled by default because the CUDA version of PyTorch is not available on PyPI. To enable GPU acceleration, run the following command in your environment after installing:

**pip:**
```bash
pip install torch torchaudio torchvision --index-url https://download.pytorch.org/whl/cu118
```

**uv:**     
Add the following to your `pyproject.toml`:
```bash
[[tool.uv.index]]
url = "https://download.pytorch.org/whl/cu118"
name = "pytorch-cu118"
explicit = true

[tool.uv.sources]
torch = { index = "pytorch-cu118" }
torchaudio = { index = "pytorch-cu118" }
torchvision = { index = "pytorch-cu118" }
```
Then run:
```bash
uv add torch torchaudio torchvision
uv sync
```

The tool will automatically detect and use the GPU if CUDA is available.

## API Reference

### ShortGenerator

The main class for video processing.

```python
ShortGenerator(
    video_file: Path,
    audio_file: Path,
    taxt_overlay_file: Path,
    output_file: Path,
    tts_generator: Optional[TextToSpeechGenerator] = None
)
```

**Methods:**
- `generate_short(audio_volume=1.0, keep_video_audio=False, tone='Regular Guy', font_path=Path('Dosis-Bold.ttf'), subtitle_color='#FF0000')` - Main processing pipeline

### TextToSpeechGenerator

Handles AI narration and subtitle extraction.

```python
import torch
from youtube_short_generator import TextToSpeechGenerator

device = 'cuda' if torch.cuda.is_available() else 'cpu'
TextToSpeechGenerator(device=device)
```

**Methods:**
- `generate_text_to_speech_audio(text: str, tone: str, output_file: Path)` - Generate speech audio
- `generate_timestamped_subtitles(input_speach_file: Path) -> list[dict]` - Extract word-level timing

### YouTube Utilities

```python
from youtube_short_generator import download_youtube_video

download_youtube_video(
    link: str,
    output_dir: Path,
    audio_only: bool = False
)
```

## System Dependencies

### FFmpeg

This tool requires FFmpeg for video and audio processing. It's a system-level dependency that must be installed separately.

**Install FFmpeg:**
- **Windows**: [Download Installer](https://ffmpeg.org/download.html#build-windows) or `winget install ffmpeg`
- **macOS**: `brew install ffmpeg`
- **Linux (Ubuntu/Debian)**: `sudo apt-get install ffmpeg`
- **Linux (Fedora/RHEL)**: `sudo dnf install ffmpeg`

Verify installation:
```bash
ffmpeg -version
```

## Troubleshooting

### "ffmpeg not found"
Ensure FFmpeg is installed and added to your system PATH. See installation instructions above.

### "GPU not detected"
Verify your NVIDIA GPU and CUDA Toolkit installation:
```python
>>> import torch
>>> print('CUDA available:', torch.cuda.is_available())
CUDA available: True
>>> print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')
NVIDIA A100-PCIE-40GB
```

### Slow video processing
GPU acceleration requires CUDA. If you're on CPU-only, processing will be slower. GPU is optional but strongly recommended.