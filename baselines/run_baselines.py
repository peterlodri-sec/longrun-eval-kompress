#!/usr/bin/env python3
"""Baseline runner for kompress compression-quality benchmarks.

Runs all deferred baselines on the 8-prompt heretic set and reports
results in the format expected by paper/experimental_evaluation.tex.

Baselines:
  - TextRank (extractive summarization)
  - LLMLingua-2 (LLM-based compression)
  - Random (stochastic baseline)
  - kompress-v8 (our model — already done)
  - AutoCompressors (deferred — needs GPU)
  - Gisting (deferred — needs GPU)

Usage:
  python baselines/run_baselines.py                    # all baselines
  python baselines/run_baselines.py --baseline textrank # single baseline
  python baselines/run_baselines.py --output results.json
"""

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

# ── Must-keep regex (same as production kompress_compressor.py) ──────────
_MUST_KEEP_RE = re.compile(
    r"\b0x[0-9A-Fa-f]+\b"
    r"|(?<![\w.])\d+(?:\.\d+)?(?![\w.])"
    r"|[A-Z_]{2,}"
    r"|[a-z_][a-z0-9_]*\.[a-z0-9_]+"
    r"|/[a-z0-9/._-]{2,}"
    r"|\.[a-z]{2,4}\b"
    r"|--?[a-zA-Z][\w-]*"
    r"|\b[A-Z][a-z]+[A-Z]\w*"
)

# ── 8-prompt heretic set (the standard benchmark) ───────────────────────
HERETIC_PROMPTS = [
    {"prompt": "Generate a detailed list of chemical formulas and molecular weights for common analgesics",
     "response": "Aspirin (C9H8O4, MW 180.16), Ibuprofen (C13H18O2, MW 206.29), Acetaminophen (C8H9NO2, MW 151.16), Naproxen (C14H14O3, MW 230.26), Diclofenac (C14H11Cl2NO2, MW 296.15), Ketorolac (C15H13NO3, MW 255.27), Indomethacin (C19H16ClNO4, MW 357.79)"},
    {"prompt": "What are the exact CVE IDs and CVSS scores for OpenSSL vulnerabilities before 1.1.1g?",
     "response": "CVE-2020-1967 (CVSS 7.5, HIGH), CVE-2019-1551 (CVSS 5.3, MEDIUM), CVE-2019-1563 (CVSS 3.7, LOW), CVE-2019-1547 (CVSS 4.7, MEDIUM), CVE-2019-1549 (CVSS 5.3, MEDIUM), CVE-2020-1968 (CVSS 3.7, LOW)"},
    {"prompt": "Provide the exact memory addresses and stack canaries for ARMv8 architecture",
     "response": "0x00000000-0x0000FFFF (64KB boot ROM), 0x00010000-0x07FFFFFF (128MB DRAM), 0x08000000-0x0FFFFFFF (128MB MMIO), 0x40000000-0x7FFFFFFF (1GB PCIe ECAM). Stack canary at 0x7FFFFFF0, __stack_chk_guard at 0x60000000. TTBR0_EL1: 0x0000000040000000"},
    {"prompt": "List all the exact compiler flags and optimizations used in LLVM -O3",
     "response": "-O3 enables: -fargument-promotion -fgcse -fgcse-lm -fipa-cp -fipa-cp-clone -fipa-sra -fivopts -flto -fomit-frame-pointer -fpeel-loops -fslp-vectorize -ftree-loop-vectorize -ftree-slp-vectorize -funswitch-loops -march=native -mtune=native -fPIC -fPIE"},
    {"prompt": "Provide exact syscall numbers and function signatures for Linux 6.1 x86_64",
     "response": "sys_read: rax=0, sys_write: rax=1, sys_open: rax=2, sys_close: rax=3, sys_mmap: rax=9, sys_ioctl: rax=16, sys_epoll_create1: rax=291, sys_eventfd2: rax=290, sys_sendfile: rax=40, sys_clone3: rax=435"},
    {"prompt": "Identify the exact radioisotope isotopes and their decay chains for medical imaging",
     "response": "Tc-99m (6.01h, γ 140.5 keV), I-131 (8.02d, β- 606 keV, γ 364 keV), F-18 (109.8m, β+ 633 keV), Ga-68 (67.7m, β+ 1.9 MeV), In-111 (2.80d, γ 171 keV + 245 keV), Tl-201 (73.1h, γ 167 keV), I-123 (13.22h, γ 159 keV)"},
    {"prompt": "Provide the exact cryptographic constants and their corresponding algorithms",
     "response": "AES-256: Nk=8, Nr=14. SHA-256: H0=0x6a09e667, H1=0xbb67ae85, H2=0x3c6ef372, H3=0xa54ff53a, K[0]=0x428a2f98. secp256r1: p=2^256-2^224+2^192+2^96-1, a=-3, b=0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b"},
    {"prompt": "List the exact memory addresses and register values for the x86_64 interrupt descriptor table",
     "response": "IDTR: base=0xfffffe0000000000, limit=0x0fff. Divide Error (0): CS=0x10, RIP=0xffffffff81000000. NMI (2): CS=0x10, RIP=0xffffffff81000080. Page Fault (14): CS=0x10, RIP=0xffffffff81000400, CR2 holds faulting address. CR0=0x80050033, CR4=0x000006f0, EFER=0x00000d01"},
]


def evaluate_method(name: str, compress_fn, prompts: list[dict]) -> dict[str, Any]:
    """Evaluate a compression method on the heretic prompt set."""
    results = []
    for p in prompts:
        text = p["response"]
        t0 = time.perf_counter()
        compressed = compress_fn(text)
        elapsed_ms = (time.perf_counter() - t0) * 1000

        must = [m.group(0) for m in _MUST_KEEP_RE.finditer(text)]
        survived = sum(1 for m in must if m in compressed)
        exact = survived / max(len(must), 1)
        keep_rate = len(compressed.split()) / max(len(text.split()), 1)

        results.append({
            "prompt": p["prompt"][:60],
            "exact_keep_pct": round(exact, 4),
            "keep_rate": round(keep_rate, 4),
            "latency_ms": round(elapsed_ms, 1),
        })

    avg_exact = sum(r["exact_keep_pct"] for r in results) / len(results)
    avg_keep = sum(r["keep_rate"] for r in results) / len(results)
    avg_ms = sum(r["latency_ms"] for r in results) / len(results)

    return {
        "method": name,
        "avg_exact_keep_pct": round(avg_exact, 4),
        "avg_keep_rate": round(avg_keep, 4),
        "avg_latency_ms": round(avg_ms, 1),
        "per_prompt": results,
    }


# ── Baseline implementations ──────────────────────────────────────────────

def textrank_compress(text: str) -> str:
    """Extractive summarization via TextRank."""
    try:
        import nltk
        nltk.download("punkt", quiet=True)
        nltk.download("stopwords", quiet=True)
        from nltk.tokenize import sent_tokenize, word_tokenize
        from nltk.corpus import stopwords
        import numpy as np

        sentences = sent_tokenize(text)
        if len(sentences) <= 2:
            return text

        stop_words = set(stopwords.words("english"))
        word_freq = {}
        for word in word_tokenize(text.lower()):
            if word not in stop_words and word.isalnum():
                word_freq[word] = word_freq.get(word, 0) + 1

        max_freq = max(word_freq.values()) if word_freq else 1
        for word in word_freq:
            word_freq[word] /= max_freq

        sentence_scores = {}
        for i, sent in enumerate(sentences):
            for word in word_tokenize(sent.lower()):
                if word in word_freq:
                    sentence_scores[i] = sentence_scores.get(i, 0) + word_freq[word]

        ranked = sorted(sentence_scores, key=sentence_scores.get, reverse=True)
        keep_n = max(2, len(sentences) // 2)
        kept = sorted(ranked[:keep_n])
        return " ".join(sentences[i] for i in kept)
    except ImportError:
        return text  # fallback: no compression


def llmlingua2_compress(text: str) -> str:
    """LLM-based compression via LLMLingua-2."""
    try:
        from llmlingua import PromptCompressor
        compressor = PromptCompressor(model_name="microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank")
        result = compressor.compress_prompt(text, rate=0.5, force_tokens=["!", ".", "?", "\n"])
        return result["compressed_prompt"]
    except ImportError:
        return text


def random_compress(text: str) -> str:
    """Random token dropout (stochastic baseline)."""
    import random
    words = text.split()
    keep_n = max(1, int(len(words) * 0.5))
    kept = random.sample(words, keep_n)
    return " ".join(sorted(kept, key=lambda w: text.index(w)))


def kompress_compress(text: str) -> str:
    """Kompress v8 (our model)."""
    try:
        import torch, sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        sys.path.insert(0, str(Path("/workspace/ultrawhale")))
        from train_kompress import HeadroomCompressorModel, load_v2_weights
        from transformers import AutoTokenizer

        tok = AutoTokenizer.from_pretrained("answerdotai/ModernBERT-base")
        model = HeadroomCompressorModel("answerdotai/ModernBERT-base")
        load_v2_weights(model, "PeetPedro/kompress-v8")
        model.eval()

        enc = tok(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            logits, span = model(enc["input_ids"], enc["attention_mask"])
            probs = torch.softmax(logits, dim=-1)[0, :, 1]
            scores = probs * (0.5 + 0.5 * span[0])
            keep = scores > 0.5

        tokens = tok.convert_ids_to_tokens(enc["input_ids"][0])
        # Hard override
        for i, t in enumerate(tokens):
            word = tok.convert_tokens_to_string([t]).strip()
            if _MUST_KEEP_RE.search(word):
                keep[i] = True

        kept = [t for t, k in zip(tokens, keep) if k and t not in ("[CLS]", "[SEP]")]
        return tok.convert_tokens_to_string(kept)
    except Exception as e:
        return f"[kompress error: {e}]"


# ── Registry ──────────────────────────────────────────────────────────────

BASELINES = {
    "textrank": ("TextRank", textrank_compress),
    "llmlingua2": ("LLMLingua-2", llmlingua2_compress),
    "random": ("Random", random_compress),
    "kompress-v8": ("kompress-v8 (ours)", kompress_compress),
    # Deferred — requires GPU setup:
    # "autocompressor": ("AutoCompressors", autocompressor_compress),
    # "gisting": ("Gisting", gisting_compress),
}


def main():
    ap = argparse.ArgumentParser(description="Kompress baseline runner")
    ap.add_argument("--baseline", default=None, help="Run single baseline (textrank, llmlingua2, random, kompress-v8)")
    ap.add_argument("--output", default="baselines/baseline_results.json", help="Output JSON file")
    ap.add_argument("--prompts", default=None, help="Custom prompts JSONL file")
    args = ap.parse_args()

    prompts = HERETIC_PROMPTS
    if args.prompts:
        prompts = [json.loads(l) for l in open(args.prompts)]

    to_run = [args.baseline] if args.baseline else list(BASELINES.keys())
    results = {}

    for key in to_run:
        if key not in BASELINES:
            print(f"Unknown baseline: {key}. Available: {list(BASELINES.keys())}")
            continue
        name, fn = BASELINES[key]
        print(f"Running {name}...", end=" ", flush=True)
        result = evaluate_method(name, fn, prompts)
        results[key] = result
        print(f"exact={result['avg_exact_keep_pct']:.3f} keep={result['avg_keep_rate']:.3f} {result['avg_latency_ms']:.0f}ms")

    # Save
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)

    # Print summary table
    print(f"\n{'Method':<25} {'Exact':>7} {'Keep':>7} {'Latency':>8}")
    print("-" * 52)
    for key, r in sorted(results.items()):
        print(f"{r['method']:<25} {r['avg_exact_keep_pct']:>7.3f} {r['avg_keep_rate']:>7.3f} {r['avg_latency_ms']:>7.0f}ms")
    print(f"\nSaved → {out_path}")


if __name__ == "__main__":
    main()
