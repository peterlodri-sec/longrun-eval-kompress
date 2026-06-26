"""Experiment: compress prompts, classify sentiment, log results.

The experiment takes a compression spec (from the loop's Plan phase),
applies it to the dataset, runs a simple keyword-based classifier,
and returns accuracy + compression ratio.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from data import PROMPTS

# Simple sentiment lexicon (word -> score)
LEXICON = {
    # Strong positive
    "amazing": 2, "love": 2, "excellent": 2, "outstanding": 2, "fantastic": 2,
    "incredible": 2, "perfect": 2, "best": 2, "great": 1.5, "happy": 1.5,
    "impressed": 1.5, "satisfied": 1.5, "recommend": 1.5, "reliable": 1,
    "solid": 1, "good": 1, "fine": 0.5, "decent": 0.5, "works": 0.5,
    # Strong negative
    "terrible": -2, "worst": -2, "awful": -2, "horrible": -2, "useless": -2,
    "garbage": -2, "trash": -2, "junk": -2, "defective": -2, "broken": -1.5,
    "broke": -1.5, "waste": -1.5, "scam": -2, "ripoff": -2, "disappointed": -1.5,
    "poor": -1, "cheap": -1, "bad": -1, "never": -1, "refused": -1.5,
}

STOPWORDS = {
    "a", "an", "the", "is", "it", "in", "on", "at", "to", "for", "of",
    "and", "or", "but", "not", "with", "this", "that", "was", "are", "be",
    "has", "had", "have", "do", "does", "did", "will", "would", "could",
    "should", "can", "may", "might", "shall", "its", "i", "my", "me",
    "we", "our", "you", "your", "he", "she", "they", "them", "their",
}


@dataclass
class CompressionSpec:
    """Defines how to compress prompts."""
    name: str
    max_words: int | None = None
    remove_stopwords: bool = False
    extract_keywords: bool = False
    keyword_top_n: int = 10
    keep_positive_only: bool = False


def classify(text: str) -> str:
    """Simple lexicon-based sentiment classifier."""
    words = re.findall(r"\w+", text.lower())
    score = sum(LEXICON.get(w, 0) for w in words)
    return "POSITIVE" if score >= 0 else "NEGATIVE"


def compress(text: str, spec: CompressionSpec) -> str:
    """Apply compression spec to a prompt."""
    words = text.split()

    if spec.max_words and len(words) > spec.max_words:
        words = words[:spec.max_words]

    if spec.remove_stopwords:
        words = [w for w in words if w.lower().strip(".,!?") not in STOPWORDS]

    if spec.extract_keywords:
        # Keep words with highest absolute sentiment score
        scored = [(w, abs(LEXICON.get(w.lower().strip(".,!?"), 0))) for w in words]
        scored.sort(key=lambda x: -x[1])
        words = [w for w, s in scored[:spec.keyword_top_n] if s > 0]
        if not words:
            words = text.split()[:5]  # fallback

    if spec.keep_positive_only:
        words = [w for w in words if LEXICON.get(w.lower().strip(".,!?"), 0) >= 0]

    return " ".join(words)


def run_experiment(spec: CompressionSpec) -> dict:
    """Run the full experiment: compress → classify → measure."""
    correct = 0
    total = 0
    original_words = 0
    compressed_words = 0

    for prompt, label in PROMPTS:
        compressed = compress(prompt, spec)
        predicted = classify(compressed)

        if predicted == label:
            correct += 1
        total += 1
        original_words += len(prompt.split())
        compressed_words += len(compressed.split())

    accuracy = correct / total if total > 0 else 0.0
    compression_ratio = compressed_words / original_words if original_words > 0 else 1.0

    return {
        "accuracy": round(accuracy, 4),
        "compression_ratio": round(compression_ratio, 4),
        "correct": correct,
        "total": total,
        "original_words": original_words,
        "compressed_words": compressed_words,
    }
