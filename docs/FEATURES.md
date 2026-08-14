# Feature Reference

## Agent feedback loop

The application performs multiple model calls rather than stopping after the first response. Tool outputs are inserted into conversation history, allowing later reasoning cycles to use real execution results.

## Tool calling

The model can request structured function calls. The dispatcher maps each request to a local Python implementation and returns the result using the matching tool-call ID.

## Project inspection

`get_files_info` lets the agent discover the structure of the working directory before deciding which files need closer inspection.

## Source reading

`get_file_content` allows the agent to retrieve the contents of specific project files.

## File modification

`write_file` allows the model to create or replace project files within the permitted working directory.

## Python execution

`run_python_file` executes Python programs and returns stdout/stderr to the agent. This makes test-driven iteration possible.

## Interactive sessions

Running `uv run main.py` without a prompt starts a persistent shell. The same conversation history remains available until `/reset` or `/quit`.

## Adaptive terminal UI

The interface calculates a stable width from the active terminal and uses straight horizontal rules instead of fixed box-drawing corners. This avoids broken or misaligned borders when terminals render Unicode characters with slightly different widths.

## Guided first-run setup

If `OPENROUTER_API_KEY` is missing, the application prompts for it automatically rather than exiting with an error.

The key is entered using hidden terminal input and can either be saved to the local Git-ignored `.env` file or used for only the current session.

## In-app configuration

The `/configure` command reruns the secure setup wizard without leaving the interactive agent.

The same action is available from the shell:

```bash
uv run main.py --configure
```

## Single-command mode

A task can be passed directly:

```bash
uv run main.py "inspect the calculator and explain how it works"
```

## Configuration

Runtime behavior can be adjusted through CLI flags or environment variables:

- `AI_AGENT_MODEL`
- `AI_AGENT_MAX_ITERATIONS`
- `AI_AGENT_MAX_TOKENS`
- `OPENROUTER_BASE_URL`

## Safety limits

Agent reasoning cycles are bounded to prevent accidental infinite loops and excessive token consumption.

## Friendly API errors

Common authentication, credit, model availability, and rate-limit errors are translated into shorter actionable messages.

## Secret isolation

API credentials are kept outside source code. Saved credentials live in `.env`, which is excluded from Git.
