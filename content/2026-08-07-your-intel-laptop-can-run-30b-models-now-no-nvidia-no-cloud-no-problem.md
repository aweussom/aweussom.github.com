Title: Your Intel Laptop Can Run 30B Models Now. No NVIDIA. No Cloud. No Problem.
Date: 2026-08-07 12:00
Slug: your-intel-laptop-can-run-30b-models-now-no-nvidia-no-cloud-no-problem
Tags: llm, openvino, python, moe
Summary: OpenVINO 2026.3 quietly made 30B-class models interactive on Intel laptops — and a 74 GB model run on a 64 GB desktop. Two days of measuring, four benchmark lies, and one line of source code that explains everything.

In April I wrote that your Intel laptop can run LLMs. That post was about 8B models — good little assistants, honest about their limits, the kind of model that answers your question and doesn't architect your microservices.

This post is about running a 30B model on the same laptop. Interactively. And then, because being from Northern Norway means being apparently incapable of leaving a thing alone, about running a 74 GB model on a desktop with 64 GB of RAM.

That last sentence is not a typo. Hold it. It is the entire plot.

## The trick is that big models stopped being big

The new generation of local models are Mixture-of-Experts: Qwen3-30B-A3B has 30 billion parameters, but only 3 billion *activate* for any given token. The other 27 billion sit there being knowledge — consulted occasionally, like a reference library, not read cover to cover for every word.

This changes the economics completely. Decoding speed on consumer hardware is a memory-bandwidth game, and an A3B model only moves the *active* experts through memory per token. You pay small-model speed for big-model knowledge.

OpenVINO 2026.3 shipped the plumbing to exploit this on Intel hardware, and the release notes were their usual understated selves about it. We spent two days measuring what they actually delivered, across a Lunar Lake laptop (Arc 140V iGPU + NPU), a desktop Core Ultra 9 285K, and — for perspective — an RTX 5090.

Some of it is genuinely impressive. Some of it is a silent no-op unless your GPU has one specific hardware feature nobody documented. Both halves are below, with numbers.

## Part one: the NPU still needs a secret handshake

First, housekeeping from the smaller end. OpenVINO 2026.3 added NPU support for the new small models — SmolLM3-3B, LFM2, LFM2.5. This is true. What the release notes don't say is that if you convert these models yourself with the obvious command, the NPU driver compiler crashes:

```
[vpux-compiler] StopLocationVerifierPass Pass failed :
Found 364 duplicated names after full verification
```

That is not your fault. It is a known compiler bug with group-quantized INT4, and the fix is to quantize channel-wise instead:

```powershell
optimum-cli export openvino --model HuggingFaceTB/SmolLM3-3B \
  --weight-format int4 --group-size -1 --sym --ratio 1.0 <output>
```

NoLlama's `download-model.ps1` now has this as `-Weight int4-cw`, so you don't have to remember it. And because nobody had published OpenVINO builds of these models at all, we did — they're on HuggingFace with measured numbers in the cards:

| Model | NPU decode (285K) | Link |
|---|---|---|
| SmolLM3-3B int4-cw | 23.3 tok/s | [aweussom/SmolLM3-3B-int4-cw-ov](https://huggingface.co/aweussom/SmolLM3-3B-int4-cw-ov) |
| SmolLM3-3B int8-cw | 12.3 tok/s | [aweussom/SmolLM3-3B-int8-cw-ov](https://huggingface.co/aweussom/SmolLM3-3B-int8-cw-ov) |
| LFM2.5-1.2B int4-cw | 38.8 tok/s | [aweussom/LFM2.5-1.2B-Instruct-int4-cw-ov](https://huggingface.co/aweussom/LFM2.5-1.2B-Instruct-int4-cw-ov) |
| LFM2-1.2B int4-cw | 36.5 tok/s | [aweussom/LFM2-1.2B-int4-cw-ov](https://huggingface.co/aweussom/LFM2-1.2B-int4-cw-ov) |

Do not try int8 on the LFM models. Symmetric int8 compiles and runs fast and produces `BY-AL-AN-AN-AN-AN` forever. Asymmetric int8 produces correct English at 1.4 tokens per second. We measured both so you never have to.

## Part two: the disk offload feature, and the hardware gate nobody mentions

The headline 2026.3 feature: MoE expert weights can now be streamed from disk instead of held in GPU memory. `OFFLOAD_RATIO=50` means half your experts live on SSD and get fetched through an LRU cache. The release notes say this lets "30B MoE models like Qwen3-30B-A3B run even on devices with 16 GB of memory."

We spent a full day failing to make this do anything on a desktop iGPU. Every ratio, every model, every export vintage. Identical memory usage, identical speed, no warning, no log line, nothing.

The answer was one line in the OpenVINO source:

```cpp
// Gated on supports_immad (systolic-only) and oneDNN
if (device_info.supports_immad && config.get_use_onednn() && ...)
```

The entire MoE offload path requires **XMX** — the systolic matrix hardware in Arc GPUs, Lunar Lake, and newer. Desktop Arrow Lake and Meteor Lake iGPUs don't have it, and on those the feature is a *silent* no-op. Not "slow". Not "unsupported, error". Silent.

Check your own machine in one line:

```python
import openvino as ov
print(ov.Core().get_property("GPU", "OPTIMIZATION_CAPABILITIES"))
# GPU_HW_MATMUL in the list = you're in business
```

NoLlama's installer now prints this verdict at device detection, and the server warns at startup if you ask for offload on a GPU that will ignore you. Nobody should size their model plans around a feature their silicon doesn't have.

## Part three: on the right hardware, it actually works

On the Arc 140V laptop (which has XMX), the same feature that no-ops on the desktop delivers exactly what Intel promised. Qwen3-30B-A3B INT4 — a 15.2 GB model on a GPU with an 18 GB memory budget:

| `--offload-ratio` | Resident GPU memory | Steady-state decode |
|---|---|---|
| 30 | 10.8 GB | **25.3 tok/s** |
| 50 | 8.1 GB | 22.1 tok/s |
| 90 | 2.35 GB | 5.1 tok/s |

Twenty-five tokens per second is interactive. It matches a 24-core desktop CPU running the same model fully resident. From a thin laptop's iGPU, on a model that doesn't fit resident at all.

At ratio 90 the model runs in 2.35 GB of GPU memory. That's not a typo either — 15.2 GB of weights, 2.35 GB resident, the rest streaming from SSD on demand. It costs you speed (5 tok/s is ask-and-fetch-coffee territory), but the smallest ratio that fits your memory is the right setting, and at moderate ratios there's surprisingly little pain.

In NoLlama this is one flag, and it composes with prefix caching:

```powershell
python nollama.py --model-dir ~\models\Qwen3-30B-A3B-int4-ov --device GPU --offload-ratio 30
```

## Part four: the 74 GB model and the 64 GB computer

Here is where proportion left the building.

A GitHub issue collaborator — Dmitriy Teteruk, who deserves to be named because he ground through a conversion that required a **400 GB Windows pagefile** and then published the result — uploaded the first OpenVINO build of Qwen3-Coder-Next in existence: 74.4 GB of INT8 weights. ([It's on HuggingFace.](https://huggingface.co/dmitriyteteruk/Qwen3-Coder-Next-int8-ov))

My desktop has 64 GB of RAM. The model does not fit. We ran it anyway:

```
load:          ~80 s
steady-state:  8.8–11.5 tok/s   (cold vs warm OS page cache)
resident RAM:  stabilizes around 35 GB
```

No flags. No configuration. No offload feature. It just works, and the reason is the same MoE arithmetic as before: 10 of 512 experts activate per token, the hot experts stay in RAM, the cold ones sleep on disk, and the operating system's page cache turns out to be a perfectly serviceable LRU. The offload feature you need is called "an OS", and you already have it.

Æ e faen ikke helt sikker på hvordan vi havna her.

**Update, two days later:** the circle closed. Dmitriy pointed out — correctly,
with a screenshot — that his model is 80 billion parameters, and asked why the
title says 30B. Then he ran his own 74 GB upload on his own *laptop* and posted
the logs:

| Route | RAM committed | Steady-state |
|---|---|---|
| Everything GPU-resident (`--offload-ratio 0`) | 74 GB | **21.3 tok/s** |
| `--offload-ratio 30` | ~53 GB | 3.7 tok/s |
| `--offload-ratio 60` | ~31 GB | 3.7 tok/s |

An 80B coding model at 21 tokens per second, on a laptop, no NVIDIA in sight.
Load time with offload: 16 seconds, down from 145.

So why is the title still 30B? Because his laptop is not your laptop. It's a
ThinkPad he built out to **128 GB of RAM**, with Intel's shared-GPU-memory
override cranked to 110 GB — socketed memory, deliberately maxed. A Lunar Lake
laptop like mine is capped at 32 GB forever; the RAM is soldered *inside the CPU
package*. 30B is what the Intel laptop you probably own can do. 80B is what an
Intel laptop can be *built* to do. Both sentences are true, and the second one
has Dmitriy's name on it.

His logs also broke my own sizing rule, which is why they're worth a table:
ratio 30 and 60 decode at the *same* speed on his machine. With a model this
much bigger than the GPU's own budget, the retained experts land in host RAM
anyway — so the ratio decides how much RAM gets pinned, not how fast you go,
and the *highest* ratio wins. The exact opposite of the "smallest ratio that
fits" rule from part three, which still holds when the retained experts are
device-resident, like on my 140V. Hardware decides which rule applies.
Measure yours; `scripts/offload-test.py` prints the memory lines that tell
you which world you're in.

## Where does your hardware land?

Same model family, best route per hardware class, steady-state decode. Mixed quantizations and sizes — read it as routes, not a controlled A/B:

| Hardware | Route | Model | tok/s |
|---|---|---|---|
| RTX 5090 32 GB + CPU | Ollama, hybrid auto-split | Coder-Next Q4 (53 GB) | **~73** |
| Arc 140V laptop, offload 30 | NoLlama / OpenVINO | 30B-A3B int4 | 25.3 |
| 24-core desktop CPU, fits in RAM | NoLlama / OpenVINO | 30B-A3B int4 | 23.7 |
| 24-core desktop CPU, **bigger than RAM** | NoLlama / OpenVINO | Coder-Next int8 (74 GB) | 9–11.5 |
| 8-core laptop CPU (LPDDR5X) | NoLlama / OpenVINO | 30B-A3B int4 | 9.1 |
| Non-XMX desktop iGPU | — | any big MoE | won't load |

The fairness ritual, because it's earned: the 5090 wins by 3× and Ollama's auto-split needed zero configuration to do it — llama.cpp's MoE handling is genuinely excellent engineering. If you have a big CUDA card, use it. The point of the Intel rows is different: every one of them is *usable*, they run on hardware you may already own, and two of them — the offload row and the bigger-than-RAM row — were not possible before this release and this model generation.

Also worth saying out loud: 73 tokens per second from a gaming GPU in Verdal is faster than the streaming rate I get from the frontier cloud services. For an 80B-class coding model. With no queue, no quota, and no per-token bill.

## Four ways my benchmarks lied to me in one week

Numbered maxims, learned the humbling way:

1. **The first generation pays the bills.** Offloaded GPU runs start with a cold expert cache; CPU runs fault weights in lazily. Single-shot benchmarks reported *half to a fifth* of real steady-state speed. Our original offload numbers were 2–5× too pessimistic, and we published them before noticing. Measure warm, report the median.
2. **Count the tokens you got, not the tokens you asked for.** A model that answers "Hello!" and stops at four tokens, divided by a 64-token budget assumption, reports 645 tok/s. That number made it to a terminal, looked glorious, and was fiction.
3. **Your neighbors are part of the benchmark.** An Ollama instance quietly loading 53 GB in the background evicts your page cache and changes your numbers by 25%. So does Windows Defender meeting a fresh model download.
4. **Page-cache temperature is a variable.** The same >RAM model ran 11.5 tok/s right after downloading (cache warm from the writes) and 8.8 tok/s after something else evicted it. Both numbers are true. Report the range.

NoLlama's `scripts/offload-test.py` bakes the first two lessons in — warm-up labeled separately, real token counts, median of post-warm-up runs. The other two are on you.

## The shortlist

If you just want models that work, measured on real hardware this week:

**NPU** (channel-wise builds only — see the secret handshake above):

1. **Qwen3-8B int4-cw** — the quality pick, proven since spring ([Intel's build](https://huggingface.co/OpenVINO/Qwen3-8B-int4-cw-ov))
2. **SmolLM3-3B int4-cw** — 23 tok/s, and the same file runs on GPU and CPU too ([ours](https://huggingface.co/aweussom/SmolLM3-3B-int4-cw-ov))
3. **LFM2.5-1.2B int4-cw** — 39 tok/s, the speed pick ([ours](https://huggingface.co/aweussom/LFM2.5-1.2B-Instruct-int4-cw-ov), NPU-only build)

**GPU** (Arc iGPU or discrete):

1. **Qwen3-30B-A3B int4** — the reason this post exists; add `--offload-ratio 30` on XMX if it doesn't fit ([Intel's build](https://huggingface.co/OpenVINO/Qwen3-30B-A3B-int4-ov))
2. **Qwen3-VL 8B int8** — vision that keeps OCR detail; our verified pairing with NPU chat ([Intel's build](https://huggingface.co/OpenVINO/Qwen3-VL-8B-Instruct-int8-ov))
3. **Qwen2.5-Coder 7B int4** — the tool-calling agent workhorse for VS Code Copilot / OpenClaw ([Intel's build](https://huggingface.co/OpenVINO/Qwen2.5-Coder-7B-Instruct-int4-ov))

**CPU** (strong desktops):

1. **Qwen3-30B-A3B int4** — 23.7 tok/s on a 24-core 285K, no tricks
2. **Qwen2.5-Coder 7B/14B** — agent duty; a strong CPU out-prefills a weak iGPU
3. **SmolLM3-3B int4-cw** — 37 tok/s when you want light and instant

Honesty clause for the CPU column: if your machine has *no* Intel accelerators at all, plain Ollama is also excellent there and has a bigger model menu — NoLlama's reason to exist is the NPU/GPU stack, and we've said so [since the first post](https://aweussom.github.io/your-intel-laptop-can-run-llms-right-now-no-nvidia-no-cloud-no-problem.html).

**Next on the bench:** Google just shipped [Gemma 4, encoder-free multimodal](https://dev.to/googleai/introducing-gemma-4-12b-a-unified-encoder-free-multimodal-model-3ge5?bb=263641). I trust Google roughly as far as I can throw Brin — a couple of meters, if my tomoe-nage lands right — but Gemma 3 4B earned its place on our verified list fair and square, and early reports say Gemma 4's int4 builds hit the *same* NPU compiler bug the channel-wise recipe fixes. So they'll get tested, properly, numbers and all. The models keep being better than the corporate weather around them.

**Update, six hours after publishing:** tested. Properly. Numbers and all.

| Gemma 4 | Device | Steady-state |
|---|---|---|
| 26B-A4B int4 (multimodal MoE) | Arc 140V laptop GPU, resident | **26.6 tok/s** |
| 26B-A4B int4 | 24-core desktop CPU | 21.0 tok/s |
| 26B-A4B int4, `--offload-ratio 30` | Arc 140V (frees ~4 GB for context) | ~12 tok/s and climbing |
| E4B int8 | Arc 140V GPU | 16.4 tok/s |
| E4B int8 | Desktop CPU / non-XMX iGPU | ~13 / 12.6 tok/s |
| E4B int8 | Any NPU we own | do not |

The good news is genuinely good: a 26B multimodal MoE runs *faster on the laptop's iGPU than on a 24-core desktop CPU*, answers questions about XKCD strips while 30% of its experts live on the SSD, and Intel had pre-converted builds ready at launch. The models are excellent.

The NPU verdict is a two-part tragedy we've filed under "measured so you don't have to": on the older desktop NPU, Gemma 4 generates multilingual token salad at 0.5 tok/s. On the newer laptop NPU it generates *perfectly coherent* answers — at 0.1 tok/s. Eight minutes per reply. Right answers, geological pace. Two separate bugs, both now documented with repro commands in the repo's TODONT.md, neither of them the models' fault.

Brin remains unthrown. The corporate weather forecast, however, stands.

## The honest part

- **Thinking models on slow devices are a UX disaster** by default: a 4B model burned three minutes reasoning about "sum 11 to 29" on the iGPU. NoLlama's web UI now defaults no-think ON, sends a firmer repetition penalty, and has a visible Stop button. If you serve slow devices, you need all three — and if you're hitting the API directly, you need to bring them yourself:

```python
import requests

r = requests.post("http://localhost:8000/v1/chat/completions", json={
    "model": "Qwen3-30B-A3B",
    # /no_think goes in the USER prompt — Qwen-family models ignore it
    # in the system message. Measured, not folklore.
    "messages": [{"role": "user", "content": "Sum the numbers 11 to 29. /no_think"}],
    "max_tokens": 512,          # a budget, not a wish. 16k on a slow iGPU is a trap.
    "repetition_penalty": 1.1,  # Ollama's default; breaks think-loops.
})
print(r.json()["choices"][0]["message"]["content"])

# The panic button — stops the active generation server-side:
# requests.post("http://localhost:8000/v1/cancel")
```

  NoLlama passes `repetition_penalty`, `frequency_penalty`, and `presence_penalty` through to the runtime (Ollama-API callers: `options.repeat_penalty`). Until recently it silently ignored all of them, so if you tried this before and nothing happened — that was us, it's fixed. One more honesty clause: `/no_think` is a Qwen-family switch. Other model families have their own incantation or none at all — we verified that the exact snippet above runs fine against a MiniCPM5, which accepted the penalties and then serenely thought anyway.
- **The LFM int8 situation** (fast garbage or correct-but-1.4-tok/s) means quality-versus-speed on NPU is model-specific. Test per architecture; assume nothing.
- **No XMX means no offload, full stop.** Your model must fit. The installer will tell you which side of the line you're on.
- The 74 GB-on-64 GB trick needs an MoE with strong expert locality. A dense 70B model will thrash and you will be sad.
- All numbers are from two specific machines, measured this week, with the methodology above. Your silicon, drivers, and thermal situation will vary.

## The condensed payoff

```powershell
git clone https://github.com/aweussom/NoLlama
cd NoLlama
.\install.ps1        # detects devices, tells you if you have XMX, offers models
.\start.ps1

# Big MoE on an XMX GPU that's short on memory:
python nollama.py --model-dir <model> --device GPU --offload-ratio 30

# Find out what a model actually does on YOUR hardware:
python scripts\offload-test.py 0  <model-dir> CPU
python scripts\offload-test.py 30 <model-dir> GPU

# Convert your own models for the NPU (the recipe that doesn't crash):
.\download-model.ps1 <hf-model> -Convert -Weight int4-cw
```

NoLlama is MIT-licensed, one Python file, and speaks OpenAI and Ollama APIs so your existing tools just point at localhost. The full war diary — including every dead end — lives in the repo's TODONT.md, which is where we keep the things we tried so you don't have to.

---

*The author is a Systems Specialist who does not work in software development. This week he ran a model bigger than his computer's memory, discovered his benchmarks had been lying to him four different ways, and read GPU driver source code to find out why a documented feature did nothing. The feature was fine. The documentation had simply not mentioned which hardware it was for. He is keeping the laptop, the desktop, and the grudge.*
