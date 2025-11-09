# negativity_score.py
from tone_sentiment import transcribe_audio, detect_emotion, analyze_sentiment

# Define which emotions are considered negative
NEGATIVE_EMOTIONS = {"ang", "sad"}


def compute_negativity(audio_path: str) -> dict:
    """
    Compute a total negativity score (0 to 1) based on both emotion and sentiment data.
    """
    # Step 1: Transcribe and analyze
    transcript = transcribe_audio(audio_path)
    emotions = detect_emotion(audio_path)
    sentiment_scores = analyze_sentiment(transcript)

    # --- Emotion negativity ---
    emotion_neg = 0.0
    total_weight = 0.0
    for e in emotions:
        label = e["label"].lower()
        score = e["score"]
        total_weight += score
        if any(neg in label for neg in NEGATIVE_EMOTIONS):
            emotion_neg += score
    if total_weight > 0:
        emotion_neg /= total_weight  # normalize to 0–1

    # --- Sentiment negativity ---
    sentiment_neg = 0.0
    for s in sentiment_scores:
        if s["label"].lower() == "negative":
            sentiment_neg = s["score"]

    # --- Combined negativity (weighted) ---
    total_negativity = 0.6 * sentiment_neg + 0.4 * emotion_neg

    return {
        "transcript": transcript,
        "emotion_negativity": round(emotion_neg, 3),
        "sentiment_negativity": round(sentiment_neg, 3),
        "total_negativity": round(total_negativity, 3),
    }


# --- Optional test ---
if __name__ == "__main__":
    AUDIO_FILE = "sample.wav"
    result = compute_negativity(AUDIO_FILE)
    print("\nNegativity Analysis:")
    for k, v in result.items():
        print(f"{k}: {v}")
