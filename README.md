# SwahiliSub-AI: Automatic Swahili Subtitle Generator

This project automates the process of generating Swahili subtitles for movies using AI. It transcribes audio using OpenAI's Whisper model, translates the text to Swahili using Deep Translator (Google Translate) or Argos Translate, and then hardcodes the subtitles into the video file using FFmpeg.

## Features

-   **Automatic Transcription:** Uses Whisper AI to listen and transcribe video audio.
-   **Swahili Translation:** Translates English subtitles to Swahili.
-   **Hardcoding:** Burns the subtitles permanently into the video for compatibility with all players.
-   **Batch Processing:** Can process an entire folder of movies automatically.
-   **Quality Control:** Includes an inspector module to check subtitle quality.
-   **Cinema Style:** Applies a professional cinema-style font and outline to subtitles.

## Files

-   `swahilisub_ai.py`: Core script for transcription and translation of a single file.
-   `batch_process_movies.py`: Scans a directory and processes all video files found.
-   `inspector.py`: Helper script for quality control.
-   `Washa_SwahiliSub.bat`: Windows Batch file to easily launch the system.

## Setup

1.  Install Python.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Ensure FFmpeg is installed and added to your system PATH.

## Usage

1.  Edit `batch_process_movies.py` to point to your video folder (`SOURCE_FOLDER`).
2.  Run the batch script:
    ```bash
    python batch_process_movies.py
    ```
    Or use the provided `Washa_SwahiliSub.bat` file.

## Requirements

-   Python 3.8+
-   FFmpeg
-   Internet connection (for Google Translate)
