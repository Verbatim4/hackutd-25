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
    """
    Transcribe an audio file into text using Whisper.

    Args:
        audio_path (str): Path to the input audio file.

    Returns:
        str: The transcribed text string.
    """
    return _asr(audio_path)["text"].strip()


def detect_emotion(audio_path: str) -> list:
    """
    Perform speech emotion recognition on an audio file.

    Args:
        audio_path (str): Path to the input audio file.

    Returns:
        list: A list of dictionaries, each containing:
              {
                  'label': str,   # predicted emotion
                  'score': float  # confidence score
              }
    """
    return _ser(audio_path)


def analyze_sentiment(text: str) -> list:
    """
    Perform sentiment analysis on text and return all label-score pairs.

    Args:
        text (str): The input text to analyze.

    Returns:
        list: A list of dictionaries, each containing:
              {
                  'label': str,   # sentiment label (e.g., negative, neutral, positive)
                  'score': float  # confidence score for that label
              }
    """
    return _sentiment(text)[0]


# --- Optional: Test directly when run standalone ---
if __name__ == "__main__":
    AUDIO_FILE = "sample.wav"

    transcript = transcribe_audio(AUDIO_FILE)
    emotion = detect_emotion(AUDIO_FILE)
    sentiment = analyze_sentiment(transcript)

    print("Transcript:", transcript)
    print("\nDetected emotion(s):")
    for e in emotion:
        print(f"  {e['label']}: {e['score']:.3f}")

    print("\nText sentiment(s):")
    for s in sentiment:
        print(f"  {s['label']}: {s['score']:.3f}")
