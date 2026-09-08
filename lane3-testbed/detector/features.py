"""Simple, interpretable text features for the feature-baseline detector
and for the fluency-proxy analysis in Day 2 part 2.

No external NLP dependencies -- everything here is stdlib string/regex
arithmetic, which is enough to define legible fluency and style proxies.
"""

import re

_WORD_RE = re.compile(r"[A-Za-z']+")
_SENT_SPLIT_RE = re.compile(r"[.!?]+")


def word_tokens(text: str) -> list[str]:
    return _WORD_RE.findall(text)


def sentences(text: str) -> list[str]:
    parts = [s.strip() for s in _SENT_SPLIT_RE.split(text)]
    return [s for s in parts if s]


def feature_dict(text: str) -> dict:
    words = word_tokens(text)
    n_words = len(words)
    sents = sentences(text)
    n_sents = max(len(sents), 1)
    lower_words = [w.lower() for w in words]
    n_unique = len(set(lower_words))
    char_len = len(text)

    punct_count = sum(1 for c in text if c in ".,;:!?")
    comma_count = text.count(",")

    return {
        "n_words": n_words,
        "n_sentences": n_sents,
        "n_chars": char_len,
        "avg_word_len": (sum(len(w) for w in words) / n_words) if n_words else 0.0,
        "avg_sentence_len_words": n_words / n_sents,
        "type_token_ratio": (n_unique / n_words) if n_words else 0.0,
        "punct_per_100_words": (100 * punct_count / n_words) if n_words else 0.0,
        "comma_per_100_words": (100 * comma_count / n_words) if n_words else 0.0,
    }


FEATURE_NAMES = [
    "n_words",
    "n_sentences",
    "avg_word_len",
    "avg_sentence_len_words",
    "type_token_ratio",
    "punct_per_100_words",
    "comma_per_100_words",
]


def feature_vector(text: str) -> list[float]:
    d = feature_dict(text)
    return [d[k] for k in FEATURE_NAMES]
