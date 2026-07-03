#!/usr/bin/env python3
"""Approximate Homework 3 token buckets with OpenAI Chat Completions."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path


ENV_PATH = Path(os.getenv("OPENAI_ENV_PATH", ".env"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

TEXT = """Kestra is an open-source orchestration platform that allows you to define workflows declaratively in YAML. It enables both developers and non-developers to automate tasks through a no-code interface, while keeping everything versioned, governed, secure, and auditable. Kestra extends easily for custom use cases through plugins and custom scripts.

Kestra follows a "start simple and grow as needed" philosophy. You can schedule a basic workflow in a few minutes, then later add Python scripts, Docker containers, or complex branching logic if the situation requires it. This makes Kestra ideal for data engineering, ETL pipelines, business process automation, and more.

In LLM Zoomcamp, we learn how to build production-ready LLM applications using RAG, vector search, agents, and evaluation. In this bonus module, we're exploring how AI can accelerate workflow development through AI Copilot, RAG, and autonomous agents."""


def load_env(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def chat(system: str, prompt: str) -> dict:
    api_key = os.environ["OPENAI_API_KEY"]
    body = {
        "model": MODEL,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    }
    data = json.dumps(body).encode()
    request = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        message = exc.read().decode(errors="replace")
        raise RuntimeError(f"OpenAI request failed: HTTP {exc.code}: {message}") from exc


def main() -> None:
    load_env(ENV_PATH)
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit(f"OPENAI_API_KEY not found. Checked {ENV_PATH}")

    system_short = """You are a precise technical assistant.
Produce a short summary in en.
Keep it factual, remove fluff, and avoid marketing language.
If the input is empty or non-text, return a one-sentence explanation.

Output format guidelines:
- For 'short': 1-2 sentences
- For 'medium': 2-5 sentences
- For 'long': 1-3 paragraphs"""

    system_long = system_short.replace("Produce a short summary", "Produce a long summary")
    prompt = f"Summarize the following content: {TEXT}"

    short = chat(system_short, prompt)
    long = chat(system_long, prompt)

    long_text = long["choices"][0]["message"]["content"]
    brevity_1 = chat(
        "You are a precise technical assistant.",
        f'Generate exactly 1 sentence English summary of the following:\n"{long_text}"',
    )
    brevity_3 = chat(
        "You are a precise technical assistant.",
        f'Generate exactly 3 sentences English summary of the following:\n"{long_text}"',
    )

    rows = [
        ("multilingual_agent short", short),
        ("multilingual_agent long", long),
        ("english_brevity 1 sentence", brevity_1),
        ("english_brevity 3 sentences", brevity_3),
    ]

    for label, response in rows:
        usage = response["usage"]
        text = response["choices"][0]["message"]["content"].replace("\n", " ")
        print(f"{label}:")
        print(f"  prompt_tokens={usage['prompt_tokens']}")
        print(f"  completion_tokens={usage['completion_tokens']}")
        print(f"  total_tokens={usage['total_tokens']}")
        print(f"  text={text}")
        print()

    short_out = short["usage"]["completion_tokens"]
    long_out = long["usage"]["completion_tokens"]
    one_out = brevity_1["usage"]["completion_tokens"]
    three_out = brevity_3["usage"]["completion_tokens"]
    print(f"long/short output-token ratio: {long_out / short_out:.2f}x")
    print(f"3-sentence/1-sentence output-token ratio: {three_out / one_out:.2f}x")


if __name__ == "__main__":
    main()
