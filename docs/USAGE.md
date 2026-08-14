# Usage Guide

## Start interactive mode

```bash
uv run main.py
```

If no OpenRouter API key is configured, the application starts a secure first-run wizard automatically.

```text
────────────────────────────────────────────────────────────────────
                         FIRST-TIME SETUP
                  Secure OpenRouter configuration
────────────────────────────────────────────────────────────────────

No OpenRouter API key is configured.

OpenRouter API key: [hidden]
Save this key locally for future sessions? [Y/n]:
```

The API key is entered invisibly. If saved, it is stored only in the local `.env` file, which is ignored by Git.

## Reconfigure the API key

From the shell:

```bash
uv run main.py --configure
```

Or from inside an interactive session:

```text
/configure
```

## Interactive interface

The UI uses adaptive-width horizontal rules rather than fixed box corners, which keeps the header aligned across different terminal widths and fonts.

```text
────────────────────────────────────────────────────────────────────
                           AI CODING AGENT
                    Inspect • Modify • Test • Verify
────────────────────────────────────────────────────────────────────

  MODEL      google/gemini-2.5-flash
  COMMANDS   /help  /status  /tools  /configure
             /reset /clear   /quit

────────────────────────────────────────────────────────────────────

agent › inspect the calculator project
```

## Run one request

```bash
uv run main.py "explain the calculator architecture"
```

## Verbose tool output

```bash
uv run main.py "inspect the project" --verbose
```

## Choose a model

```bash
uv run main.py \
  --model "provider/model-name" \
  "inspect the project"
```

## Change agent limits

```bash
uv run main.py \
  --max-iterations 8 \
  --max-tokens 2048 \
  "fix and test the calculator"
```

## Environment configuration

Advanced users can configure the application directly with environment variables:

```text
OPENROUTER_API_KEY=your_key_here
AI_AGENT_MODEL=google/gemini-2.5-flash
AI_AGENT_MAX_ITERATIONS=20
AI_AGENT_MAX_TOKENS=4096
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

## Interactive commands

- `/help` — show command help and examples
- `/status` — show active model and session limits
- `/tools` — list available agent tools
- `/configure` — securely update the OpenRouter API key
- `/reset` — clear conversation history
- `/clear` — clear and redraw the terminal
- `/quit` — close the agent

## Useful prompt patterns

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
