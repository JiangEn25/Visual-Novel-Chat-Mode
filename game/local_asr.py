import sys
import json
import argparse
from vosk import Model, KaldiRecognizer
import sounddevice as sd
import queue

# 初始化队列
q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

def voice_input(model_path):
    model = Model(model_path)
    rec = KaldiRecognizer(model, 16000)

    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16', channels=1, callback=callback):
        print("Listening...", file=sys.stderr)  # 将调试信息输出到 stderr
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = rec.Result()
                try:
                    parsed_result = json.loads(result)
                    recognized_text = parsed_result.get("text", "")
                    print(f"\n最终识别文本: {recognized_text}", file=sys.stderr)  # 将调试信息输出到 stderr
                    return recognized_text
                except json.JSONDecodeError as e:
                    print(f"JSON Decode Error in ASR: {str(e)}", file=sys.stderr)
                    return f"JSON Decode Error in ASR: {str(e)}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Voice recognition script using Vosk.")
    parser.add_argument('--model', type=str, help='Path to the Vosk model.')
    args = parser.parse_args()

    try:
        print("Script started.", file=sys.stderr)
        language_model = args.model if args.model else "D:/renpy/myVN/myVN2/game/models/vosk-model-small-en-us-0.15"
        print(f"Using language model: {language_model}", file=sys.stderr)
        recognized_text = voice_input(language_model)
        # 返回识别结果
        sys.stdout.write(json.dumps({"recognized_text": recognized_text}))
        sys.stdout.flush()
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)