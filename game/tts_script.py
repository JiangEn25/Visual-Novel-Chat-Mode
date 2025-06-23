import sys
import os
from gtts import gTTS

def generate_audio(text, lang='en', output_dir='audio', output_file='temp_audio.mp3'):
    """
    Generate audio file from text using gTTS.

    :param text: Text to be converted to speech.
    :param lang: Language of the text (default is 'en').
    :param output_dir: Directory to save the generated audio file.
    :param output_file: Name of the output audio file.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_path = os.path.join(output_dir, output_file)
    tts = gTTS(text=text, lang=lang)
    tts.save(output_path)
    print(f"Audio file generated at {os.path.abspath(output_path)}")
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tts_script.py '<text>' [lang] [output_dir] [output_file]")
        sys.exit(1)

    text = sys.argv[1]
    lang = sys.argv[2] if len(sys.argv) > 2 else 'en'
    output_dir = sys.argv[3] if len(sys.argv) > 3 else 'audio'
    output_file = sys.argv[4] if len(sys.argv) > 4 else 'temp_audio.mp3'

    generate_audio(text, lang, output_dir, output_file)