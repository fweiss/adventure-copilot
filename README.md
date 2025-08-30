## Outline
an agent:
- takes inputs
- produces outputs

it can use:
- instructions
- tools
- guardrails
- hooks

## try it with cahtgpt5:
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

## Links and references
openAI agent tutorial
https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf
