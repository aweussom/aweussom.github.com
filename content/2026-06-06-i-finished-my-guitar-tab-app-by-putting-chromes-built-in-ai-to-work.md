Title: I Finished My Guitar-Tab App by Putting Chrome's Built-In AI to Work
Date: 2026-06-06 06:03
Slug: i-finished-my-guitar-tab-app-by-putting-chromes-built-in-ai-to-work
Tags: devchallenge, githubchallenge
Summary: This is a submission for the GitHub Finish-Up-A-Thon Challenge           What I Built   TabTabTab is...
Original: https://dev.to/tommy_leonhardsen_81d1f4e/i-finished-my-guitar-tab-app-by-putting-chromes-built-in-ai-to-work-114

*This is a submission for the [GitHub Finish-Up-A-Thon Challenge](https://dev.to/challenges/github-2026-05-21)*

## What I Built

[TabTabTab](https://github.com/aweussom/tabtabtab) is a static, offline-first guitar-tab web app. Its most unusual feature is not an AI chat box: it gives Chrome's built-in Gemini Nano model a real batch-processing job.

It began as **NorTabs**, a browser for roughly 7,700 Norwegian guitar tabs from [nortabs.net](https://nortabs.net). The entire catalog is downloaded as static data and searched locally. There is no application backend, no account, no tracking, and no live dependency on the source site's API.

That version worked, but it had reached an obvious boundary: it could only browse the catalog I had shipped with it.

For this challenge I finished the other half of the idea. The renamed TabTabTab can now import a user's own Ultimate Guitar bookmarks, enrich them locally with Chrome's on-device Gemini Nano model, mix them into the same search index as the Norwegian catalog, and optionally sync them through the user's own Google Drive.

I had seen plenty of built-in-AI demos where someone submits one prompt and displays one response. I wanted to find out whether the model could do ordinary application work.

My test library contained 259 Ultimate Guitar bookmarks. The exporter recovered 253 usable tabs; six were publisher-locked. TabTabTab then treated those 253 tabs as a real enrichment workload. For each tab, Gemini Nano reads the artist, title, and chord/lyric body and produces structured search metadata:

- themes;
- mood;
- occasions;
- language;
- alternate titles;
- memorable lyric phrases;
- a compact search-oriented keyword field.

The output is not displayed as a novelty response. It is parsed, repaired when the model returns imperfect JSON, persisted in browser storage, inserted into the actual search index, and optionally synchronized to Google Drive. The application becomes measurably more useful after the model has done the work.

Making that reliable required the less glamorous parts that demos usually omit:

- feature detection and a useful non-AI fallback;
- background download of the multi-gigabyte model;
- model-download progress reporting;
- a single-batch work queue;
- per-tab progress and error accounting;
- balanced-JSON extraction, JSON5 parsing, salvage, and retry;
- immediate persistence so completed work survives navigation;
- index rebuilding when the batch completes;
- background execution while the user continues browsing.

The architectural rule remained:

> If it can be done in JavaScript, it shall be done in JavaScript.

So the finished application still has:

- no framework or build step;
- no application server;
- no database;
- no API key for on-device enrichment;
- no upload of the user's copyrighted tabs to my infrastructure;
- no storage belonging to me.

It is plain HTML, CSS, and JavaScript modules. The browser is the application platform, search engine, database, AI runtime, batch worker, and offline cache.

The feature I care most about is search. Raw tab data can answer queries such as an artist name or lyric fragment. Enriched metadata lets the same local index answer fuzzier human memories:

- "melancholic Eurovision song";
- "Trondheim roadtrip";
- "wedding songs";
- a half-remembered lyric with spelling mistakes;
- themes, moods, occasions, regions, and alternate titles that never appeared in the original tab.

The search engine is dependency-free JavaScript. It combines inverted indexes, IDF weighting, prefix expansion, diacritic folding, typo correction, phrase detection, body-to-song score propagation, and small hand-curated alias tables.

This project does not need to exist. That is also why it has been such a useful place to experiment.

## Demo

- **Live application:** [nortabs.netlify.app](https://nortabs.netlify.app)
- **Source:** [github.com/aweussom/tabtabtab](https://github.com/aweussom/tabtabtab)
- **Ultimate Guitar import guide:** [open the guide](https://nortabs.netlify.app/docs/import-ug-guide.html)
- **Agentry, the Copilot-backed tool created during the process:** [github.com/aweussom/agentry](https://github.com/aweussom/agentry)

The original application was a focused Norwegian catalog browser:

![NorTabs before the finish-up: letter browsing and local semantic search](https://raw.githubusercontent.com/aweussom/aweussom-gist-images/main/tabtabtab/01-home.png)

The finished application adds a bring-your-own-tabs import flow. Drop an export into the page and Chrome's built-in model enriches each tab locally:

![Ultimate Guitar import page with on-device AI ready](https://raw.githubusercontent.com/aweussom/aweussom-gist-images/main/tabtabtab/ug-6.png)

Enrichment runs as a background queue, so the user can leave the import page and continue using the application:

![Background enrichment processing a 253-tab import](https://raw.githubusercontent.com/aweussom/aweussom-gist-images/main/tabtabtab/ug-7.png)

Imported artists become first-class entries alongside the static catalog. The small red `U` identifies user-imported content:

![Imported artists mixed into the normal letter browser](https://raw.githubusercontent.com/aweussom/aweussom-gist-images/main/tabtabtab/ug-8.png)

The resulting tab behaves like any other tab: it is searchable, can be placed in songbooks, supports text resizing and auto-scroll, and remains available offline:

![An imported Jolene tab rendered in TabTabTab](https://raw.githubusercontent.com/aweussom/aweussom-gist-images/main/tabtabtab/ug-jolene-rendered.png)

## The Comeback Story

Before the challenge, NorTabs was already a useful static catalog browser. It had:

- alphabetic artist, song, and tab navigation;
- an enriched local search engine;
- favorites and shareable songbooks;
- responsive chord-over-lyric wrapping;
- auto-scroll for playing;
- a scheduled crawler that kept the static catalog current.

But it was still a closed collection. The roadmap contained several competing ideas for private imports: a cloud proxy, prebuilt private bundles, command-line enrichment, and eventually Word document import. They were technically possible, but none completed the product I actually wanted.

The challenge period forced a decision: stop expanding the plan and finish one coherent path.

The completion arc was:

1. **Prove local enrichment.** I built a standalone experiment using Chrome's Prompt API and Gemini Nano, including recovery for imperfect JSON output.
2. **Make it survive a real workload.** I ran the path against a 253-tab personal library rather than a hand-picked single prompt, then added progress, failure accounting, recovery, and retry.
3. **Turn the experiment into a real import route.** Ultimate Guitar exports could be dropped directly into the application.
4. **Make imports part of the product.** Imported artists and songs joined normal browsing, search, navigation, and songbooks instead of living in a separate demo.
5. **Move long work into the background.** Model download and enrichment gained progress reporting, a queue, and a global status pill.
6. **Keep non-Chrome browsers useful.** They perform literal imports and retain artist, title, lyric, and chord search even without the semantic layer.
7. **Add private cross-device sync.** Google Drive's hidden `appDataFolder` stores the user's imports. The app can pull, merge, and push without operating a storage service of its own.
8. **Make it public.** I removed my personal Ultimate Guitar library, cleaned up stale experiments, wrote the import guide, collected screenshots, and moved deployment from a dead GitHub Pages URL to Netlify.

During the entry period I made 74 commits. The important change was not the number of files or features. It was reducing several plausible architectures to one understandable product:

> Export your bookmarks, drop the file into TabTabTab, and let your own browser do the rest.

Word document import is still a possible future feature, but it is deliberately deferred. Finishing this project required deciding what *not* to finish.

## My Experience with GitHub Copilot

GitHub Copilot supported this project, but not mainly by writing the JavaScript.

I turned Copilot into infrastructure.

While experimenting with semantic enrichment, I wanted ordinary Python scripts to use GitHub Copilot CLI as an LLM backend. Calling it once per item with `copilot -p` worked, but repeatedly starting and authenticating a coding-agent process added several seconds of overhead to every request. That is painful when an enrichment job contains hundreds or thousands of calls.

Then I found Copilot CLI's Agent Client Protocol mode:

```text
copilot --acp
```

ACP exposes structured JSON-RPC over standard input and output. That meant the process did not need to be restarted for every prompt.

I built [Agentry](https://github.com/aweussom/agentry), a small Python service that:

- starts one persistent `copilot --acp` process;
- performs the ACP initialization and session handshake;
- keeps the process warm across requests;
- translates prompts and streamed responses;
- exposes an OpenAI-compatible `/v1/chat/completions` endpoint;
- rejects filesystem, permission, and tool requests so the coding agent behaves as a pure language service.

In other words, instead of Copilot consuming tools, my enrichment code consumed Copilot.

```text
Normal coding agent:  model  ---> tools
Agentry:             my code ---> model
```

The persistent process reduced short-request latency from roughly eight seconds in repeated `-p` mode to approximately the model's own two-to-three-second response floor. More importantly, it gave my experiments a standard HTTP interface. I could compare approaches and swap model backends without rewriting the enrichment pipeline.

That experimentation helped me reach the final architecture and made the Chrome result more interesting. Gemini Nano was not being compared on a toy prompt; it had to replace a working, scriptable remote-model pipeline:

- Copilot through Agentry was valuable as a programmable enrichment and evaluation backend.
- A remote or account-backed model was the wrong default for users' private tab libraries.
- Chrome's on-device model could perform the shipped enrichment workload without a server, API key, per-request cost, or upload.
- The older CLI pipelines remain useful for benchmarking and QA rather than being required by the web app.

So Copilot's contribution was slightly sideways. It did not just suggest implementation details. Its protocol mode became a reusable development tool, and building that tool clarified which AI responsibilities belonged in the final application and which did not.

I wrote more about that detour in [I Built an OpenAI-Compatible Proxy for GitHub Copilot Because Search Was Too Stupid to Understand Norwegian Guitar Tabs](https://dev.to/tommy_leonhardsen_81d1f4e/i-built-an-openai-compatible-proxy-for-github-copilot-because-search-was-too-stupid-to-understand-31de).

The result is a finished application whose production AI runs locally, plus a separate Copilot-powered tool that came out of discovering where the product boundary should be.
