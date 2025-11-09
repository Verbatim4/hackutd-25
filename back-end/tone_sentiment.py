# speech_tone.py
import warnings
import os
import logging
from transformers import pipeline

# --- Silence all logs, warnings, and progress ---
warnings.filterwarnings("ignore")
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["PYTHONWARNINGS"] = "ignore"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

# Disable logging for noisy modules
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("torch").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)

# --- Load models once (quietly) ---
_asr = pipeline("automatic-speech-recognition", model="openai/whisper-base", device=-1)
_ser = pipeline("audio-classification", model="superb/wav2vec2-base-superb-er", device=-1)
_sentiment = pipeline("text-classification", model="cardiffnlp/twitter-roberta-base-sentiment-latest", return_all_scores=True, device=-1)


def transcribe_audio(audio_path: str) -> str:
    return _asr(audio_path)["text"].strip()


def detect_emotion(audio_path: str) -> list:
    return _ser(audio_path)


def analyze_sentiment(text: str) -> list:
    return _sentiment(text)[0]


# --- Optional: Test directly when run standalone ---
if __name__ == "__main__":
    AUDIO_FILE = "sample.wav"

    transcript = transcribe_audio(AUDIO_FILE)
    emotion = detect_emotion(AUDIO_FILE)
    sentiment = analyze_sentiment(transcript)

    print("Transcript:", transcript)
    print("\nDetected emotion(s):")
    print(emotion)
    print(sentiment)
