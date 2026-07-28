Title: Destructive Reader LLM — When an Author Gets Tired of Reddit's Gatekeeping
Date: 2026-02-14 19:03
Slug: destructive-reader-llm-when-an-author-gets-tired-of-reddits-gatekeeping
Tags: devchallenge, githubchallenge, cli, githubcopilot
Summary: This is a submission for the GitHub Copilot CLI Challenge           What I Built   I'm a systems...
Original: https://dev.to/tommy_leonhardsen_81d1f4e/destructive-reader-llm-when-an-author-gets-tired-of-reddits-gatekeeping-2k9f

*This is a submission for the [GitHub Copilot CLI Challenge](https://dev.to/challenges/github-2026-01-21)*

## What I Built

I'm a systems administrator who dabbles in programming — and an author with two published novels. I'm working on my third book, and I needed honest, structured feedback on my chapters.

I found [r/DestructiveReaders](https://www.reddit.com/r/DestructiveReaders/), a Reddit community known for "brutal but loving" literary critique. The concept is exactly what I wanted: direct, specific feedback that doesn't sugarcoat problems but always offers solutions. The reality was different. The community requires extensive karma-building before you can receive a critique — other authors report spending days earning enough credit. And after all that effort, the critiques I read varied wildly in quality.

So I built my own.

**Destructive Reader LLM** is a Python CLI tool that takes a fiction chapter and delivers structured literary critique in the r/DestructiveReaders style. It uses NVidia Nemotron Nano 30B via [Ollama](https://ollama.com/) — a free cloud model — guided by a carefully crafted system prompt that captures the community's ethos: be brutal, be loving, be specific, always offer a fix.

The critique follows a consistent structure:

- **Opening Hook** — one thing that works, the biggest problem, overall take
- **The Big Issues** (2-3 max) — quoted from your text, explained, with concrete fixes
- **Reader Journey** — where the critic was hooked, lost, confused, or kept reading
- **Quick Fixes** — ranked actionable changes with before/after examples
- **What's Working** — genuine positives with quoted evidence

This isn't a toy project. I use it on my actual manuscript chapters. The critique below was generated from a chapter of my published novel in 15 seconds.

## Demo

**GitHub Repository:** [github.com/aweussom/DestructiveReader-LLM](https://github.com/aweussom/DestructiveReader-LLM)

Running the tool against a chapter from my published novel:
```
python destructive-reader-llm.py Markdown/01-AWAKENING.md
```

![Image description]({static}/images/destructive-reader-llm-when-an-author-gets-tired-of-reddits-gatekeeping/01.png)

The generated critique is saved as Markdown alongside the chapter file, ready to reference during revision.

## My Experience with GitHub Copilot CLI

I used GitHub Copilot CLI (v0.0.410, running on the free Claude Haiku 4.5 model) as my development partner for the entire build. The whole tool went from idea to working software in a single session.

### Step 1: Describe the project and test connectivity

I opened Copilot CLI and described what I needed — a test script to verify I could connect to Ollama cloud and the Nemotron model. Copilot CLI generated a working `test_ollama.py` on the first attempt. It worked after I corrected the model name from `nemotron-3-nano:latest` to `nemotron-3-nano:30b-cloud`.


![Image description]({static}/images/destructive-reader-llm-when-an-author-gets-tired-of-reddits-gatekeeping/02.png)

### Step 2: Build the main tool

I gave Copilot CLI a clear spec: read `INSTRUCTIONS.md`, accept a chapter filename as argument, build a combined prompt, send to Ollama, save the critique as `<chapter-name>-critique-<timestamp>.md`. Copilot CLI read my instructions file to understand the context, then generated the complete `destructive-reader-llm.py` — 145 lines covering argument parsing, file loading, prompt construction, API calls, and output saving. It worked on first run.

![Image description]({static}/images/destructive-reader-llm-when-an-author-gets-tired-of-reddits-gatekeeping/03.png)

### Step 3: Refine the output

The critique was truncated on console but saved correctly to disk. I asked Copilot CLI to print the full response, add timing, and display the output filename. Two targeted edits, done.

### Step 4: Evaluate the results

Here's where it got interesting. I asked Copilot CLI to read the original chapter, the instructions, and the generated critique — then tell me whether the Nemotron critique was any good and how it would compare to Claude Sonnet 4.5. Copilot CLI gave a thoughtful assessment: Nemotron nails the brutal-but-constructive voice but misses some thematic subtlety that a larger model would catch. Its recommendation — stick with Nemotron for the punchy r/DestructiveReaders style, consider a second model for deeper thematic analysis.

![Image description]({static}/images/destructive-reader-llm-when-an-author-gets-tired-of-reddits-gatekeeping/04.png)

### Overall impression

The free tier Haiku 4.5 model in Copilot CLI was more than capable for this kind of structured code generation. Copilot handled the boilerplate and let me focus on what actually matters — the critique prompt and the workflow design. From first prompt to working tool: one session, no debugging required beyond correcting a model name.
