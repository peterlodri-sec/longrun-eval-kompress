"""Experiment: generate slugs from titles, measure readability + brevity.

Each slug strategy transforms page titles into URL-friendly slugs.
The evaluation measures readability (word preservation) and brevity (length).
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from data import TITLES

STOPWORDS = {
    "a", "an", "the", "is", "it", "in", "on", "at", "to", "for", "of",
    "and", "or", "but", "with", "by", "from", "your", "a",
}


@dataclass
class SlugSpec:
    """Defines how to generate slugs."""
    name: str
    max_words: int | None = None
    remove_stopwords: bool = False
    remove_vowels: bool = False
    truncate_title: int | None = None
    keep_first_n: int | None = None
    lowercase: bool = True
    use_hyphens: bool = True


def generate_slug(title: str, spec: SlugSpec) -> str:
    """Generate a URL slug from a page title."""
    text = title.lower() if spec.lowercase else title

    # Truncate title to N chars
    if spec.truncate_title:
        text = text[:spec.truncate_title]

    # Split into words
    words = re.findall(r"[a-z0-9]+", text)

    # Remove stopwords
    if spec.remove_stopwords:
        words = [w for w in words if w not in STOPWORDS]

    # Keep first N words
    if spec.keep_first_n:
        words = words[:spec.keep_first_n]
    elif spec.max_words:
        words = words[:spec.max_words]

    # Remove vowels from long words
    if spec.remove_vowels:
        words = [
            re.sub(r"[aeiou]", "", w) if len(w) > 4 else w
            for w in words
        ]

    # Filter empty
    words = [w for w in words if w]

    sep = "-" if spec.use_hyphens else "_"
    return sep.join(words)


def run_experiment(spec: SlugSpec) -> dict:
    """Run the full experiment: generate slugs -> measure metrics."""
    total_slug_chars = 0
    total_title_chars = 0
    readability_hits = 0
    readability_total = 0

    for title in TITLES:
        slug = generate_slug(title, spec)
        total_slug_chars += len(slug)
        total_title_chars += len(title)

        # Readability: does the slug contain recognizable words from the title?
        title_words = set(re.findall(r"[a-z]{3,}", title.lower()))
        slug_words = set(re.findall(r"[a-z]{3,}", slug.lower()))
        if title_words:
            overlap = len(title_words & slug_words) / len(title_words)
            readability_hits += overlap
            readability_total += 1

    avg_readability = readability_hits / readability_total if readability_total > 0 else 0.0
    avg_length = total_slug_chars / len(TITLES) if TITLES else 0
    compression = total_slug_chars / total_title_chars if total_title_chars > 0 else 1.0

    return {
        "avg_readability": round(avg_readability, 4),
        "avg_slug_length": round(avg_length, 1),
        "compression": round(compression, 4),
        "total_slugs": len(TITLES),
    }
