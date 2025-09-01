# agent_runner.py
from openai import OpenAI
from game_tool import game_io

client = OpenAI()

# 1) Declare the tool schema for the model
tools = [
    {
        "type": "function",
        "name": "game",
        "function": {
            "name": "game_io",
            "description": "Send one command to the text adventure and get the resulting screen.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "A single game command like 'look', 'north', 'get lamp'."}
                },
                "required": ["command"]
            },
        },
    }
]

system_instructions = """You are an expert player of a text-based adventure.
Always reason briefly about the current scene, then choose exactly one next command.
Use the tool 'game_io' to send commands. The game prompt ends with '>'.
Prefer concise commands: 'look', 'inventory', compass directions, 'get X', 'open Y'.
After each observation, summarize state: location, exits, inventory, goals.
Stop if the game ends or if you're stuck and need human input.
"""

# 2) Start the session by reading the game's opening screen
opening = game_io("n")["output"] # skip instructions

messages = [
    {"role": "system", "content": system_instructions},
    {"role": "user", "content": f"You're connected to the game. Opening screen:\n\n{opening}\n\nPlay to reach the main goal."}
]

# 3) Response loop (tool calling)
for _ in range(50):  # cap steps
    resp = client.responses.create(
        model="gpt-5",              # or another tool-capable model
        input=messages,
        tools=tools,
        tool_choice="auto",         # let the model decide when to call game_io
        # temperature=0.2,          # unsupported parameter
    )

    msg = resp.output[0] if hasattr(resp, "output") else resp  # SDKs differ; adjust as needed

    # Handle tool calls (may be multiple)
    made_tool_call = False
    for item in getattr(msg, "content", []):
        if item.get("type") == "tool_use" and item["name"] == "game_io":
            made_tool_call = True
            cmd = item["input"]["command"]
            tool_result = game_io(cmd)

            # Append tool result back to the conversation
            messages.append({
                "role": "tool",
                "name": "game_io",
                "content": tool_result["output"]
            })

    # If the model didn’t call the tool, append its text and break
    if not made_tool_call:
        # show final reasoning / summary
        assistant_text = "".join(
            part.get("text", "") for part in getattr(msg, "content", []) if part.get("type") == "output_text"
        )
        print(assistant_text)
        break

    # Also append the assistant’s tool call message so the model can continue the chain
    messages.append({"role": "assistant", "content": msg.dict() if hasattr(msg, "dict") else str(msg)})
