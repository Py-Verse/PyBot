![Python-Versions](https://img.shields.io/badge/python-3.8.7-blue?style=flat-square)
![Discord.py-Version](https://img.shields.io/badge/discord.py-1.6.0-blue?style=flat-square)
# PyBot
PyBot - A Bot for PyVerse Server which is now open source for it's community!

## About
[PyVerse](https://discord.gg/M89SmYyfcD) is a discord server for developers and PyBot is our personal discord bot!

#### Sample layout of `.env` file
```bash
TOKEN=token_here
logs = url_here
mongo = url_here
```

# Contributing Guidelines

## These are few needed things for contributing to Leafy

You should use pre-commit.

```bash
python3 -m pip install pre-commit  # required only once
pre-commit install
```

That's it! The plugin will run every time you commit any changes. If there are any errors found during the run, fix them and commit those changes. You can even run the plugin manually on all files:

```bash
pre-commit run --all-files --show-diff-on-failure
```
* Note - Use `.env` or `.venv` instead of `env` or `venv` ( virtual environments ). It is to prevent pre-commit from scanning them. Pre-commit is must , to prevent github actions

Also, great thanks to [python discord bot](https://github.com/python-discord/bot)! PyBot uses some of their's code

disco