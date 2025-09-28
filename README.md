A copilot to assist in playing the command-line Colossal Cave Adventure game
> You are standing at the end of a road before a small brick building.
> Around you is a forest.  A small stream flows out of the building and
> down a gully.

## Background
Back in the early 1980's I first played Colossal Cave Adventure
on the company's time sharing system. In order to become adept
I took some large line printer sheets and mapped out the cave.
I had this idea to build a front end or wrapper for the command-line
game that could assist in mapping out the cave. I never followed up
until now. I wanted to see if the OpenAI Agent SDK could provide
the solution I had envisioned.


## Project setup - Mac
Do the following before you run the app.

## Colossal Cave Adventure
There are many versions. The following was closest to the original one from the 1980's:
```
brew install open-adventure
```
The installation directory is:
``/usr/local/cellar/open-adventure/1.20/bin/advent``

> The version from the AppStore ain't so good.

### Python setup
This is a python project. Do the needful:
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### OpenAI API key
You will need to get an [API key](https://platform.openai.com/api-keys) and put it in the environment. The file ``key`` is gitignored for this purpose. Put the API key in the  file as follows,
```
export OPENAI_API_KEY=<your API key>
```
and then run ``source key`` in import it into your environment.

## Outline
an agent:
- takes inputs
- produces outputs

it can use:
- instructions
- tools
- guardrails
- hooks

## Links and references
openAI agent tutorial
https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf

Collosal Cave Adventure - on the AppStore

https://openai.github.io/openai-agents-python/
