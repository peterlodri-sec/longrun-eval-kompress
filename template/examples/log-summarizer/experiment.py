"""Experiment: summarize logs, measure information retention.

Each summarization strategy extracts different fields from verbose log lines.
The evaluation measures whether critical info (level, timestamp, error codes,
component) is retained while compression is achieved.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from data import LOGS


@dataclass
class SummarySpec:
    """Defines how to summarize log lines."""
    name: str
    keep_timestamp: bool = True
    keep_level: bool = True
    keep_component: bool = True
    keep_error_codes: bool = True
    keep_message: bool = True
    message_max_chars: int | None = None
    extract_fields: list[str] | None = None  # e.g. ["user_id", "error"]
    first_n_words: int | None = None


# Regex patterns for structured fields
ERROR_CODE_RE = re.compile(r"E\d{3}")
FIELD_RE = re.compile(r"(\w+=[^\s,]+)")


def summarize(log_line: str, spec: SummarySpec) -> str:
    """Apply summarization spec to a single log line."""
    parts = []

    # Extract timestamp
    ts_match = re.match(r"(\d{4}-\d{2}-\d{2}T[\d:.]+Z)", log_line)
    if spec.keep_timestamp and ts_match:
        parts.append(ts_match.group(1))

    # Extract level
    level_match = re.search(r"\b(INFO|WARN|ERROR|DEBUG|FATAL)\b", log_line)
    if spec.keep_level and level_match:
        parts.append(level_match.group(1))

    # Extract component
    comp_match = re.search(r"\[(\w+)\]", log_line)
    if spec.keep_component and comp_match:
        parts.append(f"[{comp_match.group(1)}]")

    # Extract error codes
    if spec.keep_error_codes:
        codes = ERROR_CODE_RE.findall(log_line)
        if codes:
            parts.extend(codes)

    # Extract specific fields
    if spec.extract_fields:
        for field in spec.extract_fields:
            field_match = re.search(rf"{field}=([^\s,]+)", log_line)
            if field_match:
                parts.append(f"{field}={field_match.group(1)}")

    # Extract message (everything after the structured prefix)
    if spec.keep_message:
        msg_match = re.search(r"\[(?:auth|db|api|cache)\]\s*(.*)", log_line)
        if msg_match:
            msg = msg_match.group(1)
            if spec.message_max_chars:
                msg = msg[:spec.message_max_chars]
            if spec.first_n_words:
                msg = " ".join(msg.split()[:spec.first_n_words])
            parts.append(msg)

    return " | ".join(parts)


def run_experiment(spec: SummarySpec) -> dict:
    """Run the full experiment: summarize -> measure retention."""
    original_chars = 0
    summarized_chars = 0
    retention_hits = 0
    retention_total = 0

    critical_fields = ["level", "timestamp", "component", "error_code"]

    for log_line in LOGS:
        summary = summarize(log_line, spec)
        original_chars += len(log_line)
        summarized_chars += len(summary)

        # Check retention of critical fields
        ts_orig = re.match(r"(\d{4}-\d{2}-\d{2}T[\d:.]+Z)", log_line)
        ts_summ = re.search(r"\d{4}-\d{2}-\d{2}T[\d:.]+Z", summary)
        if ts_orig:
            retention_total += 1
            if ts_summ:
                retention_hits += 1

        level_orig = re.search(r"\b(INFO|WARN|ERROR|DEBUG|FATAL)\b", log_line)
        level_summ = re.search(r"\b(INFO|WARN|ERROR|DEBUG|FATAL)\b", summary)
        if level_orig:
            retention_total += 1
            if level_summ:
                retention_hits += 1

        comp_orig = re.search(r"\[(\w+)\]", log_line)
        comp_summ = re.search(r"\[(\w+)\]", summary)
        if comp_orig:
            retention_total += 1
            if comp_summ:
                retention_hits += 1

        codes_orig = ERROR_CODE_RE.findall(log_line)
        codes_summ = ERROR_CODE_RE.findall(summary)
        if codes_orig:
            retention_total += 1
            if codes_summ and set(codes_orig) <= set(codes_summ):
                retention_hits += 1

    retention = retention_hits / retention_total if retention_total > 0 else 0.0
    compression = summarized_chars / original_chars if original_chars > 0 else 1.0

    return {
        "retention": round(retention, 4),
        "compression": round(compression, 4),
        "retention_hits": retention_hits,
        "retention_total": retention_total,
        "original_chars": original_chars,
        "summarized_chars": summarized_chars,
    }
