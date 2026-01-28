# YouTube Downloader UI

A modern desktop GUI application for downloading YouTube videos and audio, built with Python and PyQt5. This application acts as a user-friendly frontend for the powerful [yt-dlp](https://github.com/yt-dlp/yt-dlp) command-line tool.

## Features

- **Video Download**: 
  - Selectable quality (Best, 720p, 480p, 360p)
  - Format conversion options (mp4, mkv, webm, avi, flv)
- **Audio Download**:
  - Extract audio from videos
  - Multiple formats supported (mp3, aac, flac, wav, m4a, opus, vorbis)
  - Quality selection
- **User-Friendly Interface**:
  - Clean PyQt5-based GUI
  - Real-time log output
  - Automatic default path selection (Videos/Music folders)
- **System Integration**:
  - Native file dialogs for folder selection

## Prerequisites

Before running this application, you need to have the following installed on your system:

1. **Python 3.6+**
2. **FFmpeg** (Required for media merging and format conversion)
   - *Linux*: `sudo apt install ffmpeg`
   - *Windows/macOS*: Download from [ffmpeg.org](https://ffmpeg.org/download.html)
3. **yt-dlp** command line tool
   - You can install it via pip (recommended): `pip install yt-dlp`
   - Or follow instructions on the [yt-dlp GitHub page](https://github.com/yt-dlp/yt-dlp)

## Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd youtube-downloader-ui
   ```

2. Install the required Python dependencies:
   ```bash
   pip install PyQt5 yt-dlp
   ```

## Usage

1. Run the application:
   ```bash
   python yt_downloader.py
   ```

2. **To download a video:**
   - Paste the YouTube URL.
   - Select "Video" in Download Type.
   - Choose your desired Quality and Format.
   - Select the Output Folder (defaults to `~/Videos`).
   - Click "Download".

3. **To download audio:**
   - Paste the YouTube URL.
   - Select "Audio Only" in Download Type.
   - Choose your desired Format and Quality.
   - Select the Output Folder (defaults to `~/Music`).
   - Click "Download".

## Troubleshooting

- **"Command failed" or "File not found" errors**: Ensure `yt-dlp` and `ffmpeg` are installed and added to your system's PATH.
- **Download stuck**: Check your internet connection or try a lower quality setting.

## License

[MIT License](LICENSE)