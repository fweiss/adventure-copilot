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

## Colosal Cave Adventure
brew install open-adventure

``/usr/local/cellar/open-adventure/1.20/bin/advent``

AppStore ain't so good.

the session doesn't support fully interactive applications directl

this does work: ``echo "n\nquit\ny\n" | ./advent``

## Issues
To run ``pexpect_pyshell.py``, need pre release agents as of Spet 2025.
Install ``pip install --upgrade --pre openai``

## Links and references
openAI agent tutorial
https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf

Collosal Cave Adventure - on the AppStore

https://openai.github.io/openai-agents-python/
