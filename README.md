# LLM Zoomcamp 2026 - Homework 3: AI Orchestration

Homework source:
`cohorts/2026/03-orchestration/homework.md` in the main `llm-zoomcamp` repo

Lesson/flow source:
`03-orchestration` in the main `llm-zoomcamp` repo

The OpenAI key is loaded at runtime from the Kestra secret store (`OPENAI_API_KEY`). No API keys are stored in this repository.

## Final Answers

- Q1: AI Copilot has access to current Kestra plugin documentation
- Q2: Vague, generic, or fabricated - the model guesses from training data
- Q3: 60-100 tokens
- Q4: 2-5x more
- Q5: 2-4x more
- Q6: Use traditional task-based workflows for predictability and auditability

## Notes

Q1 is answered directly by the AI Copilot lesson: Kestra Copilot is grounded in current plugin documentation, valid property names, and best practices for the running Kestra version.

Q2 follows from the RAG lesson and the `1_chat_without_rag.yaml` log message: without retrieved release-note context, the model gives a generic or guessed answer about Kestra 1.1.

Q3-Q5 depend on model output and may vary slightly between runs. The selected choices are the closest buckets for the `4_simple_agent.yaml` flow:

- short `multilingual_agent` summaries are around one or two concise sentences, which fits the 60-100 output-token bucket better than the very small 5-15 bucket.
- long summaries are several times larger than short summaries, but not an order of magnitude larger.
- changing `english_brevity` from exactly 1 sentence to exactly 3 sentences produced a 1.73x ratio in the Kestra run and 2.22x in the local estimator. The "within 20%" bucket requires <=1.2x, which 1.73x exceeds; "2-4x more" is therefore the closest available option per the homework's pick-the-closest instruction.

## Reproduction

The original Kestra flow for Q5 was copied and modified here:

```bash
flows/4_simple_agent_3_sentences.yaml
```

OpenAI-provider copies used for Docker/Kestra runs:

```bash
flows/1_chat_without_rag_openai.yaml
flows/2_chat_with_rag_openai.yaml
flows/4_simple_agent_openai.yaml
flows/4_simple_agent_openai_3_sentences.yaml
```

An optional OpenAI-based estimator is included for local checking:

```bash
uv run scripts/openai_token_estimate.py
```

This estimator does not replace the Kestra UI logs required by the homework; it just reproduces the same prompt structure with OpenAI and reports API token usage.
Set the `OPENAI_API_KEY` environment variable or place it in a `.env` file at the path defined in `scripts/openai_token_estimate.py`.

Observed OpenAI estimator run:

- `multilingual_agent short`: 86 output tokens
- `multilingual_agent long`: 161 output tokens, 1.87x the short run
- `english_brevity` 1 sentence: 46 output tokens
- `english_brevity` 3 sentences: 102 output tokens, 2.22x the 1-sentence run

Observed Docker/Kestra run with `gpt-4o-mini` OpenAI-provider flow copies:

- short `4_simple_agent_openai` run:
  - `multilingual_agent` output tokens: 87
  - `english_brevity` output tokens: 59
- long `4_simple_agent_openai` run:
  - `multilingual_agent` output tokens: 169
  - `english_brevity` output tokens: 51
  - long/short `multilingual_agent` ratio: 1.94x
- long `4_simple_agent_openai_3_sentences` run:
  - `multilingual_agent` output tokens: 174
  - `english_brevity` output tokens: 88
  - 3-sentence/1-sentence `english_brevity` ratio: 1.73x

The original course flows use Gemini. Since I do not have a Gemini key, everything was adapted to use OpenAI; the Docker/Kestra runs use OpenAI provider flow copies. The multiple-choice answers above use the closest homework buckets.

