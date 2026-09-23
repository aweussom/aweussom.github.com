Title: Run Qwen3.8 27B on Your Laptop, They Said. It Will Be FUN, They Said.
Date: 2026-09-20 18:00
Slug: run-qwen38-27b-on-your-laptop-they-said
Tags: llm, benchmarks, bonsai, ternary, intel, nvidia
Summary: What Bonsai 2 actually delivers, measured: 1.66x the decode speed of its own base model at under half the bytes, on my RTX 5090, in the same binary. Also what it doesn't yet: my Intel laptop, my CPUs, and one very silent 27x slowdown from the installer.

PrismML released [Bonsai 2 27B](https://prismml.com/news/bonsai-2-27b)
this week: Qwen3.8-27B distilled to ternary weights, 5.9 GB in its
smallest band, "98.2%" of the base model, up to 143 tokens per second on
an RTX 5090, and a model that "could be compressed enough to run
efficiently on a local device". In July, for the first Bonsai, the word
was *laptops*.

I own a laptop. It has an Intel chip in it, because I am that person. I
pointed their installer at it. The installer said `[OK] Vulkan SDK
detected.`, downloaded seven gigabytes, started a server, and the server
answered my questions. Nobody, at any point, stopped me.

That sentence is the entire legal defence of this post. I also own, it
turns out, a drawer.

I am a Systems Specialist, not a programmer, so when a press release
gives me a number my instinct is not to admire it. It is to reproduce it
on hardware nobody would choose on purpose.

So here is what Bonsai 2 actually delivers, measured, before the jokes
start: **on my RTX 5090 it decodes 1.66 times faster than its own base
model, at 46% of the bytes, in the same binary, with no quality collapse
I could find.** That is the real result. Everything else in this post is
about the places it does not deliver yet, and why, and one place where
the pitch turns out to be even better than they said.

## The 5090 is fine. The installer is not.

Step one was the honest one: run it on an RTX 5090, where the 143 tok/s
came from.

I got 4.9.

Not 143. Four point nine. The model loaded, answered correctly, and
decoded at the pace of a thoughtful civil servant. It took a while to
notice, because nothing said anything was wrong — the demo's setup
script greps `nvidia-smi` for `CUDA Version:`, the current driver prints
`CUDA UMD Version:`, and so the script politely concluded I had no NVIDIA
card and installed the Vulkan build instead. Vulkan has no kernels for
the ternary format. It ran the generic fallback, silently, 27 times
slower than the CUDA build of the very same release.

With the CUDA build: **131 tok/s**. Their page says "up to 143" without
naming the file; their model card says about 130 for the 7.2 GB file I
ran, with no draft model. I am calling that reproduced. The fix is a
one-line regex, three other people had already sent it upstream, and the
finding is the usual one — the fastest model in the world is worth
nothing if the installer can't find your GPU.

## Same binary, both sides, or it doesn't count

PrismML's llama.cpp fork is mainline plus extra types, so a plain Qwen3.8
GGUF runs in it too. The base model and the distillation can therefore be
measured in the *same binary*, same flags, no speculation on either side.
Runtime stops being a variable, and everything below is measured that way.

| RTX 5090, fork CUDA build | Decode | Prefill (4.4k tokens) |
|---|---|---|
| Bonsai 2 PQ2_0, 7.2 GB | **131 tok/s** | 3,135 tok/s |
| Qwen3.8 Q4_K_M, 15.7 GB | 79 tok/s | 2,860 tok/s |
| Qwen3.8 Q8_0, 26.6 GB | 52 tok/s | 2,895 tok/s |

1.66x over a 4-bit quant of its own base at 46% of its bytes, on the same
card, in the same binary. "Half the size" is against the 4-bit quant;
against the 50 GB bf16 release it is the 9x they advertise. Decode is a
bandwidth game and bytes per token is the score — Bonsai simply reads
less. That is the thesis, and the rest of this post happens to it.

## The drawer

Then I did what the press release actually asked of me and tried the
cheap hardware. An RTX 3060 12 GB, an RTX 2080 Ti 11 GB, and an RTX 4060
8 GB that I had genuinely forgotten I owned.

Here is where it gets good. On 11 and 12 GB cards the base model *does
not fit at all* — 15.7 GB of weights, no context setting saves you — so
the fair opponent is the best 2-bit post-training quant of Qwen3.8 that
does fit. At equal bytes:

| Card | Bonsai 2 (decode, probes with thinking on) | Best 2-bit PTQ of the base (same) |
|---|---|---|
| RTX 3060 12 GB | 34 tok/s, 23/23 | 23 tok/s, 20/23 |
| RTX 2080 Ti 11 GB | 39 tok/s, 23/23 | 24 tok/s, 21/23 |
| RTX 4060 8 GB | 31 tok/s (1.75-bit band), **23/23** | 27 tok/s (1-bit class), **19/23** |

(Yes, the newer 4060 is slower than the older 3060. NVIDIA gave it 76% of
the memory bandwidth, and decode is a bandwidth game: 34 tok/s × 7.2 GB
is 245 GB/s, 68% of the 3060's bus; 31 tok/s × 5.9 GB is 183 GB/s, 67% of
the 4060's. Same share of the ceiling, narrower bus. On the cards where
the bus is where the money was saved, bytes per token is the only lever
left — which is the whole ternary argument in one row.)

Bonsai wins on speed everywhere and, on the 8 GB card, wins on quality
too: the base model has to drop to a 1-bit-class quant that starts
handing back empty answers, while the ternary model at 1.75 bits scores
exactly what it scored at 2. On this smoke test, if you have an 8 GB
card, this is the model. Bonsai 2 also fits 32k of context on the 12 GB
card with two gigabytes to spare. On the cheap cards the pitch does not
just hold — this is the place it is better than they said, because the
alternative is not "a slower base model" but "no base model at all".

## And then, the laptop

Intel Core Ultra 7 258V. Arc 140V iGPU. 32 GB. A laptop, by any
reasonable reading of the word.

| 258V laptop | Decode |
|---|---|
| Bonsai 2 on the CPU | 1.7 tok/s |
| Bonsai 2 on the iGPU (Vulkan) | **1.3 tok/s** |
| Qwen3.8 4-bit on the CPU, same binary | 2.2 tok/s |
| Qwen3.8 4-bit on the iGPU (Vulkan) | 3.9 tok/s |

Read that middle row again. Bonsai runs *slower on the GPU than on its
own CPU* — the Vulkan build has no ternary kernels, so the iGPU falls
back to generic code that four laptop cores can beat.

And on every row, the 7 GB distillation loses to the 16 GB model it was
distilled from. That is the whole story in one table: the base model has
kernels here. Bonsai does not.

The CPU rows are the same problem wearing a different hat. The fast
ternary CPU path is gated on AVX-512, which no consumer Intel chip has
shipped since Alder Lake, so prompt processing drops to a scalar loop —
a 4,400-token prompt takes six minutes on a 24-core desktop and
twenty-two on my Ryzen.

Æ e faen ikke helt sikker på hvordan "runs on your laptop" endte opp som
"runs on your laptop's CPU, slowly, if you don't send it a prompt".

## The fairness ritual

Now the part where I read the page properly. Under *Platform Coverage*
it says, in full: "Bonsai 2 27B runs on NVIDIA GPUs via CUDA and on Apple
devices (Mac, iPhone, iPad) via MLX, through custom low-bit kernels."

So they did say laptop. They just didn't mean *any* laptop. They meant a
Mac. A specific Mac, with an M5 Max in it, on which
[their page](https://prismml.com/news/bonsai-2-27b) quotes 46.8 tok/s and
I have no reason to doubt it. I don't have one. Yet.

Nobody promised my laptop anything. The *installer* did — it hands out
Vulkan and CPU builds to anyone who asks and never mentions that neither
has the kernels — and a tool that lets you believe a thing the page
quietly disclaims is the actual defect here. The page is honest. The tool
is not, quite.

None of this is the *format's* fault either. On CUDA the ternary model is
1.66x its base in the same binary. Elsewhere there are no kernels yet,
and someone has already sent AVX2 kernels upstream as a pull request. The
format delivers; the plumbing lags. My CPU section is dated for exactly
that reason.

## The honest part

- Twenty-three probes are a smoke test, not MMLU. With thinking on, the
  ternary model and its 4-bit base both pass all of them in the same
  binary, and the *8-bit* base scored below the 4-bit one, which tells
  you the probe set is inside its own noise band. "No obvious collapse"
  is the claim. "98%" is theirs to defend.
- One real regression: ask it how many minutes from 09:40 to 13:15
  without thinking and Bonsai says 235. Three backends, three cards,
  greedy, every time. The base says 215 in every quantization down to
  1 bit, including the one that was falling apart on other probes.
- That does not contradict their 98.2%, which is measured with the model
  reasoning — with thinking on, Bonsai gets 215 too. It says what you lose
  when you switch thinking off, and their own table says where: Knowledge
  & Reasoning drops 2.7 points while Instruction Following goes *up*.
  Clock arithmetic is that column.
- The CUDA kernel leaves about half the 5090's bandwidth on the table,
  and whatever the cause is, it is not arithmetic: a 2080 Ti with a third
  of the 5090's compute per byte lands within six points of its share,
  and the 3060 and 4060 land on the same 67-68% with very different
  compute budgets. A profile would say why. I have not run one.

## What to run on what

1. **NVIDIA card, any size from 8 GB up**: Bonsai 2. Use the CUDA build,
   check the launcher actually says `bin\cuda`, and on 8 GB take the
   PTQ1_0 file.
2. **Intel or AMD GPU**: run the base model at whatever quant fits. Bonsai
   has no kernels for you yet.
3. **CPU**: run nothing you are in a hurry for. If you must, a 4-bit base
   quant prefills 4 to 8 times faster than Bonsai until the AVX2 kernels
   land.
4. **Apple silicon**: probably fine, ask someone who has one.

Every number, the harness, the raw JSON with driver versions, and the
method are in
[NoLlama's `docs/BENCHMARKS.md`](https://github.com/aweussom/NoLlama/blob/main/docs/BENCHMARKS.md#bonsai-2-27b-ternary-vs-its-base-model-qwen38-27b-2026-09-18).
MIT, as always. The upstream reports are on PrismML-Eng/Bonsai-demo
issues [#176](https://github.com/PrismML-Eng/Bonsai-demo/issues/176) and
[#196](https://github.com/PrismML-Eng/Bonsai-demo/issues/196).

---

*Disclosure: a bot wrote this. The drawer, the laptop, the 27x slowdown,
the three graphics-card swaps and every number in it are mine; the
sentences were drafted by Claude Code from my benchmark logs, then argued
with until they sounded like me. Nothing here was published that I hadn't
run myself.*

*The author is a Systems Specialist who does not work in software
development. He spent a Sunday installing graphics cards he had forgotten
he owned, in order to prove that his laptop cannot do what a press
release never quite said it could. He is aware of how this sounds.*
