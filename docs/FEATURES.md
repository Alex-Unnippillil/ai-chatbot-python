# Feature Reference

## Agent Feedback Loop

The application performs multiple model calls rather than stopping after
the first response. Tool outputs are inserted into conversation history,
allowing later reasoning cycles to use real execution results.

## Tool Calling

The model can request structured function calls. The dispatcher maps each
request to a local Python implementation and returns the result using the
matching tool-call ID.

## Project Inspection

`get_files_info` lets the agent discover the structure of the working
directory before deciding which files need closer inspection.

## Source Reading

`get_file_content` allows the agent to retrieve the contents of specific
project files.

## File Modification

`write_file` allows the model to create or replace project files within
the permitted working directory.

## Python Execution

`run_python_file` executes Python programs and returns stdout/stderr to the
agent. This makes test-driven iteration possible.

## Interactive Sessions

Running `uv run main.py` without a prompt starts a persistent shell. The
same conversation history remains available until `/reset` or `/quit`.

## Single-Command Mode

A task can be passed directly:

```bash
uv run main.py "inspect the calculator and explain how it works"
```

## Configuration

Runtime behavior can be adjusted through CLI flags or environment
variables:

- `AI_AGENT_MODEL`
- `AI_AGENT_MAX_ITERATIONS`
- `AI_AGENT_MAX_TOKENS`
- `OPENROUTER_BASE_URL`

## Safety Limits

Agent reasoning cycles are bounded to prevent accidental infinite loops
and excessive token consumption.

## Friendly API Errors

Common authentication, credit, model availability, and rate-limit errors
are translated into shorter actionable messages.

## Secret Isolation

API credentials are read from `.env`; that file is excluded from Git.
