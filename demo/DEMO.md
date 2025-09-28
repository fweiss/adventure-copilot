This directory has the initial attempts.

## try it with chatgpt5:
```
write a simple agent in python that creates bash shel as a subtask sends commands to it and reeives information from it
```
This was saved as ``simple.py``
now added:
```
using the openai agent sdk, sned the output of the llm to the subprocess and send the output of the subprocess to the llm
```
needs ``pip install --upgrade openai-agents``
needs ``export OPENAI_API_KEY="sk-..."``

> The prompt sent to the subshell is ``Create /tmp/agents_demo, cd there, make hello.txt with 'hi', then show its contents.``
> It does what is says!

the session doesn't support fully interactive applications directl

this does work: ``echo "n\nquit\ny\n" | ./advent``

## Issues
To run ``pexpect_pyshell.py``, need pre release agents as of Spet 2025.
Install ``pip install --upgrade --pre openai``
