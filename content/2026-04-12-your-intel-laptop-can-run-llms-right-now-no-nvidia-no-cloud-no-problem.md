Title: Your Intel Laptop Can Run LLMs Right Now. No NVIDIA. No Cloud. No Problem.
Date: 2026-04-12 17:44
Slug: your-intel-laptop-can-run-llms-right-now-no-nvidia-no-cloud-no-problem
Tags: llm, openvino, python
Summary: Your Intel laptop has an NPU. It has probably had one for a while. Intel has been marketing it...
Original: https://dev.to/tommy_leonhardsen_81d1f4e/your-intel-laptop-can-run-llms-right-now-no-nvidia-no-cloud-no-problem-3ejo

Your Intel laptop has an NPU. It has probably had one for a while. Intel has been marketing it enthusiastically. You have been ignoring it politely.

Fair enough. Until recently, using it for anything involved reading OpenVINO documentation until your eyes bled, converting models by hand, and writing pipeline code that made you nostalgic for the simplicity of CUDA driver hell. The NPU existed. Using it was a different proposition.

That has changed. [NoLlama](https://github.com/aweussom/NoLlama) is a local LLM server that runs on the full Intel stack — NPU, ARC iGPU, ARC discrete GPU, and CPU — and speaks both the OpenAI and Ollama APIs. Any tool that normally talks to OpenAI or Ollama just works: point it at localhost and go. Automatic device detection, streaming, vision model support, and a built-in web UI. Two commands to install. Two commands to run.

```powershell
.\install.ps1
.\start.ps1
```

No NVIDIA required. No Ollama install. No llama.cpp. No sending your data anywhere.


![Image description]({static}/images/your-intel-laptop-can-run-llms-right-now-no-nvidia-no-cloud-no-problem/01.gif)

---

## The Full Intel Stack

"Full Intel stack" is not marketing language. It means every Intel device you might have:

| Device | What it does |
|---|---|
| **NPU** (AI Boost) | Text chat, streaming. Fast and efficient for <8B models. |
| **ARC iGPU** | Vision models, or larger LLMs. Shares system RAM, so bigger models fit — they just run slower.* |
| **ARC discrete** | Same as iGPU, but with dedicated VRAM — larger models run faster. |
| **CPU** | Fallback. Slower, but it works everywhere. |

*\* iGPU and NPU both use system memory. Model size is limited by your RAM, not by a fixed VRAM budget. A 14B model will load on an iGPU with 32 GB of system RAM — it'll just think longer per token than on a discrete card.*

NoLlama auto-detects what you have and picks the best device. If you have both an NPU and a GPU, it runs them simultaneously — text chat on the NPU, image analysis on the GPU:

```http
POST /v1/chat/completions
  "What is the capital of Norway?"        --> NPU  [streaming]
  [image + "What vehicle is this?"]       --> GPU  [VLM]
```

You don't need to configure this. You don't need to pick devices. You send a request and the right thing happens.

### Actual numbers

Benchmarked on a Core Ultra 7 258V laptop (5 runs, outliers discarded):

| Device | Model | "Say hello" | tok/s |
|---|---|---|---|
| **NPU** | Qwen3 8B INT4-CW | 11.7s | ~5.2 |
| **CPU** | Qwen3 8B INT4-CW | 8.1s | ~7.4 |
| **ARC iGPU** | Qwen2.5-VL 3B | 2.6s | *** |

CPU actually beats NPU on raw throughput for this model — NPU wins on power efficiency, not speed. The ARC iGPU is running a smaller 3B VLM so not directly comparable, but subtracting prompt overhead, GPU generation is roughly 3x faster than NPU on this hardware. Image analysis (two photos, "are these the same vehicle?") takes ~3.8s regardless of answer length.

*\*\*\* VLMPipeline doesn't support streaming, so per-token speed can't be measured directly. Based on output length and total time, we estimate roughly 15-20 tok/s on ARC iGPU — but don't quote us on that. We're quoting ourselves and we're not sure we trust us.*





---

## Why Local?

I'll keep this short, because the full version involves a VPN that behaves like a bouncer who has lost the guest list, a proxy server with undocumented opinions, and the kind of data processing paperwork that makes the original technical problem feel nostalgic.

The short version: I work with GDPR-sensitive data. Sending it to cloud AI services requires security reviews and agreements that take longer than building the alternative. I want to be clear: **the security people are completely right.** The data I touch on a normal Tuesday could genuinely cause harm if it leaks. The straightjacket is load-bearing.

But a local model — running on-site, inside the network perimeter, no data leaving — is not a workaround. It is the correct architecture.

If you handle medical records, legal documents, financial data, or anything where "we sent it to an API" is not an acceptable answer during an audit, this is your architecture too.

---

## The Install Experience

`install.ps1` detects your hardware, shows a menu of models verified to work on Intel devices, downloads what you pick, and generates `start.ps1`. The launcher waits for the model to load (with a progress indicator), then opens the chat UI in your browser.

Every model in the menu is pre-exported for OpenVINO. No conversion step. No "please install optimum-intel and wait 45 minutes." Download, load, go.**

### NPU models (chat)

| Model | Size | Notes |
|---|---|---|
| Qwen3 8B (INT4-CW) | ~5 GB | **Recommended.** Best quality for NPU. |
| Phi 3.5 Mini (INT4-CW) | ~2 GB | Smaller, faster. |
| Mistral 7B v0.3 (INT4-CW) | ~4 GB | General purpose. Reliable. |
| DeepSeek R1 Distill 7B (INT4-CW) | ~4 GB | Reasoning specialist. |

### GPU vision models

| Model | Size | Notes |
|---|---|---|
| Gemma 3 4B Vision (INT4) | ~3 GB | Fast, good quality. |
| Gemma 3 12B Vision (INT4) | ~7 GB | Excellent quality. |
| Qwen2.5-VL 7B (INT4) | ~5 GB | Proven architecture. |

### GPU large LLMs (bigger brain, slower mouth)

| Model | Size | Notes |
|---|---|---|
| Qwen3 14B (INT4) | ~8 GB | Great reasoning. Sweet spot for ARC. |
| Phi 4 (INT4) | ~8 GB | Strong reasoning. |
| Qwen3 30B-A3B MoE (INT4) | ~17 GB | 30B brain, 3B speed. Needs beefy RAM. |

---

## Drop-in Replacement: OpenAI + Ollama APIs

This is the part that makes NoLlama actually useful beyond a tech demo. It speaks both the **OpenAI API** and the **Ollama API**, which means your existing tools don't know the difference. They think they're talking to a remote service. They're not. Everything stays on your machine.

Concretely, this works out of the box with:

- **Open WebUI** — connect via OpenAI mode (`http://localhost:8000/v1`) or Ollama mode (`http://localhost:11434`). No config changes beyond the URL.
- **The `openai` Python package** — point `base_url` at localhost, done.
- **Any Ollama client** — NoLlama serves on port 11434 (the Ollama default), so most clients find it automatically.
- **Anything else** that speaks either protocol — IDE plugins, CLI tools, custom scripts.

```python
from openai import OpenAI
client = OpenAI(base_url="http://localhost:8000/v1", api_key="unused")
resp = client.chat.completions.create(
    model="qwen3-8b",
    messages=[{"role": "user", "content": "Hello!"}],
    stream=True,
)
for chunk in resp:
    print(chunk.choices[0].delta.content or "", end="")
```

NoLlama pretends to be both services simultaneously, which is the kind of thing that should feel dishonest but actually just feels convenient. The Ollama clients think they're talking to Ollama. We don't correct them.

---

## The Web UI

The server includes a built-in chat interface. No separate install, no Docker, no Node.js.

Dark theme, streaming tokens, drag-and-drop images, model selector, device badge on every response (`[NPU 1.2s]`, `[GPU 2.8s]`). Qwen3's thinking models like to philosophise at length before answering, so the UI collapses `<think>` blocks into a tidy summary.

There is also a button labelled **"Just answer me, dammit!"** which cancels the current generation mid-stream. This now actually works — the generation runs in its own thread and checks for the cancel signal on every token. In the first version, the button was primarily motivational. I kept the name anyway.

---

## The Norway Incident

During initial testing with DeepSeek R1 1.5B — the smallest model in the list — I asked:

> **"What is the capital of Norway?"**

The model's response:

> *"I need to figure out the capital of Norway. I know it's a country in Norway. I remember that Norway is a small island..."*

Norway is not a small island. Norway is, among other things, a peninsula attached to Sweden, which is attached to Finland, which is attached to Russia, and so on. It is geographically quite attached to things.

Or *is* it? To paraphrase the greatest detective of all time, Ford Fairlane: "...an island in an ocean of diarrhea."

The lesson: 1.5B models are for testing whether the plumbing works. They are not for geography, geopolitics, or any domain where being wrong has consequences beyond entertainment. Use Qwen3-8B or larger for actual work. The small models are getting smarter every month. In the meantime, at least we know the pipes work — even if the water coming through them is, occasionally, nonsense.

---

## How I Built It

I'm a Systems Specialist, not a programmer. I've argued before that [code was always the easy part](https://dev.to/tommy_leonhardsen_81d1f4e/code-was-always-the-easy-part-5eaa) — the hard work happens before anyone touches a keyboard. Architecture, constraints, understanding what data you're allowed to touch and why.

Claude Code handled the part I was bad at — the boilerplate, the frontend JavaScript, the framework documentation at 3am. I handled the part I was already doing — the system design, the device routing logic, the security constraints. The whole thing took about six hours.

The appropriate superhero analogy is Spider-Man. Not Clark Kent — Clark Kent was always Superman, just pretending. Spider-Man had no powers. He got bitten by something unexpected, and the combination of that bite with skills he already had produced something disproportionate.

Specifically, he should be called **Web Crawler Spider-Man**, because if Peter Parker had been named by a backend engineer it would have been accurate and also slightly worse.

---

## Try It

**GitHub:** [github.com/aweussom/NoLlama](https://github.com/aweussom/NoLlama)

MIT license. Any Intel hardware with an NPU, ARC GPU, or just a CPU. OpenVINO 2026.1+. Two PowerShell commands. No data leaves your machine. Your IT department will not receive any reports.

---

*The author is a Systems Specialist who does not work in software development. His laptop now runs LLMs on three different Intel devices simultaneously. He is not sure how this happened but he is keeping it.*

*\*\* If your model isn't in the curated list, NoLlama provides a script to automate the painful process of converting any HuggingFace model to OpenVINO format — installing optimum-intel, figuring out weight formats, waiting while praying nothing crashes. It is still conversion, which means it is still fundamentally an act of faith. But at least the script handles the swearing for you. The curated list exists because pre-exported models are faster to get running, not because they're the only option.*

*Developed and tested on an Intel Core Ultra 7 258V (NPU + ARC 140V iGPU, 32 GB RAM). Should work on any Intel Core Ultra with NPU, any system with an ARC discrete GPU (A770, B580, etc.), or — in a pinch — any Intel CPU.*
