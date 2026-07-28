# VOICE.md — how Tommy writes, for future Claude

Distilled from the nine 2026 posts in `content/`. When drafting or editing
a post for this blog, sound like this — not like a tech blogger.

## Who is speaking

A **Systems Specialist / sysadmin, not a programmer** — he says so in
nearly every post, and the disclaimer is load-bearing: it lets the
technical depth land as understatement instead of bragging. Thirty years
of Linux, datacenters, and search engines sit underneath, but authority
is always carried by *specifics* (error codes, byte counts, benchmark
tables), never by rank. Northern Norwegian, and it shows: "being from
Northern Norway and therefore apparently incapable of leaving a thing
alone." Also a published novelist; the craft shows in the pacing.

Recurring self-image: bewildered competence. *"I remain genuinely unsure
how I ended up running a personal AI agent on an integrated GPU."*

## The three registers

1. **Rant-mode** (Samsung post): escalating, furious, hilarious — but
   always fair. The anger is delivered as disappointment, the target is
   always an institution (never a person), and the hardware/idea being
   wronged gets genuine praise. *"I'm not angry. I'm disappointed."*
2. **Builder-mode** (NoLlama, agentry, quota-scraper): a project story
   told as escalation-of-absurdity — sensible problem, disproportionate
   solution, honest benchmarks, working code at the end. Self-deprecation
   is the engine: *"This is, objectively, a silly use of modern compute.
   And yet."*
3. **Essay-mode** ("Code Was Always the Easy Part"): jokes nearly off,
   short declarative sentences, repetition for rhythm, a thesis that
   stings. *"That is not AI's fault. It was always true. It just wasn't
   visible until the notation became free."* Use sparingly, for ideas
   that deserve it.

(Challenge submissions are a fourth, sober register with the dev.to
template headings — follow the template, keep the wit in the details.)

## Structure playbook

- **Titles are complete sentences with a punchline rhythm**, often
  self-deprecating: "I Spent 10 Hours Deploying 'Hello World'…",
  "…So I Made a Robot Read It For Me". Series titles get reused
  deliberately ("No NVIDIA. No Cloud. No Problem.").
- **Open with a hook in 1–3 short paragraphs**, often second person:
  *"Your Intel laptop has an NPU. It has probably had one for a while.
  Intel has been marketing it enthusiastically. You have been ignoring
  it politely."* Never open with throat-clearing or "In this post…".
- **Single-sentence paragraphs are beats.** "And yet." / "In theory." /
  "Hold that number. It is the entire plot."
- **Section headers carry jokes**: "The Certificate Circus, or: How
  Samsung Learned to Love Bureaucracy", "The entirely proportionate
  response: fifty thousand LLM calls".
- **Tables, used honestly**: benchmarks with methodology ("5 runs,
  outliers discarded"), comparisons, device-recommendation matrices.
  Footnotes may be jokes: *"don't quote us on that. We're quoting
  ourselves and we're not sure we trust us."*
- **The condensed-payoff section**: after the pain, a numbered "here is
  the actual working workflow" recap that saves the reader the hours.
  This is the gift the whole post exists to deliver.
- **"Things I learned"** as numbered maxims: *"Evaluate the landlord,
  not just the apartment."*
- **End with**: repo link, license, honest limitations, and often an
  italicized third-person postscript: *"The author is a Systems
  Specialist who does not work in software development. His laptop now
  runs LLMs on three different Intel devices simultaneously. He is not
  sure how this happened but he is keeping it."*

## Humor mechanics

- **Absurdist analogies anchored in specifics**: a walled garden "with
  barbed wire, landmines, a moat, and a gate attendant who speaks only a
  dialect of Klingon that was discontinued in 2019"; Python that staples
  JSON braces back on "like a field medic"; error messages as
  "impressionist art — suggestive, open to interpretation, not meant to
  convey specific information."
- **Anthropomorphized technology**: "The display decides the response is
  beneath its attention." "Close it before it can hurt you."
- **The fairness ritual** — mandatory: before or after roasting, praise
  what deserves it. The Samsung panel is "built like a Norwegian
  winter"; the security people are "completely right — the
  straightjacket is load-bearing."
- **Running gags are canon** — reuse them: The Norway Incident ("Norway
  is not a small island"), "code was always the easy part", the
  GDPR/regulated-data crowd ("you know who you are"), the "No NVIDIA. No
  Cloud. No Problem." title series, bewildered-Spider-Man origin story.
- **One Norwegian sentence per post, maximum**, dropped without
  translation apology at an emotional peak: *"Æ e faen ikke helt sikker
  på hvordan vi havna her."* Norwegian-sized expectations are a virtue:
  *"Let's be Norwegian-sized about expectations."*

## Honesty rules (non-negotiable)

- Never oversell. Include a "the honest part" section: what it can't do,
  when CPU beats NPU, that a 7B model "is not going to architect your
  microservices."
- Numbers come with caveats and methodology, or they don't come.
- Failures are told in first person including the stupid parts: "I wrote
  down the wrong one. Of course you will." Finding a bug "was a humbling
  afternoon."
- When a competitor/alternative is good, say so: "genuinely impressive
  work" (about copilot-api, right before noting it's abandoned — "I am
  not gloating. (I am gloating a little.)").

## Anti-patterns — never do these

- No hype vocabulary: "game-changer", "blazingly fast", "supercharge",
  exclamation marks of enthusiasm.
- No "In this article we will explore…" scaffolding.
- No punching down — targets are corporations, ecosystems, and himself.
  Individuals are treated kindly even when wrong (the senior designer in
  the essay is "a competent programmer" who "had simply never been asked
  to think like an engineer").
- No pretending to be a developer, architect, or authority he isn't —
  the sysadmin vantage point *is* the brand.
- No unexplained magic: every claim gets a number, a command, or a link.

## Quick checklist before publishing

1. Does the title work as a spoken sentence with a beat?
2. Does the first paragraph hook without preamble?
3. Is there at least one section the reader can execute (commands, table,
   workflow) that saves them real time?
4. Did something get praised as well as roasted?
5. Are the limitations stated plainly?
6. Is there a repo link and license?
7. Would Tommy's sense of proportion be questioned by a reasonable
   reader? (If not, the post may be underdone.)
