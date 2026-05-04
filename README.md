# YouTube Short Generator

Converts videos into YouTube Shorts format (9:16) with AI-generated voiceover, subtitles, and background music.

## Requirements

- uv: https://docs.astral.sh/uv/getting-started/
- FFmpeg: https://ffmpeg.org/download.html

## Usage

Run commands with `uv run`:

### Create a YouTube Short

```bash
uv run python main.py create -v video.mp4 -a music.mp3 -t script.txt -o output.mp4
```

Required arguments:
- `-v, --video`: Input video file (.mp4, .mov, .avi, .mkv)
- `-a, --audio`: Background music file (.mp3, .wav, .aac, .flac)
- `-t, --text`: Text file for voiceover
- `-o, --output`: Output file path

Optional arguments:
- `--volume`: Background music volume (default: 1.0)
- `--keep-video-audio`: Keep original video audio
- `--tone`: TTS tone/emotion (default: "Regular Guy")
- `-c, --subtitle-color`: Subtitle color in hex (default: #FF0000)

Example:
```bash
uv run python main.py create -v clip.mp4 -a bgm.mp3 -t narration.txt -o short.mp4 --tone "excited" -c "#00FF00" --volume 0.5
```

### Download from YouTube

```bash
uv run python main.py download -l "https://youtube.com/watch?v=..." -o ./output
```

Optional: add `-a` flag to download audio only
