import pexpect
# from openai.agents import tool

client = OpenAI()

# Spawn Python REPL once using pexpect
python_proc = pexpect.spawn("/usr/bin/python3", encoding="utf-8", timeout=5)
python_proc.expect(">>>")  # Wait for initial prompt

# @tool
def python_repl(code: str) -> str:
    """Send code to a persistent Python REPL (/usr/bin/python3) and return the output."""
    try:
        python_proc.sendline(code)
        python_proc.expect(">>>")  # Wait for next prompt
        output = python_proc.before.strip()
        return output
    except Exception as e:
        return f"[ERROR] {e}"

# Create the agent
agent = client.agents.create(
    name="PythonPexpectAgent",
    instructions="You are a Python expert who interacts with a running /usr/bin/python3 REPL via the python_repl tool.",
    tools=[python_repl]
)

# Run session
with client.agents.session(agent_id=agent.id) as session:
    # List files in home directory
    res1 = session.respond("List the contents of the home directory using python_repl.")
    print("Home listing:\n", res1.output_text)

    # Calculate total space used
    res2 = session.respond("Now calculate the total size in bytes of all files in the home directory using python_repl.")
    print("Disk usage:\n", res2.output_text)
