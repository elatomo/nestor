<div align="center">
  <img src="https://raw.githubusercontent.com/elatomo/nestor/main/assets/logo.png" alt="Néstor logo" width="300">
</div>

# Néstor

Néstor is my personal AI assistant project. The core idea is simple: use a cheap
capable model (gpt-4o-mini) as a natural language interface to useful functions.

I mainly use it through my [Matrix bot](https://github.com/elatomo/nestor-matrix),
but the core library works standalone via CLI. Eventually I might swap the model
for something that runs locally.

You're welcome to use it as reference, fork it, or steal ideas for your own
experiments.

## Features

- 🕐 **Date/time**: Current time and date in any timezone
- 🔍 **Web search**: [DDGS](https://github.com/deedy5/ddgs) integration
- 🌤 **Weather**: Forecasts via [Open-Meteo](https://open-meteo.com)

More tools added as I need them.

## Quick Start

Requires Python 3.14 and [uv](https://github.com/astral-sh/uv).

```bash
# Clone the repository
git clone https://github.com/elatomo/nestor.git
cd nestor
uv sync
```

Copy `.env.example` to `.env` and add your OpenAI API key:

```bash
cp .env.example .env
```

Run a query:

```bash
# Your $0.0001 time check 🤡
uv run nestor ask "Hey Néstor, what time is it?"
```

## Development

```bash
make dev      # Install with dev dependencies
make check    # Run lints, types, tests
make shell    # Python REPL with project loaded
```

Run `make help` for all available commands.
