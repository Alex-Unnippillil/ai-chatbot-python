import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

from call_function import call_function, available_functions


def main():
    load_dotenv()

    if len(sys.argv) < 2:
        print("Usage: uv run main.py \"your prompt here\"")
        sys.exit(1)

    api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY")

    if not api_key:
        print("Error: API key not found")
        sys.exit(1)

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    user_prompt = sys.argv[1]

    messages = [
        {
            "role": "system",
            "content": (
                "You are a coding agent. Use the available tools to inspect files, "
                "read source code, run Python files, and make changes when needed. "
                "Continue using tools until the user's task is fully resolved. "
                "Do not guess about file contents; inspect them first."
            ),
        },
        {
            "role": "user",
            "content": user_prompt,
        },
    ]

    verbose = "--verbose" in sys.argv

    for _ in range(20):
        response = client.chat.completions.create(
            model="google/gemini-2.5-flash",
            messages=messages,
            tools=available_functions,
            max_completion_tokens=4096,
        )

        message = response.choices[0].message

        # Keep the assistant's complete turn, including tool calls
        messages.append(message)

        # No tool calls means the agent has finished
        if not message.tool_calls:
            print("Final response:")
            print(message.content)
            return

        # Execute every requested tool and feed each result back
        for tool_call in message.tool_calls:
            result_message = call_function(tool_call, verbose=True)
            messages.append(result_message)

    print("Error: maximum number of agent iterations reached.")
    sys.exit(1)


if __name__ == "__main__":
    main()
