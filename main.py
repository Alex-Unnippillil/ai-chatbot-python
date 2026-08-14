import argparse
import os
import sys
import time

from dotenv import load_dotenv
from openai import OpenAI

from call_function import available_functions, call_function


load_dotenv()

APP_NAME = "AI Coding Agent"
VERSION = "1.0.0"

DEFAULT_MODEL = os.getenv(
    "AI_AGENT_MODEL",
    "google/gemini-2.5-flash",
)

DEFAULT_MAX_ITERATIONS = int(
    os.getenv("AI_AGENT_MAX_ITERATIONS", "20")
)

DEFAULT_MAX_TOKENS = int(
    os.getenv("AI_AGENT_MAX_TOKENS", "4096")
)

SYSTEM_PROMPT = """
You are a professional autonomous coding agent.

Your purpose is to inspect, understand, modify, test, and explain
software projects using the tools available to you.

Operating rules:

1. Inspect relevant files before editing them.
2. Never invent file contents.
3. Prefer small, maintainable changes.
4. Use tools when filesystem or runtime information is required.
5. Test changes after modifying code.
6. If a test fails, investigate and continue.
7. Continue until the user's requested task is actually complete.
8. Never reveal API keys, passwords, tokens, private keys,
   environment-variable values, or credentials.
9. Never write secrets into project source code.
10. Summarize the work clearly when finished.

Prefer verification over assumption.
""".strip()


# ============================================================
# Terminal presentation
# ============================================================

def colors_enabled() -> bool:
    return (
        sys.stdout.isatty()
        and not os.getenv("NO_COLOR")
    )


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


def line() -> None:
    print(dim("─" * 58))


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


def success(text: str) -> None:
    print(green(f"✓ {text}"))


def info(text: str) -> None:
    print(cyan(text))


def warning(text: str) -> None:
    print(yellow(f"! {text}"))


def failure(text: str) -> None:
    print(red(f"✗ {text}"), file=sys.stderr)


# ============================================================
# Client
# ============================================================

def create_client() -> OpenAI:
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key or api_key == "replace_with_your_own_key":
        raise RuntimeError(
            "OpenRouter is not configured.\n\n"
            "Create or edit .env and add:\n"
            "OPENROUTER_API_KEY=your_actual_key"
        )

    return OpenAI(
        base_url=os.getenv(
            "OPENROUTER_BASE_URL",
            "https://openrouter.ai/api/v1",
        ),
        api_key=api_key,
    )


def new_history():
    return [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]


# ============================================================
# Error presentation
# ============================================================

def friendly_api_error(exc: Exception) -> str:
    message = str(exc)

    if "401" in message or "Authentication" in message:
        return (
            "Authentication failed. Check OPENROUTER_API_KEY "
            "in your local .env file."
        )

    if "402" in message or "credits" in message.lower():
        return (
            "The provider rejected the request because of account "
            "credit or token-limit restrictions."
        )

    if "404" in message or "No endpoints found" in message:
        return (
            "The configured model is currently unavailable. "
            "Choose another model with --model or AI_AGENT_MODEL."
        )

    if "429" in message:
        return (
            "The provider rate limit was reached. "
            "Wait briefly and try again."
        )

    return f"Agent request failed: {message}"


# ============================================================
# Agent loop
# ============================================================

def run_agent_turn(
    client,
    messages,
    prompt,
    model,
    verbose,
    max_iterations,
    max_tokens,
) -> bool:

    messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    started = time.perf_counter()
    tool_count = 0

    print()
    info("◆ Working on request")
    line()

    for iteration in range(1, max_iterations + 1):

        if verbose:
            print(
                dim(
                    f"  reasoning cycle "
                    f"{iteration}/{max_iterations}"
                )
            )

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=available_functions,
            max_completion_tokens=max_tokens,
        )

        message = response.choices[0].message

        # Critical agent-loop behavior:
        # preserve the assistant turn before tool results.
        messages.append(message)

        if not message.tool_calls:
            elapsed = time.perf_counter() - started

            print()
            print(green("◆ Completed"))
            line()
            print(message.content or "(No response text returned.)")
            line()
            print(
                dim(
                    f"{tool_count} tool call(s) • "
                    f"{elapsed:.1f}s"
                )
            )
            print()

            return True

        for tool_call in message.tool_calls:
            tool_count += 1
            name = tool_call.function.name

            # Preserve Boot.dev-friendly function-name output.
            info(f"  → Calling function: {name}")

            result_message = call_function(
                tool_call,
                verbose=verbose,
            )

            messages.append(result_message)

    failure(
        f"Stopped after {max_iterations} reasoning cycles "
        "without receiving a final response."
    )

    return False


# ============================================================
# Interactive commands
# ============================================================

def show_help() -> None:
    print()
    print(bold("Commands"))
    print()
    print("  /help      Show command help")
    print("  /status    Show current session configuration")
    print("  /tools     Show available coding tools")
    print("  /reset     Clear conversation history")
    print("  /clear     Clear the terminal")
    print("  /quit      Exit")
    print()
    print(bold("Example tasks"))
    print()
    print("  Explain how the calculator works")
    print("  Find the bug in the calculator and test the fix")
    print("  Inspect the Python project and summarize its architecture")
    print("  Run the calculator and investigate any errors")
    print()


def show_tools() -> None:
    print()
    print(bold("Available tools"))
    print()

    names = []

    for tool in available_functions:
        try:
            names.append(tool["function"]["name"])
        except (KeyError, TypeError):
            names.append(str(tool))

    for name in names:
        print(f"  • {name}")

    print()


def show_status(
    model: str,
    max_iterations: int,
    max_tokens: int,
    messages,
) -> None:

    print()
    print(bold("Session status"))
    print()
    print(f"  Model             {model}")
    print(f"  Max iterations    {max_iterations}")
    print(f"  Max output tokens {max_tokens}")
    print(f"  Conversation      {max(0, len(messages) - 1)} message(s)")
    print(f"  Tools             {len(available_functions)}")
    print()


def interactive_mode(
    client,
    model,
    verbose,
    max_iterations,
    max_tokens,
) -> int:

    banner(model)

    messages = new_history()

    while True:

        try:
            prompt = input(
                style("agent › ", "1;34")
            ).strip()

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
            show_status(
                model,
                max_iterations,
                max_tokens,
                messages,
            )
            continue

        if command == "/tools":
            show_tools()
            continue

        if command == "/reset":
            messages = new_history()
            success("Conversation history cleared.")
            continue

        if command == "/clear":
            os.system(
                "cls"
                if os.name == "nt"
                else "clear"
            )
            banner(model)
            continue

        try:
            run_agent_turn(
                client,
                messages,
                prompt,
                model,
                verbose,
                max_iterations,
                max_tokens,
            )

        except Exception as exc:
            failure(friendly_api_error(exc))


# ============================================================
# Command-line parsing
# ============================================================

def parse_args():
    parser = argparse.ArgumentParser(
        prog="ai-agent",
        description=(
            "Autonomous coding agent with filesystem, "
            "editing, and Python execution tools."
        ),
    )

    parser.add_argument(
        "prompt",
        nargs="*",
        help=(
            "Coding request. Leave blank to launch "
            "interactive mode."
        ),
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed tool execution information.",
    )

    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Model name (default: {DEFAULT_MODEL})",
    )

    parser.add_argument(
        "--max-iterations",
        type=int,
        default=DEFAULT_MAX_ITERATIONS,
        help=(
            "Maximum agent reasoning cycles "
            f"(default: {DEFAULT_MAX_ITERATIONS})"
        ),
    )

    parser.add_argument(
        "--max-tokens",
        type=int,
        default=DEFAULT_MAX_TOKENS,
        help=(
            "Maximum model output tokens "
            f"(default: {DEFAULT_MAX_TOKENS})"
        ),
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"{APP_NAME} {VERSION}",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        client = create_client()

    except RuntimeError as exc:
        failure(str(exc))
        return 1

    prompt = " ".join(args.prompt).strip()

    if not prompt:
        return interactive_mode(
            client,
            args.model,
            args.verbose,
            args.max_iterations,
            args.max_tokens,
        )

    messages = new_history()

    try:
        completed = run_agent_turn(
            client,
            messages,
            prompt,
            args.model,
            args.verbose,
            args.max_iterations,
            args.max_tokens,
        )

        return 0 if completed else 1

    except Exception as exc:
        failure(friendly_api_error(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
