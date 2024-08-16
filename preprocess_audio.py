import os
import torchaudio
import argparse
import yt_dlp
from pytube import YouTube

ydl_opts = {"format": "bestaudio/best"}

def get_video_info(video_url):
    """Get video information from a YouTube URL."""
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            yt = YouTube(video_url)
            video_id = yt.video_id
            video_title = yt.title.replace(" ", "_")
            return video_id, video_title, info
    except Exception as e:
        raise RuntimeError(f"Failed to get video information: {e}")

def download_audio_clips(video_url, start_time=0, duration=10, output_dir="audio_clips"):
    """Download audio clips from a YouTube video and store them in a subdirectory."""
    try:
        # Extract video information using yt-dlp
        video_id, video_title, info = get_video_info(video_url)
        sub_dir = os.path.join(output_dir, f"{video_title}_{video_id}")

        # Check if subdirectory already exists and contains audio clips
        if os.path.exists(sub_dir) and os.listdir(sub_dir):
            print(f"Audio clips already exist in: {sub_dir}")
            return [os.path.join(sub_dir, f) for f in os.listdir(sub_dir) if f.endswith('.wav')]

        # Create subdirectory if it doesn't exist
        if not os.path.exists(sub_dir):
            os.makedirs(sub_dir)

        # Download the audio
        ydl_opts.update({
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
            }],
            "outtmpl": os.path.join(sub_dir, "%(title)s.%(ext)s"),
        })

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        filename = ydl.prepare_filename(info).replace(".webm", ".wav")

        # Extract audio clips
        audio_clips = []
        audio, sr = torchaudio.load(filename)

        num_samples = duration * sr
        start_sample = start_time * sr
        while start_sample < audio.size(1):
            end_sample = min(start_sample + num_samples, audio.size(1))
            clip = audio[:, start_sample:end_sample]
            audio_file = os.path.join(sub_dir, f"clip_{start_sample/sr:.2f}_{end_sample/sr:.2f}.wav")
            if not os.path.exists(audio_file):
                torchaudio.save(audio_file, clip, sr)
            audio_clips.append(audio_file)
            start_sample += num_samples

        return audio_clips

    except Exception as e:
        raise RuntimeError(f"Failed to download or process audio clips: {e}")

def prepare_for_cloning(audio_clips, output_dir="cloning_files", video_title="", video_id=""):
    """Prepare the necessary files for cross-lingual voice cloning."""
    try:
        # Create subdirectory in cloning_files based on video title and ID
        sub_dir = os.path.join(output_dir, f"{video_title}_{video_id}")
        if not os.path.exists(sub_dir):
            os.makedirs(sub_dir)

        for i, audio_clip in enumerate(audio_clips):
            wave, sr = torchaudio.load(audio_clip)
            target_clip = os.path.join(sub_dir, f"clip_{i}.wav")
            torchaudio.save(target_clip, wave, sr)

        print(f"Prepared {len(audio_clips)} audio clips for voice cloning in {sub_dir}.")
        return sub_dir
    except Exception as e:
        raise RuntimeError(f"Failed to prepare files for voice cloning: {e}")

def main(video_url):
    try:
        print("Downloading audio clips for:", video_url)
        audio_clips = download_audio_clips(video_url)
        print(f"Downloaded {len(audio_clips)} audio clips.")

        # Extract video information to pass to prepare_for_cloning
        video_id, video_title, _ = get_video_info(video_url)

        print("Preparing files for cross-lingual voice cloning...")
        cloning_files_dir = prepare_for_cloning(audio_clips, video_title=video_title, video_id=video_id)

        print(f"All files prepared in {cloning_files_dir}. You can now start cross-lingual voice cloning.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download audio clips from a YouTube video and prepare for cross-lingual voice cloning.")
    parser.add_argument("video_url", type=str, help="The YouTube video URL to download audio from")
    args = parser.parse_args()

    main(args.video_url)
