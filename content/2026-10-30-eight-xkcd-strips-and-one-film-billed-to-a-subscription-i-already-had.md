Title: Eight xkcd Strips and One Film, Billed to a Subscription I Already Had
Date: 2026-10-30 15:00
Slug: eight-xkcd-strips-and-one-film-billed-to-a-subscription-i-already-had
Tags: ai, python, comics, agentry, grok
Summary: agentry got image and video endpoints over the summer. Nobody noticed, so I pointed a comic pipeline at it and redrew eight xkcd strips as a webtoon with a recurring cast, then made one of them into a film. Two evenings, one API key used twice, the rest on subscriptions. Numbers, failures and a demo repo with an installer my brother can run.

Do you have Claude Code, OpenAI's codex CLI, GitHub Copilot CLI or Grok Build installed and logged in?

Then you have an API. Not the one you pay per token for. The one you already pay for by the month, sitting behind a coding agent that only wants to talk about your repo.

[agentry](https://github.com/aweussom/agentry) is the proxy that takes the model behind one of those CLIs and serves it as an OpenAI-compatible endpoint on localhost. Last time I wrote about it, it let my scripts talk to GitHub Copilot, so I could enrich fifty thousand guitar tabs on a subscription, not a credit card. That post ended with the repo doing far more work than it was ever meant to.

Since then it grew three more backends and, almost by accident, image generation. Codex ships an image tool. Grok Build ships one too, plus image-to-video. agentry's job is to strip the tools off a coding agent and hand you the bare model, so the obvious move was to strip everything except the image tool and expose it as `/v1/images/generations`, `/v1/images/edits` and `/v1/videos`. Which I did, in September and on 5 October.

Then it sat there. agentry has eight stars and a README. A README does not show that the same face comes out of the model forty times in a row.

So I needed a demo, and there is one body of work every engineer on the internet already knows panel by panel.

## The premise, and the part where I asked permission from nobody

xkcd is CC BY-NC 2.5. You may copy and adapt it, with credit, not for money. Is "redraw it with an image model as a demo for my proxy" within what Randall Munroe had in mind when he picked that licence? The licence text does not settle that. My position is the only one available to me: credit him on every image, in the footer, in the repo, in this post, and take it all down if he asks.

The dialogue is his, word for word, including the words the image model might have refused. The drawings are a cast I made: Cueball, Megan and Black Hat as a modern 3D-cartoon trio, two extras, and a character card for each. Nine strips were picked on the evening of 6 October. Eight became strips. One, #162 "Angular Momentum", became a film, because a woman spinning in a dark bedroom to slow the planet down is a shot list, not a panel.

![Eight redrawn xkcd strips in a grid, each with an xkcd credit footer]({static}/images/eight-xkcd-strips-and-one-film-billed-to-a-subscription-i-already-had/01-grid.jpg)

## The pipeline is the point, and it is semi-automated on purpose

I make my own daily comic with a tool called `comic.py`. A project is a folder: canon text, character cards, one markdown draft per strip. The script assembles the prompt, attaches the cards, calls an OpenAI-compatible endpoint, keeps every result with the prompt that made it, and opens a page in the browser where I click the run I want, or click a panel and type what is wrong. `approve` adds the header and draws the credit footer with Pillow, because lettering is the one thing I will not trust an image model with.

The only agentry-specific line in that whole tool is `base_url = http://localhost:8770/v1`.

"Semi-automated" is not an apology. The human in the loop is one click per strip and one sentence per bad panel. That is cheap enough to do every day and expensive enough that nothing ships unseen.

## The numbers

Measured on 6 and 7 October, Windows 11, agentry 0.2.0, the same drafts and the same cards through both backends.

| | codex via agentry | Grok Build via agentry |
|---|---|---|
| One strip, four to five panels, one call | 75 to 90 s | about 30 s |
| Identities held, one call | 8 of 8 strips | 2 of 4 panels |
| One strip, one call per panel, stitched | not needed | 2 min 13 s, 5 of 5 panels |
| One 2:3 key frame | not used | 29 to 56 s |
| One 6 s clip, 480p | no video tool | 37 to 48 s |

Seven of eight strips were right on the first codex run. The eighth needed one panel redone because the two characters had swapped sides. 705, "Devotion to Duty", came out like this on the first try, with Black Hat cast as the sysadmin because the original's alt text says that kind of devotion "can border on the sociopathic":

![705 Devotion to Duty redrawn: two hostage takers in a control room, then Black Hat in a server room with duct-taped feet plugging a cable back in]({static}/images/eight-xkcd-strips-and-one-film-billed-to-a-subscription-i-already-had/02-devotion-to-duty.jpg)

Ask Grok for a whole strip and it swaps roles between panels. Panel 1 right, panel 2 right, and by panel 4 Cueball is wearing Megan's top. Ask for one panel at a time, with panel 1 sent back as a style reference, and it does not. That became a `--panels` flag. The rendering drifts toward photoreal unless the style is stated three times in three ways, which is a trick I learned making films with it, and it works for strips too.

## The film

Nine shots, each with a prompt for the key frame and a prompt for the movement. Key frames came from Grok with the two cards and an empty bedroom as a room reference, which is how you keep the same window in every shot. Clips came from Grok's image-to-video at six seconds a piece, cut to length, with a still and a slow zoom for the two shots that did not need motion. The subtitles fall out of the same script as an `.srt`. Voices are xAI's text-to-speech, one preset for her and one for him, placed at the subtitle times with ffmpeg.

![Angular Momentum, redrawn, with subtitles]({static}/images/eight-xkcd-strips-and-one-film-billed-to-a-subscription-i-already-had/03-angular-momentum.webp)

Shot 3. The line is "Spinning counterclockwise." Grok Build's first take spun her clockwise. The second take kept her face locked on the camera while her body rotated, which is a scene from a different film. The third spun her clockwise again. The same key frame and the same prompt through xAI's API directly, on their cheapest video model, spun her the right way at the first attempt. 19 seconds, 12 cents.

![Same key frame, same prompt: agentry's clip and the API's clip at three timestamps]({static}/images/eight-xkcd-strips-and-one-film-billed-to-a-subscription-i-already-had/04-agentry-vs-api.jpg)

So that one clip is the API's, and the film says so. Everything else in it is agentry on a subscription.

## What did not work, so you do not have to

- "Counterclockwise" in a video prompt is read both ways. Say "she turns toward her own left, right shoulder toward the camera".
- "Turns on the spot" can lock the head. Say that the face turns away and comes back.
- A key frame of "the window alone" drew a different window. Say what must not be in the frame, or the model fills it from the room reference, empty bed and all.
- A card for a character who is not in the panel invites them in. Send cards only for the people named in that panel.
- Speech bubbles are read top to bottom. The first line must sit higher than the reply, or the joke runs backwards. Image models do not know this. Tell them.

## Before you clone it

Two subscriptions were used, ChatGPT for the strips and SuperGrok for the film. That is taste: I like the look of codex's images better. One subscription does the whole job; Grok draws strips panel by panel, and the proof is in the repo next to the codex version of the same strip.

The API key was used twice: the one clip, and the voices, because agentry does not expose a speech endpoint. For a weekend film the API is also cheaper than the subscription, by a factor of two to four. A weekend film is about 60 seconds of clips and 40 images, which is a few dollars on the API against a 399 kr month. The subscription wins only if you burn the whole weekly quota, which I came close to once, debugging.

Grok's video tool through agentry has a six second floor and needs the account's training opt-in switched on, which is account-wide. The API has neither problem. These are the things a demo built on "no API key" has to say out loud.

The Grok strip does not look like the codex one. Same two people from the same cards, but drawn like a 3D animated film, at full length, faces small. Part of that was my canon, which asked for a 3D film look.

On 1 November I tried to pull it over: a canon that describes the cards as drawn with ink outlines, and then a finished codex panel as a style reference. The outlines came. The washed-out colours and the distance stayed, and the reference panel changed close to nothing.

For a demo whose point is "same cast, two backends" that is fine. For a series, pick one backend.

## The repo, and an installer for my brother

[github.com/aweussom/agentry-demo](https://github.com/aweussom/agentry-demo) has the tool snapshot, the project, the strips, three cuts of the film, and the originals beside them. MIT for code, CC BY-NC 4.0 for everything that carries Munroe's work.

`install-windows.bat` is written for my brother. He is the smartest man I know and the easiest to confuse, which makes for long support calls. I like him more than I like most people, which is not a high bar, but it is the reason any of this exists: I learned to draw comics and make film with these models so I could help him with his, and Kona & Co, my own daily strip, started as the practice ground. The installer refuses to run from OneDrive or a long path, installs PowerShell 7 and Python if they are missing, fetches ffmpeg and agentry's latest release zip, makes a venv, and then checks whether `codex` or `grok` is actually logged in, loudly, with the command to fix it. `demo.bat` draws a strip and opens the picker. There is a `keys.ini` in the repo with no keys in it. The whole thing works from a zip unpacked to `C:\`.

## Things I learned

1. Continuity is cards plus canon sent with every request. A seed does not do it.
2. When a model fails the same way three times, change the words. When it fails a fourth time, change the model and say so.
3. Credit goes inside the image, drawn by code. Models cannot be trusted with the one line that matters legally.

## Update, 1 November: a new kitchen in every panel

My brother's first strips came back with the people intact and the house rebuilt in every panel. In one, panel 1 is the yard and panels 2 to 4 are the kitchen. The kitchen had flowered curtains, then checked ones, then flowered again. The lamp showed up in panel 4. The table cloth changed twice.

The film had an empty room as reference from the first shot. The strip tool did not. Each panel is drawn on its own and gets panel 1 back as a reference. That was enough for me, because my own strips mostly open in the room they stay in. His opened in the yard.

So; `comic.py` now has room cards. `comic.py rom kitchen "yellow walls, checked curtains, green cupboard"` draws the room with nobody in it, and `[rom: kitchen]` in a panel paragraph sends that picture with the panel. Same draft, same cards, one run each:

![The same four-panel strip twice. Top row without a room card: the kitchen changes between panels. Bottom row with one: same walls, curtains, lamp and table cloth.]({static}/images/eight-xkcd-strips-and-one-film-billed-to-a-subscription-i-already-had/05-room-card.jpg)

One run each is an anecdote, not a measurement. codex through agentry held the same kitchen too, at two minutes a panel against fifteen seconds on the API. One of its panels put the two of them on the wrong sides of the table. That is the draft's fault: the panel did not say who sits where.

The room cards are in the demo repo. My brother got a new zip with them and a wizard. He does not write much, so codex runs the wizard. He tells it the joke the way he remembers it, and it asks him the rest, one question at a time.

*Code: [github.com/aweussom/agentry](https://github.com/aweussom/agentry) and [github.com/aweussom/agentry-demo](https://github.com/aweussom/agentry-demo). Strips after xkcd by Randall Munroe, CC BY-NC 2.5. If he objects, they come down.*

*Disclosure: a bot wrote this. The proxy, the pipeline, the drafts, the three wrong spins and every number are mine; the sentences were drafted by Claude Code from my notes and the repo, then argued with until they sounded like me. The strips were drawn by two other models, which makes this post a committee of four about a man who says he is not a developer.*

*The author is a Systems Specialist who does not work in software development. He now owns a comic pipeline, a video pipeline, a proxy with four backends and a release process, all so he could help his brother. He is not sure how this happened but he is keeping it.*
