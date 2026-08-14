# Usage Guide

## Start Interactive Mode

```bash
uv run main.py
```

Then enter normal-language coding requests:

```text
agent › inspect the calculator project
```

## Run One Request

```bash
uv run main.py "explain the calculator architecture"
```

## Verbose Tool Output

```bash
uv run main.py "inspect the project" --verbose
```

## Choose a Model

```bash
uv run main.py \
  --model "provider/model-name" \
  "inspect the project"
```

## Change Agent Limits

```bash
uv run main.py \
  --max-iterations 8 \
  --max-tokens 2048 \
  "fix and test the calculator"
```

## Environment Configuration

`.env` example:

```text
OPENROUTER_API_KEY=your_key_here
AI_AGENT_MODEL=google/gemini-2.5-flash
AI_AGENT_MAX_ITERATIONS=20
AI_AGENT_MAX_TOKENS=4096
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

## Useful Prompt Patterns

### Understand code

```text
Inspect the calculator project and explain how expressions are evaluated.
```

### Diagnose a bug

```text
Find why 3 + 7 * 2 returns the wrong value. Fix it and verify the result.
```

### Review a project

```text
Inspect this codebase and identify the three highest-value improvements.
```

### Test a change

```text
Run the relevant Python program, investigate failures, and make the
smallest change required to fix them.
```
