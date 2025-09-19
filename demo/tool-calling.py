from pexpect.replwrap import REPLWrapper

# 1) Your executable tool
def run_repl(code: str, repl: REPLWrapper, timeout: float = 15.0) -> str:
    return repl.run_command(code + "\n", timeout=timeout).rstrip()

# 2) Tool schema (one function tool)
tool_def = {
    "type": "function",
    "function": {
        "name": "run_repl",
        "description": "Execute Python code in a live REPL and return stdout/stderr text.",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Complete Python snippet to run"}
            },
            "required": ["code"]
        }
    }
}

# 3) Controller loop (pseudo; fill in your model client)
def tool_loop(model_client, system_prompt: str, user_prompt: str):
    repl = REPLWrapper("python3 -q", prompt_regex=r">>> ", continuation_prompt_regex=r"\.\.\. ")
    messages = [{"role":"system","content": system_prompt}, {"role":"user","content": user_prompt}]
    tools = [tool_def]

    while True:
        # Ask the model what to do next (may return tool call(s) or a final message)
        resp = model_client.create_response(messages=messages, tools=tools, tool_choice="auto")
        # PSEUDOCODE: inspect resp to see if there is a tool call
        call = resp.first_tool_call_or_none()

        if call is None:
            # No tool call -> model is done
            print(resp.text())
            break

        if call.name == "run_repl":
            out = run_repl(call.args["code"], repl)
            # Return the tool result to the model, then continue
            messages.append({"role":"assistant","tool_calls":[{"id":call.id,"name":"run_repl","args":call.args}]})
            messages.append({"role":"tool","tool_call_id":call.id,"content": out})
            continue
