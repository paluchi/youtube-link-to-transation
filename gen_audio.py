import os
from TTS.api import TTS


def warmup_tts_model(
    model_name="tts_models/multilingual/multi-dataset/your_tts", use_cuda=False
):
    """Load and warm up the YourTTS model."""
    try:
        tts = TTS(model_name=model_name, progress_bar=False, gpu=use_cuda)
        print("TTS Model loaded and warmed up.")
        return tts
    except Exception as e:
        raise RuntimeError(f"Failed to load and warm up the TTS model: {e}")


def load_transcriptions(transcription_file):
    """Load transcriptions from a file."""
    with open(transcription_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    transcriptions = []
    for line in lines:
        if ": " in line:
            time_stamp, text = line.split(": ", 1)
            transcriptions.append((float(time_stamp), text.strip()))
    return transcriptions


def generate_crosslingual_audio(subdirectory_name, language, tts_model):
    # Adjust the language code if necessary
    language_map = {
        'fr': 'fr-fr',
        'pt': 'pt-br',
        'es': 'es-es',
        # Add other mappings if needed
    }
    mapped_language = language_map.get(language, language)

    transcription_file = os.path.join("transcriptions", subdirectory_name, language, "transcript.txt")
    clips_dir = os.path.join("cloning_files", subdirectory_name)
    output_dir = os.path.join("outputs", subdirectory_name, language)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Load transcriptions
    transcriptions = load_transcriptions(transcription_file)

    # Concatenate all text and generate a single output
    combined_text = " ".join([text for _, text in transcriptions])
    output_file = os.path.join(output_dir, "combined_output.wav")

    # Use the first clip as a speaker reference
    first_clip_path = os.path.join(clips_dir, "clip_0.wav")
    tts_model.tts_to_file(text=combined_text, speaker_wav=first_clip_path, language=mapped_language, file_path=output_file)

    print(f"Generated combined audio: {output_file}")


def main(subdirectory_name, language):
    # Warm up the TTS model
    tts_model = warmup_tts_model()

    # Generate cross-lingual audio
    generate_crosslingual_audio(subdirectory_name, language, tts_model)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate cross-lingual audio using YourTTS.")
    parser.add_argument("subdirectory_name", type=str, help="Name of the subdirectory containing data.")
    parser.add_argument("language", type=str, help="Language code for cross-lingual generation (e.g., 'es').")

    args = parser.parse_args()
    subdirectory_name = args.subdirectory_name
    language = args.language

    main(subdirectory_name, language)
