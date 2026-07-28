Title: I Built an OpenAI-Compatible Proxy for GitHub Copilot Because Search Was Too Stupid to Understand Norwegian Guitar Tabs
Date: 2026-05-26 11:24
Slug: i-built-an-openai-compatible-proxy-for-github-copilot-because-search-was-too-stupid-to-understand
Tags: githubcopilot, python, json, ai
Summary: Updated 2026-07-28 with Copilot SDK &amp; agy findings.  I named it agentry (because it gives an AI...
Original: https://dev.to/tommy_leonhardsen_81d1f4e/i-built-an-openai-compatible-proxy-for-github-copilot-because-search-was-too-stupid-to-understand-31de

_Updated 2026-07-28 with Copilot SDK & agy findings._

I named it _agentry_ (because it gives an AI agent persistent entry)

Software projects are supposed to begin with a sensible problem and proceed toward a proportionate solution.

Mine began with:

> "Why can't I search for that bittersweet Trønderrock song about driving home from a funeral?"

Normal people would shrug and type a few more words.

I, being from Northern Norway and therefore apparently incapable of leaving a thing alone, built a semantic search engine, an LLM enrichment pipeline, and eventually an OpenAI-compatible proxy in front of the coding-agent subscriptions I was already paying for.

This is, objectively, a silly use of modern compute.

And yet.

## The original problem: search is usually dumb

![NorTabs search for "melankolsk" — semantic enrichment surfaces songs that don't contain the literal word anywhere in their lyrics or title]({static}/images/i-built-an-openai-compatible-proxy-for-github-copilot-because-search-was-too-stupid-to-understand/01.png)

I have a hobby project called **NorTabs-web**, a static web app for browsing Norwegian guitar tabs.

Not Spotify. Not some venture-funded AI music startup. Just thousands of lovingly hand-transcribed guitar tabs from a Norwegian site, packed into one giant JSON blob and served in a browser like it's 1999.
Load-time is a wee bit slow - content is about 7 MB; About the same as a large-ish image. Search/Drilldown is INSTANT however.

Raw search worked, in the usual way:

* title match
* artist match
* maybe a lyric fragment if you were lucky

But human memory doesn't work like that.

People remember:

* "that melancholic Eurovision song"
* "a Trøndelag roadtrip vibe"
* "children's songs"
* "that one line about wanting to earn money with my body"

The raw tab data does not contain "melancholic", "roadtrip", "Eurovision", or "midlife crisis but with acoustic guitar".

So substring search was not enough.

## The entirely proportionate response: fifty thousand LLM calls

Naturally, I built an enrichment pipeline.

Each artist got metadata: genre, era, country, region, similar artists.

Each song got: mood, themes, occasions, alternate titles, lyric phrases, search-oriented semantic tags.

This meant that searching for:

> `trondheim`

could also match trønderrock, nidaros, trondhjem, trøndelag.

And searching for:

> `melankolsk`

might surface the right heartbreak song, even if the original tab never contained that word.

This required… somewhat more LLM calls than is emotionally healthy.

At one point I had scripts serializing enrichment runs across thousands of entries, checkpointing JSON, resuming partial runs, salvaging truncated model output, and retrying fallback entries.

There is Python in this project that exists purely to detect whether an LLM died halfway through a JSON object and then gently staple the braces back on like a field medic.

This may have been a warning sign.

## The CLI overhead problem

My enrichment scripts originally used CLI tools in the simplest possible way:

```text
LLM CLI -p "prompt"
```

Which works.

If by "works" you mean:

* spawn process
* initialize runtime
* load model plumbing
* authenticate
* run prompt
* tear everything down
* repeat fifty thousand times

This is acceptable for casual use.

It is less charming when you are grinding through thousands of enrichment calls because you want guitar-tab search to understand *vibes*.

## The stupid little proxy that worked suspiciously well

So I wrote a Python wrapper that:

* holds one persistent agent runtime alive across requests
* speaks its wire protocol so nothing gets torn down between calls
* translates everything into OpenAI-compatible HTTP endpoints
* streams deltas in SSE format
* denies every tool request, so the agent stays a pure chat brain

That last point grew into the framing I'm most fond of. MCP exists so models can consume tools. Agentry points the arrow the other way: it takes an agent that was *built* to call tools, confiscates the tools, and serves what's left — the model — to ordinary software over HTTP.

The agent built to call tools becomes the tool.

![Agentry startup: the SDK client starts in under two seconds, reports the authenticated login, opens a session, and settles into an idle heartbeat. Every subsequent request lands on the same warm process.]({static}/images/i-built-an-openai-compatible-proxy-for-github-copilot-because-search-was-too-stupid-to-understand/02.png)

So now anything that speaks:

```text
POST /v1/chat/completions
```

can talk to my local subscription-backed proxy as if it were a normal OpenAI API. Per-turn latency dropped from ~8 seconds of process churn to roughly the model's own thinking time.


## Embedded chat client
I also added a chat-client I originally had written another project, so that you can test end-to-end without having to write any code. 
It is surprisingly capable; but no chat history. Yet.

![The bundled chat UI talking to the proxy as a regular OpenAI endpoint — markdown, copy buttons, live thinking blocks, per-turn backend and latency tags.]({static}/images/i-built-an-openai-compatible-proxy-for-github-copilot-because-search-was-too-stupid-to-understand/03.png)

## It always adds up
This was supposed to be a weekend spike.

It worked quite a bit better than it had any right to. It is now, and I say this with the appropriate mixture of pride and concern, **in production**.

## Plot twist: GitHub legalized my hack

The first version of agentry drove Copilot CLI through its `--acp` mode — a JSON-RPC server that was clearly intended for editor integrations and not for a Norwegian man with a guitar-tab problem.

Then GitHub shipped an official **Copilot SDK**. A GA, documented, supported product surface for embedding Copilot programmatically.

My gray-zone hack became a sanctioned integration while I wasn't looking. I deleted my hand-rolled protocol client, swapped in the SDK, and the whole thing got *more* legitimate over time, which is not the usual direction for my projects.

Is "strip the agent of every tool and serve the bare model back out as an OpenAI endpoint" the use case GitHub pictured when they published an SDK for embedding agents? Almost certainly not. But that's the thing about front doors: once you're invited in, nobody dictates what you cook.

Remember this direction of travel — a vendor *opening* its subscription to programmatic use. It becomes relevant, by way of contrast, shortly.

## Then it grew tiers

The backend layer turned pluggable, and agentry now fronts three subscriptions through one endpoint:

* **Copilot** (free tier) — the official SDK, persistent session, `gpt-5-mini` for $0
* **Codex** (paid-cheap) — `codex app-server` over JSON-RPC, riding a $8-20/month ChatGPT plan
* **Claude Code** (premium) — cold-start `claude -p` per turn, for the tasks that deserve Sonnet

People get weirdly religious about which coding agent is best. I do not care. I prefer driving a BMW; I also own a Tesla Model 3 and a 2001 Freelander, and they all get me to the cabin. Harnesses are just cars. The model behind them is what matters, which is why my tiers are named after subscriptions and not after CLIs.

## Meanwhile, in the reverse-engineering business

Agentry was never the only project in this space. The best-known one, `copilot-api`, took the other road: reverse-engineer Copilot's internal HTTP endpoints, impersonate an editor, mint tokens, serve everything as an API. Broader scope than mine, more users, genuinely impressive work.

It has been unmaintained since October 2025. There is an open issue titled, plaintively, *"Is this a stale repo?"*

The commit log tells you why. When you build on an internal protocol, your maintenance work is a treadmill of `update vscode fallback ver` commits, and the day you stop running, the project dies. The community moved to a fork, which now runs the same treadmill.

I am not gloating. (I am gloating a little.) The lesson is just very clean: **build on the surface the vendor promises to keep, not the one you found in a network trace.** My half of the trade was less capability and a narrower scope; the payoff is that GitHub's releases make agentry *better* instead of breaking it.

## And then there was Google

This is the part where I make fun of Google, because I evaluated their Antigravity stack as a fourth backend **three separate times** and each round was funnier than the last.

**Round one (May):** The `google-antigravity` Python SDK ships no Windows wheel. The `agy` CLI works, but its print mode reprints the *entire conversation transcript* on every call, like a colleague who answers every email by quoting the whole thread. Shelved.

**Round two (July, morning):** The Windows wheel shipped! The SDK API is genuinely lovely — in-process agent, streaming, native tool-stripping, usage metadata. I had it running in a scratch venv in minutes. Then it made its first model call and billed my *prepaid AI Studio credits*, because the SDK supports API keys and Vertex projects and **nothing else**. No subscription auth. The one thing worth unlocking — the sponsored quota your Antigravity login carries — is the one thing the official SDK cannot touch.

Sit with that. GitHub built an SDK so your subscription could be used programmatically. Google built an SDK that goes out of its way to make sure it *can't* be. Same idea, opposite direction.

Only one of them noticed that **the subscription is the product**.

**Round three (July, afternoon):** Fine, wrap the CLI then, claude-code style. And credit where due — `agy` 1.0.2 passed every technical test I threw at it: proper stream-JSON output, reasoning-effort flags, headless tool denial. Technically, it cleared the bar.

Then I looked up what the "generous" quota had become. The launch-era free tier — the one that made everyone excited — has been community-documented at roughly **20 requests a day**, refreshing *weekly*, down from 250 at launch. That is not an enrichment backend; that is a quota for asking one question before lunch. The paid tiers fare little better unless you buy the $200/month one. And as garnish: Google has reportedly suspended *entire Google accounts* — including paying subscribers — for driving their subscription through third-party tools. Your Gmail, your Drive, your photos, gone, because you pointed a script at the thing you pay for. GitHub and Anthropic tolerate the gray zone. Google, by every community account I can find, salts it.

So: declined, permanently, and not for technical reasons. They fixed the wheel, they fixed the streaming, and while they were at it they gutted the quota and started banning customers. It's enshittification speedrun any%: most products at least wait for the *second* funding cycle.

And here is my subjective, benchmark-free, absolutely unfair opinion, offered as a man who runs LLM calls across sixty-odd projects and pays for the privilege from his own pocket: the Gemini models I'd be fighting all of this to reach feel six to twelve months behind what I already have. I don't care what the leaderboards say. I care what happens when I feed a model a Norwegian guitar tab and ask for its mood. Yes, I have a very specific life.

## Things I learned

### 1. CLI tools are often secretly protocols

A lot of "interactive" developer tools sit on top of actual machine interfaces. Find the protocol and you can build smarter wrappers than the intended UX exposes. Sometimes the vendor then blesses it with an SDK, and your hack retroactively becomes architecture.

### 2. Persistent sessions matter more than you think

Process startup overhead is tolerable once. Not fifty thousand times. Keeping the backend warm dropped latency from "why did I do this to myself" to "actually usable."

### 3. Search becomes interesting when you stop treating words literally

Substring search is useful. Semantic LLM enrichment makes search feel like memory. That was the entire point of this exercise, buried underneath a mountain of accidental systems engineering.

### 4. Only wrap what's actually locked up

A backend candidate has to pass a simple test: is there a model here you can *only* reach through the subscription? Qwen failed it — they'll happily sell anyone the API directly, so there's nothing to liberate. Antigravity failed it twice, from both ends: the SDK can't reach the subscription, and the subscription isn't worth reaching.

### 5. The vendor's temperament is part of the stack

Same architecture, three vendors, three outcomes: GitHub opened a front door, Anthropic and OpenAI tolerate polite use of the side entrance, Google reportedly deletes your account for touching the doorknob. Evaluate the landlord, not just the apartment.

### 6. The internet should probably not know about every hack

This proxy lives partly in a gray area (one backend is now fully sanctioned, which still feels strange to type). It uses my own logins. It runs locally. It is not a SaaS business, and Claude willing it never becomes one.

## Closing thoughts

People sometimes imagine software engineering as disciplined architecture guided by clear requirements.

Sometimes it is.

Sometimes it is:

> "I need guitar-tab search to understand emotional context."

…followed by:

* JSON-RPC
* SSE streaming
* semantic indexing
* quota-aware LLM pipelines
* recovery code for mutilated JSON
* an OpenAI-compatible proxy with three subscription backends
* a formal written policy on why Google is not a fourth

And then, several weekends later, you look at the repo and think:

> "Æ e faen ikke helt sikker på hvordan vi havna her."

But the search works.

And, in fairness, that bittersweet Trønderrock song *does* show up now.

Which is more than can be said for my sense of proportion.

*Code: [github.com/aweussom/agentry](https://github.com/aweussom/agentry). Personal project, now embarrassingly load-bearing.*
