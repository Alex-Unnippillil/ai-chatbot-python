import argparse
from getpass import getpass
import os
from pathlib import Path
import sys
import time

from dotenv import load_dotenv
from openai import OpenAI

from call_function import available_functions, call_function


APP_NAME = "AI Coding Agent"
VERSION = "1.1.0"
DEFAULT_MODEL = "google/gemini-2.5-flash"
DEFAULT_MAX_ITERATIONS = 20
DEFAULT_MAX_TOKENS = 4096

SYSTEM_PROMPT = """
You are a professional autonomous coding agent.

Use the available tools to inspect, understand, modify, test, and explain
software projects. Inspect relevant files before changing them, make focused
changes, verify your work, and continue until the user's task is complete.
Never reveal or write API keys, passwords, tokens, private keys, credentials,
or environment-variable values into source files.
""".strip()


def colors_enabled() -> bool:
    return sys.stdout.isatty() and not os.getenv("NO_COLOR")


def style(text: str, code: str) -> str:
    if not colors_enabled():
        return text
    return f"\033[{code}m{text}\033[0m"


def cyan(text: str) -> str:
    return style(text, "36")


def green(text: str) -> str:
    return style(text, "32")


def yellow(text: str) -> str:
    return style(text, "33")


def red(text: str) -> str:
    return style(text, "31")


def bold(text: str) -> str:
    return style(text, "1")


def dim(text: str) -> str:
    return style(text, "2")


def success(text: str) -> None:
    print(green(f"✓ {text}"))


def warning(text: str) -> None:
    print(yellow(f"! {text}"))


def failure(text: str) -> None:
    print(red(f"✗ {text}"), file=sys.stderr)


def banner(model: str) -> None:
    print()
    print(cyan("╭────────────────────────────────────────────────────────╮"))
    print(cyan("│") + bold("                   AI CODING AGENT") + " " * 19 + cyan("│"))
    print(cyan("│") + "          Inspect • Modify • Test • Verify" + " " * 12 + cyan("│"))
    print(cyan("╰────────────────────────────────────────────────────────╯"))
    print()
    print(f"  {dim('Model')}     {model}")
    print(f"  {dim('Commands')}  /help  /status  /tools  /reset  /clear  /quit")
    print()


def load_runtime_config() -> None:
    load_dotenv()


def env_value(name: str, default: str) -> str:
    return os.getenv(name, default)


def save_api_key(api_key: str) -> None:
    """Save the API key to the local .env file without exposing it."""
    env_path = Path(".env")
    lines = []

    if env_path.exists():
        lines = env_path.read_text(encoding="utf-8").splitlines()

    updated = []
    found_key = False

    for line in lines:
        if line.startswith("OPENROUTER_API_KEY="):
            updated.append(f"OPENROUTER_API_KEY={api_key}")
            found_key = True
        else:
            updated.append(line)

    if not found_key:
        if updated and updated[-1].strip():
            updated.append("")
        updated.append(f"OPENROUTER_API_KEY={api_key}")

    defaults = {
        "AI_AGENT_MODEL": DEFAULT_MODEL,
        "AI_AGENT_MAX_ITERATIONS": str(DEFAULT_MAX_ITERATIONS),
        "AI_AGENT_MAX_TOKENS": str(DEFAULT_MAX_TOKENS),
        "OPENROUTER_BASE_URL": "https://openrouter.ai/api/v1",
    }

    existing_names = {
        line.split("=", 1)[0]
        for line in updated
        if "=" in line and not line.lstrip().startswith("#")
    }

    for name, value in defaults.items():
        if name not in existing_names:
            updated.append(f"{name}={value}")

    env_path.write_text("\n".join(updated).rstrip() + "\n", encoding="utf-8")

    try:
        env_path.chmod(0o600)
    except OSError:
        pass


def setup_wizard(force: bool = False) -> str:
    """Ask for an OpenRouter API key when none is configured."""
    load_runtime_config()
    current = os.getenv("OPENROUTER_API_KEY", "").strip()

    if current and current != "replace_with_your_own_key" and not force:
        return current

    if not sys.stdin.isatty():
        raise RuntimeError(
            "OPENROUTER_API_KEY is required. Set it in the environment or a local .env file."
        )

    print()
    print(cyan("╭────────────────────────────────────────────────────────╮"))
    print(cyan("│") + bold("                FIRST-TIME SETUP") + " " * 20 + cyan("│"))
    print(cyan("╰────────────────────────────────────────────────────────╯"))
    print()
    print("No OpenRouter API key is configured." if not current else "Update your OpenRouter API key.")
    print()
    print("The key is entered invisibly, so it will not appear on screen.")
    print("You can save it locally to .env, which is ignored by Git.")
    print()

    while True:
        api_key = getpass("OpenRouter API key: ").strip()
        if api_key and api_key != "replace_with_your_own_key":
            break
        warning("Enter a valid API key, not the example placeholder.")

    print()
    choice = input("Save this key locally for future sessions? [Y/n]: ").strip().lower()

    if choice not in {"n", "no"}:
        save_api_key(api_key)
        success("Configuration saved securely to .env.")
    else:
        success("Using the key for this session only.")

    os.environ["OPENROUTER_API_KEY"] = api_key
    print()
    return api_key


def create_client(force_configure: bool = False) -> OpenAI:
    load_runtime_config()
    api_key = setup_wizard(force=force_configure)

    return OpenAI(
        base_url=env_value("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        api_key=api_key,
    )


def new_history():
    return [{"role": "system", "content": SYSTEM_PROMPT}]


def friendly_api_error(exc: Exception) -> str:
    message = str(exc)

    if "401" in message or "Authentication" in message:
        return "Authentication failed. Run `uv run main.py --configure` and enter a valid OpenRouter key."
    if "402" in message or "credits" in message.lower():
        return "The provider rejected the request because of account credit or token-limit restrictions."
    if "404" in message or "No endpoints found" in message:
        return "The configured model is unavailable. Choose another model with --model."
    if "429" in message:
        return "The provider rate limit was reached. Wait briefly and try again."
    return f"Agent request failed: {message}"


def run_agent_turn(client, messages, prompt, model, verbose, max_iterations, max_tokens) -> bool:
    messages.append({"role": "user", "content": prompt})
    started = time.perf_counter()
    tool_count = 0

    print()
    print(cyan("◆ Working on request"))
    print(dim("─" * 58))

    for iteration in range(1, max_iterations + 1):
        if verbose:
            print(dim(f"  reasoning cycle {iteration}/{max_iterations}"))

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=available_functions,
            max_completion_tokens=max_tokens,
        )

        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            elapsed = time.perf_counter() - started
            print()
            print(green("◆ Completed"))
            print(dim("─" * 58))
            print(message.content or "(No response text returned.)")
            print(dim("─" * 58))
            print(dim(f"{tool_count} tool call(s) • {elapsed:.1f}s"))
            print()
            return True

        for tool_call in message.tool_calls:
            tool_count += 1
            name = tool_call.function.name
            print(cyan(f"  → Calling function: {name}"))
            result_message = call_function(tool_call, verbose=verbose)
            messages.append(result_message)

    failure(f"Stopped after {max_iterations} reasoning cycles without a final response.")
    return False


def tool_names():
    names = []
    for tool in available_functions:
        try:
            names.append(tool["function"]["name"])
        except (KeyError, TypeError):
            try:
                names.append(tool.function.name)
            except AttributeError:
                names.append(str(tool))
    return names


def show_help() -> None:
    print()
    print(bold("Commands"))
    print("  /help      Show help")
    print("  /status    Show session configuration")
    print("  /tools     List available tools")
    print("  /reset     Clear conversation history")
    print("  /clear     Clear the terminal")
    print("  /quit      Exit")
    print()
    print(bold("Examples"))
    print("  Explain how the calculator works")
    print("  Find the calculator bug, fix it, and run the tests")
    print("  Inspect this Python project and summarize its architecture")
    print()


def interactive_mode(client, model, verbose, max_iterations, max_tokens) -> int:
    banner(model)
    messages = new_history()

    while True:
        try:
            prompt = input(style("agent › ", "1;34")).strip()
        except (KeyboardInterrupt, EOFError):
            print()
            success("Session closed.")
            return 0

        if not prompt:
            continue

        command = prompt.lower()

        if command in {"/quit", "/exit", "quit", "exit"}:
            success("Session closed.")
            return 0
        if command == "/help":
            show_help()
            continue
        if command == "/status":
            print()
            print(f"  Model             {model}")
            print(f"  Max iterations    {max_iterations}")
            print(f"  Max output tokens {max_tokens}")
            print(f"  Conversation      {max(0, len(messages) - 1)} message(s)")
            print(f"  Tools             {len(available_functions)}")
            print()
            continue
        if command == "/tools":
            print()
            for name in tool_names():
                print(f"  • {name}")
            print()
            continue
        if command == "/reset":
            messages = new_history()
            success("Conversation history cleared.")
            continue
        if command == "/clear":
            os.system("cls" if os.name == "nt" else "clear")
            banner(model)
            continue

        try:
            run_agent_turn(client, messages, prompt, model, verbose, max_iterations, max_tokens)
        except Exception as exc:
            failure(friendly_api_error(exc))


def parse_args():
    parser = argparse.ArgumentParser(
        prog="ai-agent",
        description="Autonomous coding agent with filesystem, editing, and Python execution tools.",
    )
    parser.add_argument("prompt", nargs="*", help="Coding request. Leave blank for interactive mode.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed tool activity.")
    parser.add_argument("--model", default=None, help="Override the configured OpenRouter model.")
    parser.add_argument("--max-iterations", type=int, default=None, help="Maximum agent reasoning cycles.")
    parser.add_argument("--max-tokens", type=int, default=None, help="Maximum model output tokens.")
    parser.add_argument("--configure", action="store_true", help="Run the secure API-key setup wizard.")
    parser.add_argument("--version", action="version", version=f"{APP_NAME} {VERSION}")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    load_runtime_config()

    model = args.model or env_value("AI_AGENT_MODEL", DEFAULT_MODEL)
    max_iterations = args.max_iterations or int(env_value("AI_AGENT_MAX_ITERATIONS", str(DEFAULT_MAX_ITERATIONS)))
    max_tokens = args.max_tokens or int(env_value("AI_AGENT_MAX_TOKENS", str(DEFAULT_MAX_TOKENS)))

    if args.configure:
        try:
            setup_wizard(force=True)
            success("Setup complete. Run `uv run main.py` to start the agent.")
            return 0
        except (KeyboardInterrupt, EOFError):
            print()
            warning("Setup cancelled.")
            return 1

    try:
        client = create_client()
    except (RuntimeError, KeyboardInterrupt, EOFError) as exc:
        if isinstance(exc, RuntimeError):
            failure(str(exc))
        else:
            print()
            warning("Setup cancelled.")
        return 1

    prompt = " ".join(args.prompt).strip()

    if not prompt:
        return interactive_mode(client, model, args.verbose, max_iterations, max_tokens)

    messages = new_history()

    try:
        completed = run_agent_turn(
            client,
            messages,
            prompt,
            model,
            args.verbose,
            max_iterations,
            max_tokens,
        )
        return 0 if completed else 1
    except Exception as exc:
        failure(friendly_api_error(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
