# MultiAgent-Writer

A multi-agent AI tool for academic proofreading and text improvement. Uses orchestrated LLM pipelines to analyze and refine academic writing, presenting corrections in a diff-style interface with granular accept/reject controls.

## How It Works

The tool orchestrates multiple LLM agents in sequence, each with a specialized role:

**Proofreading Pipeline** (2 agents):
1. **Analyst** (Claude Opus) — Identifies errors in grammar, style, terminology, and argumentation
2. **Editor** (GPT) — Applies targeted corrections based on the analysis

**Drafting Pipeline** (3 agents):
1. **Writer** (Kimi K2) — Expands bullet points into fully formed academic prose
2. **Analyst** (Claude Opus) — Reviews the draft for accuracy and style
3. **Editor** (GPT) — Incorporates all feedback into a polished final version

The key idea: separating analysis from editing produces better results than asking a single model to do both. The analyst's structured critique gives the editor concrete, actionable instructions.

## Features

- **Diff view** — Color-coded inline diffs (added/removed/changed) so you see exactly what was modified
- **Granular review** — Accept or reject individual changes, not just all-or-nothing
- **Analysis panel** — Read the full analyst critique (content, grammar, style, structure)
- **Configurable models** — Swap in any model available on OpenRouter
- **Cross-platform** — Desktop app (PyQt6), runs on Linux and Windows

## Tech Stack

- **Python 3.10+** with PyQt6
- **OpenRouter API** for model access (Claude, GPT, Kimi)
- Multi-agent orchestration with structured prompt templates
- Diff computation and selective patch application

## Quick Start

```bash
git clone https://github.com/marinusveit/MultiAgent-Writer.git
cd MultiAgent-Writer
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

Create a `.env` file with your OpenRouter API key:
```
OPENROUTER_API_KEY=sk-or-v1-your_key_here
```

Run:
```bash
multiagent-writer
```

## Project Structure

```
src/multiagent_writer/
├── main.py                # Entry point
├── api/                   # OpenRouter API client & service layer
├── core/                  # Text processing, diff computation
├── prompts/               # Structured prompt templates per agent role
├── config/                # Configuration management
└── ui/                    # PyQt6 desktop interface
```

## License

MIT
