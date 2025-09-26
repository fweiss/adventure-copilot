A copilot to assist in playing the command-line Collosal Caves Adventure game

## Background
Back in the early 1980's I first played Collosal Caves Adventure
on the company's time sharing system. In order to become adept
I took some large line printer sheets and mapped out the cave.
I had this idea to build a front end or wrapper for the command-line
game that could assist in mapping out the cave. I never followed up
until now. I wanted to see if the OpenAI Agent SDK could provide
the solution I had envisioned.

## Outline
an agent:
- takes inputs
- produces outputs

it can use:
- instructions
- tools
- guardrails
- hooks

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
