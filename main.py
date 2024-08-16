import subprocess
import argparse
import os

def run_command(command):
    """Run a command and check for errors."""
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {command}")

def main(video_url, languages):
    # Step 1: Fetch YouTube transcriptions
    print("Step 1: Fetching YouTube transcriptions...")
    languages_str = " ".join(languages)
    run_command(f"python get_youtube_transcriptions.py {video_url} {languages_str}")

    # Step 2: Preprocess the audio
    print("Step 2: Preprocessing the audio...")
    run_command(f"python preprocess_audio.py {video_url}")

    # Extract video ID and title to generate subdirectory name
    from pytube import YouTube
    yt = YouTube(video_url)
    video_id = yt.video_id
    video_title = yt.title.replace(" ", "_")
    subdirectory_name = f"{video_title}_{video_id}"

    # Step 3: Generate cross-lingual audio for each language
    print("Step 3: Generating cross-lingual audio...")
    for language in languages:
        run_command(f"python gen_audio.py {subdirectory_name} {language}")

    print("Process completed successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="End-to-end process to generate cross-lingual audio from a YouTube video.")
    parser.add_argument("video_url", type=str, help="The YouTube video URL")
    parser.add_argument(
        "languages", nargs="+", help="List of language codes for transcription and cross-lingual generation (e.g., 'en', 'es', 'fr')."
    )

    args = parser.parse_args()
    video_url = args.video_url
    languages = args.languages

    main(video_url, languages)
