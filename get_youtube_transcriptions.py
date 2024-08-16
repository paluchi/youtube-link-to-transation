import os
import argparse
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound


def fetch_youtube_transcriptions(
    video_url: str, languages: list, output_dir="transcriptions"
):
    try:
        # Extract the video ID and title from the URL
        yt = YouTube(video_url)
        video_id = yt.video_id
        video_title = yt.title.replace(" ", "_")

        # Create a directory for the video
        video_dir = os.path.join(output_dir, f"{video_title}_{video_id}")
        if not os.path.exists(video_dir):
            os.makedirs(video_dir)

        # Fetch available transcripts
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Store transcripts by language
        transcripts_by_language = {}

        # Fetch transcripts for the specified languages
        for language in languages:
            try:
                # Check if the transcript is available in the specified language
                transcript = transcript_list.find_transcript([language])
                transcript_data = transcript.fetch()
                transcripts_by_language[language] = transcript_data
            except NoTranscriptFound:
                print(f"No manual transcript found for language '{language}'. Checking for auto-generated transcripts.")
                
                # Check for auto-generated transcripts
                auto_generated_langs = [t.language_code for t in transcript_list if t.is_generated]
                
                if language in auto_generated_langs:
                    print(f"Found auto-generated transcript for '{language}'.")
                    transcript = transcript_list.find_transcript([language])
                    transcript_data = transcript.fetch()
                    transcripts_by_language[language] = transcript_data
                else:
                    print(f"No auto-generated transcript found for '{language}'. Attempting to translate from another language.")
                    # Try to fetch any available transcript and translate it
                    try:
                        available_transcript = next(iter(transcript_list))
                        translated_transcript = available_transcript.translate(language).fetch()
                        transcripts_by_language[language] = translated_transcript
                    except Exception as e:
                        print(f"Could not fetch translated transcript for '{language}': {str(e)}")
            except Exception as e:
                print(f"Could not fetch transcript for language '{language}': {str(e)}")

        # Save transcripts to files
        for lang, transcription in transcripts_by_language.items():
            lang_dir = os.path.join(video_dir, lang)
            if not os.path.exists(lang_dir):
                os.makedirs(lang_dir)

            transcript_file = os.path.join(lang_dir, "transcript.txt")
            with open(transcript_file, "w", encoding="utf-8") as f:
                for entry in transcription:
                    f.write(f"{entry['start']}: {entry['text']}\n")

            print(f"Transcription for language '{lang}' saved to {transcript_file}")

        return transcripts_by_language

    except Exception as e:
        print(f"Error fetching transcriptions: {str(e)}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch YouTube video transcriptions in specified languages."
    )
    parser.add_argument("url", type=str, help="The YouTube video URL")
    parser.add_argument(
        "languages", nargs="+", help="List of language codes (e.g., 'en', 'es', 'fr')"
    )
    args = parser.parse_args()
    video_url = args.url
    languages = args.languages

    print(f"Fetching transcriptions for video: {video_url}")

    transcriptions = fetch_youtube_transcriptions(video_url, languages)

    if transcriptions:
        for lang, transcription in transcriptions.items():
            print(f"Saves transcription in {lang}")
            print("\n")
