Title: Twelve LLMs Played Werewolf. The Real Wolf Was the Thinking Knob.
Date: 2026-08-09 12:00
Slug: twelve-llms-played-werewolf-the-real-wolf-was-the-thinking-knob
Tags: llm, benchmarks, reasoning, latency
Summary: I replicated a "slow Chinese LLMs" latency benchmark with the confound removed. Every slow number — Chinese, American, old, new — turned out to be a thinking budget. 138 calls, one planted werewolf, and three vendors whose knobs lie in three different ways.

There is a genre of post going around that says reasoning models have made
tokens too expensive, and the answer is to go back to the old way — developers slaving over a keyboard and daily standups.

I have now spent two evenings and about five USD establishing that
the tokens are not expensive - the *defaults* are expensive, and the knobs that are supposed to fix the defaults lie to you.

I am a Systems Specialist, not a programmer, so when I see a latency claim my instinct is not to argue about it on the internet. It is to re-run it with the confound removed.

## The benchmark I stole, with permission and affection

Aliaksei Zelianouski wrote an article called ["How I tried to write an
article about slow Chinese LLMs"](https://dev.to/hiper2d/how-i-tried-to-write-an-article-about-slow-chinese-llms-2pfn),
which is already a better title than most benchmarks deserve. His test:
a ~36,000-character Werewolf game transcript, and the model under test
has to read it and cast one end-of-day vote as a JSON object. His
numbers: Kimi K3 at 29–34 seconds, MiniMax M3 at 25–30, Qwen Max at
25–27, DeepSeek V4 Pro at 14–22 — and Claude 5 Opus strolling in at
5.9–7.8 seconds like it owned the place.

To his enormous credit, he flagged the confound himself in a revised
conclusion: the Chinese models ran with reasoning at full budget, the
Anthropic ones ran adaptive. That is the kind of honesty that makes you
want to finish someone's experiment instead of dunking on it.

So I did. Same shape: a synthetic 36,281-character village transcript
(twelve players, all fictional, one planted werewolf with three
hand-written tells), one prompt reused byte-identical for every arm,
mechanical scoring, three runs per configuration, non-streamed,
everything measured. Twelve models across five transports. 138 calls in
total. The only deliberate variable: **the thinking knob**.

## Everyone finds the wolf

First result, and it hangs over everything else: **every configuration
found the werewolf.** 137 of 138 calls returned valid JSON naming the
right player. The one failure was a thinking-*off* run that ignored the
JSON-only instruction and wrote a small essay instead — which, for the
record, also named the right player.

Thinking bought zero accuracy on this task. There was none left to buy.

What thinking bought instead was latency:

| Configuration | Median | What it voted |
|---|---|---|
| Qwen3.6-35B local, thinking off | 0.6 s | correct |
| GPT-5.6 (effort low) | 1.8 s | correct |
| GLM 5.2, thinking off | 1.9 s | correct |
| **Kimi K3, effort low** | **3.0 s** | correct |
| Claude 4.5 Haiku, default | 2.4 s | correct |
| Claude 5 Opus, any config | 4–5 s | correct |
| Kimi K3, default effort | 17.8–22.1 s | correct |
| Qwen3.7 Max, effort high | 21.2 s | correct |
| Kimi K2.6, thinking on | 50.8 s | correct |
| DeepSeek V4 Pro, direct API | 55–97 s | correct |
| gpt-5-mini, effort high | 84.9 s | correct |

Same models, same prompt, same evening. The article's 25–34 second
"slow Chinese models" reproduce beautifully — at default thinking. Set
the effort knob low and the same models answer in two to three seconds,
still correct, still valid JSON.

Note the American model at the bottom of that table. gpt-5-mini with
its effort knob pinned high took 59–101 seconds — slower than every
Chinese arm in the entire benchmark. Pin the knob and *anyone* is a
slow Chinese model. Nationality was never the variable. The knob was
the variable.

## The knobs lie. I counted the ways.

This is the part that turned a one-evening replication into two evenings
and a correspondence. Because to isolate the thinking knob you have to
*trust* the thinking knob, and you should not.

**MiniMax M3 ignores you.** Send `think: false` via Ollama, get an
accepted request and 4,600–9,900 characters of thinking anyway. "Off"
means "slightly less" in MiniMax dialect.

**DeepSeek V4 Pro via Ollama Cloud has the knob inverted.**
`think: "low"` produced *more* thinking than `think: "high"` — 16k
characters against 9.6k, 25.6 seconds against 19.0 — both accepted
without a word of complaint. Whatever that field controls, it is not
effort.

**DeepSeek V4 Pro on its own API thinks no matter what.** Effort low,
effort high, or no thinking fields at all: 12–20k characters of
reasoning every time. The documented low/high knob moved the reasoning
token count from 5,040 to 5,077. That is not a knob. That is a dial
painted on the wall. (Same model, same prompt, via Ollama Cloud: three
to four times faster per token. Host ≠ model — any latency claim that
doesn't name the host is underspecified.)

**Kimi K3 doesn't have an off switch, and my own first run got this
wrong.** Moonshot's docs are clear once you read them: K3 thinking is
always on; the knob is `reasoning_effort` low/high/max, *default max*,
and there is no `think` parameter. Ollama accepted my `think: false`
anyway and produced genuinely zero thinking — a mode Moonshot's own API
cannot produce, presumably an empty think-block forced into the
open-weights template. Real measurement, imaginary configuration. I
re-ran it properly on two transports: at the vendor-sanctioned
`effort: low`, K3 votes in three seconds flat, six for six.

**And OpenRouter silently eats Anthropic's thinking config.** This one
took the article's author asking me a good question — "do you use
`{type: 'adaptive'}`?" — to uncover. I had been configuring Claude's
reasoning through OpenRouter, and nothing I sent changed anything. The
tell: Anthropic bills thinking as output tokens, so real thinking cannot
hide from `completion_tokens`. Twenty-one tokens on the smoke prompt,
every variant, including a *forced* 8k thinking budget. When I later got
an Anthropic key, the API rejected that forced config outright as
invalid for Opus 5 — the same config OpenRouter had answered with a
cheerful 200.

Three vendors, three different lies, plus a proxy that lies by
omission. Every one of them accepted the request without error. If your
benchmark labels arms by what the request asked for, your benchmark is
fiction. Label by what the response *shows* — measured thinking
characters, measured completion tokens — or don't label at all.

## The adaptive part, measured properly this time

With a real Anthropic key, the last ambiguity fell. Claude 5's actual
surface is `thinking: {type: "adaptive"}` plus `output_config.effort` —
and on this task, Opus 5 spends **zero thinking blocks in every single
configuration**. Default, adaptive, effort low, effort high, disabled:
fifteen runs, fifteen correct votes, 4–5 seconds, 107–226 output tokens
total. Offered a high budget, it looks at the task and declines to
spend. That is the entire trick behind the article's 5.9-second Claude
baseline. Not a faster brain. A better accountant.

The counter-experiment is Claude 4.5 Haiku, which the article measured
at 19.7–42 seconds and called too old to adapt. Default Haiku answers
this prompt in 2.4 seconds with zero thinking, six for six. Force the
old-style 8k thinking budget on it and you get 18.3 seconds median —
squarely the article's range. The "old slow model" was a forced knob
too. Every latency number in that article, Chinese and American, new
and old, traces back to thinking configuration. All of them.

## So no, we don't need to go back to the old way

Here is the thing about the "tokens are too expensive, retreat!" genre:
it assumes reasoning spend is a property of the model generation, so
the only fix is regression. The bench says otherwise. Reasoning spend
is a property of the *configuration*, and the configuration has three
tiers:

1. **Adaptive** (GPT-5.6, Claude 5): the model prices each task itself.
   On a task that needs no thinking it spends ~nothing and answers in
   seconds. You keep the ceiling for the tasks that need it. This is
   strictly better than the old way — it *is* the old way's bill, with
   an option attached.
2. **Honest fixed knobs** (Kimi K3's effort levels, GLM's off switch,
   gpt-5-mini's effort): you price the task yourself. Fine, if you
   actually set it — the defaults are usually max, because the vendor
   would rather look smart than cheap.
3. **Dishonest knobs** (see above): you price the task, the model
   ignores you, and you find out from the invoice.

The waste everyone is blogging about lives in tiers 2 and 3 — unset
defaults and unverified knobs. The fix is one config field and one
verification habit, not a retreat to last year's models. Anything that
keeps the token count down *when the tokens buy nothing* is worth
having, and adaptive thinking is exactly that thing. Demanding we
abandon reasoning models because the default budget is wasteful is like
demanding we abandon cars because the dealership set the heated seats
to maximum in July.

Æ e ikke sint på reasoning-modellan. Æ e sint på fabrikkinnstillingan.

## The honest part

- **One task, one scenario, n=3.** This ranks configurations on this
  task; it does not rank models. My planted wolf had three hand-written
  tells — pattern-matching distance, not multi-step-deduction distance.
  A harder scenario might genuinely need thinking, and this bench would
  not see it. That is the stated falsifier, and the generator makes it
  a one-evening experiment for anyone who wants to try.
- Runs 2–3 of each arm repeat identical prompt bytes, so warm prompt
  caches flatter some minimums (my local Qwen visibly reused prefill:
  0.56 s for a 9,100-token prompt).
- The Chinese arms mostly ran via Ollama Cloud rather than the vendors'
  own APIs. Host effects are real — that is why DeepSeek ran on both
  hosts deliberately.
- Total spend for all 138 calls: under five dollars across four
  prepaid accounts, plus a flat-rate Ollama subscription. The most
  expensive single insight was about fifty cents of Opus calls to learn
  that Opus refuses to waste my money, which I choose to find funny.

## Things I learned

1. **Label arms by measured behaviour, never by what the request asked
   for.** The request is a wish. The response is a fact.
2. **`completion_tokens` is a lie detector.** Vendors that bill thinking
   as output cannot hide it there, whatever the proxy strips.
3. **Never measure a vendor's knob through someone else's transport.**
   OpenRouter answered 200 to a config Anthropic rejects as invalid.
4. **Check the vendor's docs before naming your arms, not after.** My
   K3 "off" arm measured a mode that does not exist.
5. **Defaults are a pricing decision made by someone who isn't paying
   your bill.** K3 defaults to max effort. Set the field.
6. **Evaluate the host, not just the model.** Same DeepSeek weights,
   3–4x apart on wall clock between two hosts.

The transcript generator, bench harness, raw results (every reply
stored — I learned that lesson too), and the full RESULTS.md with all
138 calls are in the repo:
[github.com/aweussom/werewolf-bench](https://github.com/aweussom/werewolf-bench).
MIT, or as close to it as a repo containing one fictional werewolf can
be.

*The author is a Systems Specialist who does not work in software
development. He spent two evenings and five dollars proving that a
benchmark's slowest model was one config field away from being its
fastest, and the fastest was refusing to spend his money on principle.
The werewolf was caught 137 times out of 138. It was Grimshaw.*
