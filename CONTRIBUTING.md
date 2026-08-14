# Contributing

Contributions are welcome.

## Development

Clone the project and install dependencies:

```bash
uv sync
```

Validate Python syntax:

```bash
uv run python -m compileall -q .
```

Run the sample calculator:

```bash
uv run calculator/main.py "3 + 7 * 2"
```

## Guidelines

- keep tool permissions narrowly scoped
- never commit credentials
- prefer small, testable changes
- preserve the assistant/tool message ordering required by the agent loop
- document new tools and user-facing features
