# Architecture

## High-Level Design

The project consists of three primary layers:

1. **CLI / session layer** — receives user requests and manages interaction.
2. **Agent loop** — sends conversation history to the LLM and evaluates the response.
3. **Tool layer** — performs controlled filesystem and Python operations.

## Agent Cycle

```text
┌──────────────┐
│ User request │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  LLM request │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│ Tool calls exist?│
└──────┬─────┬─────┘
       │yes  │no
       ▼     └────────────► Final response
┌──────────────┐
│ Execute tool │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│ Append tool result│
└────────┬─────────┘
         │
         └──────────────► Next LLM cycle
```

## Conversation Ordering

Tool-call protocols require strict ordering.

The application first appends the assistant message:

```python
message = response.choices[0].message
messages.append(message)
```

It then executes each requested tool and appends the corresponding result:

```python
result_message = call_function(tool_call)
messages.append(result_message)
```

This ensures every tool request is followed by a result with a matching
`tool_call_id` before the next model request.

## Tool Dispatcher

`call_function.py` acts as the boundary between model-generated tool calls
and local Python functions.

It is responsible for:

- identifying the requested function
- parsing JSON arguments
- invoking the correct implementation
- creating the tool-response message

## Working Directory Boundary

Filesystem tools operate relative to the configured working directory.
This is an important safety boundary and should remain intentionally
limited.

## Failure Handling

The outer application handles provider/API failures, while individual
tools return operation results to the model so it can reason about
recoverable coding failures.
