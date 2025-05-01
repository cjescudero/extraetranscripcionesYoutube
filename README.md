# YouTube Transcript Extractor

A tool to extract transcripts from YouTube videos, either from individual videos or from a complete playlist. The transcripts are saved in a Markdown file, with separate sections for each video.

## Installation

```bash
uv pip install pytube youtube-transcript-api
```

## Usage

### To extract transcripts from a playlist:

```bash
python extract_transcripts.py --playlist "PLAYLIST_URL" --output transcripts.md
```

### To extract transcripts from individual videos:

```bash
python extract_transcripts.py --videos "VIDEO_URL1" "VIDEO_URL2" --output transcripts.md
```

### Available options:

- `-p, --playlist`: YouTube playlist URL
- `-v, --videos`: One or more individual video URLs
- `-o, --output`: Output file name (default: transcripts.md)

## Output Format

The script generates a Markdown file with the following format:

```markdown
## [Video Title 1]
[Video 1 Transcript]

## [Video Title 2]
[Video 2 Transcript]
```

If a transcript is not available, it will be indicated with the message "_Transcript not available._" 