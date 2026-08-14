# Security Policy

## Credentials

Never commit API keys or other credentials.

Store the OpenRouter key only in your local `.env` file:

```text
OPENROUTER_API_KEY=your_key_here
```

`.env` is intentionally ignored by Git.

## Agent Permissions

This project gives an LLM controlled access to filesystem and Python
execution tools.

Only run the agent in directories containing files you are comfortable
allowing it to inspect or modify.

Do not expose:

- password stores
- SSH keys
- cloud credentials
- production configuration
- browser profiles
- personal documents
- unrestricted system directories

## Reporting

If you discover a security issue, avoid publishing credentials or exploit
details in a public issue. Revoke any exposed credential immediately.
