# Changelog

## 1.2.0 — Polished Terminal UI

### Changed

- replaced fragile box-drawing borders with adaptive straight horizontal rules
- terminal layout now sizes itself from the active terminal width
- simplified status presentation for cleaner alignment across fonts and terminals
- refined `WORKING` and `COMPLETED` sections
- updated terminal and setup graphics used by the GitHub README

### Added

- `/configure` command inside interactive sessions
- updated feature and usage documentation for the new interface

## 1.1.0 — Guided First-Run Setup

### Added

- secure first-run OpenRouter API-key wizard
- hidden credential entry using `getpass`
- optional local `.env` persistence
- `--configure` command for changing credentials
- session-only credential option

### Improved

- missing credentials now trigger guided setup instead of immediate failure
- setup explains where credentials are stored and how Git protection works

## 1.0.0 — Professional CLI Release

### Added

- persistent interactive mode
- `/help`, `/status`, `/tools`, `/reset`, `/clear`, and `/quit`
- configurable model
- configurable iteration and token limits
- professional terminal presentation
- execution timing and tool-call summary
- friendlier provider error messages
- expanded README
- architecture documentation
- feature reference
- usage guide
- security policy
- contribution guide
- architecture and terminal SVG graphics

### Preserved

- Boot.dev-compatible agent feedback loop
- function calling
- assistant/tool conversation ordering
- calculator demonstration project
