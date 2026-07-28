Title: The Robot Read My Claude Quota With 235 Billion Parameters. I Fired It and Hired a JSON File.
Date: 2026-07-28 23:15
Slug: i-fired-the-quota-robot-and-hired-a-json-file
Tags: claudecode, powershell, bash, windows
Summary: The screenshot-eating vision model is retired. Its replacement is a cache file, two small libraries, and the API endpoint that was there all along. v1.0.0 is out, and it's a Claude Code plugin now.

In February I introduced you to the robot: a PowerShell script that mashed
Print Screen every sixty seconds, and a 235-billion-parameter vision model
that read my Claude quota percentages off the screenshots like a very
expensive grandmother squinting at a thermometer.

It worked. That was never the problem. The problem was that it worked, and
therefore I had no reason to stop, and somewhere in Frankfurt a GPU was
burning watts to tell me the number 68.

Æ brukte to hundre og trettifem milliarder parametre på å lese fire tall.

The robot is retired now. This is the story of its replacement, which is a
JSON file with a timestamp.

## The confession

There was an endpoint all along.

Claude Code logs you in with OAuth. The token it stores can ask
`api.anthropic.com/api/oauth/usage` for your quota, and the answer comes
back as clean, well-formed JSON — session percentage, weekly percentage,
reset times, the lot. No screenshots. No OCR. No vision model contemplating
my browser tabs.

I did not discover this. Smarter people did —
[claude-quota-tracker](https://github.com/jonis100/claude-quota-tracker),
[ccusage](https://github.com/ryoppippi/ccusage), and
[ccstatusline-usage](https://github.com/pcvelz/ccstatusline-usage) all got
there first, and credit lives in the README where it belongs. My
contribution was noticing that every one of these tools assumed you lived a
tidy little life inside one operating system.

I do not. I run Claude Code natively on Windows 11 *and* inside WSL2,
sometimes in the same hour, because being from Northern Norway apparently
means never having to say "this environment is good enough."



## The architecture (now with actual architecture)

[claude-code-quota](https://github.com/aweussom/claude-code-quota) is two
small libraries — one PowerShell, one bash — that your status line script
calls on every refresh:

1. Check the age of a local cache file (`~/.claude/quota-data.json`)
2. Fresh enough? Return immediately. No network call, no waiting.
3. Stale? Fire a background refresh — detached, non-blocking — and return
   the *previous* frame's data right now. The next frame gets fresh numbers.
4. First run ever? Block briefly, once, so the status line isn't blank.

The TTL is 60 seconds while you're actively working and 5 minutes while
you're not, which the library figures out from how recently your session
transcript was written. No daemon. No scheduled task. No process
squatting in the background waiting for you to need it. The status line
refresh *is* the scheduler, and it never pays more than the cost of
reading one small file.

The result, permanently in view:

```
Sonnet 4.6 | main | ctx:42% | 5h:68% ~1h12m | 7d:31% ~4d2h
```

![Claude Code status line on Windows 11 showing quota]({static}/images/i-fired-the-quota-robot-and-hired-a-json-file/windows11.png)

## Windows was the hard part, obviously

Here's the trap: Claude Code on Windows runs your status line command
through Git Bash. Git Bash does not ship `jq`. Every bash-based quota tool
therefore opens with "step 1: install jq into Git Bash," which is the
step where half your Windows users quietly close the tab.

So the Windows side is pure PowerShell — `Invoke-RestMethod` and
`ConvertFrom-Json`, both built in, zero installs. Cold start is roughly
100–200 ms on PowerShell 7 and 300–500 ms on 5.1 (measured casually on my
machine; don't build a datacenter around it).

And because both libraries write the *same* cache file in the same format,
Windows and WSL2 share one quota cache. Native session fetches it, WSL2
session reads it for free. As far as I can tell nobody else in this
particular sandbox handles the dual-environment case, which is either a
market gap or a sign that everyone else has healthier work habits.

## Today's episode: the warning sign that rendered as doubt

This very evening, my status line said:

```
5h:29%? ~50m
```

A question mark. Was the data stale, or was the stale-marker glyph broken?

Both. Obviously both.

The data *was* stale — fetches had been failing for a while and the
library was honestly flagging it, exactly as designed. But the flag is
`⚠`, and what I got was `?`, because when PowerShell's stdout is captured
through a pipe — which is precisely how Claude Code runs your status line —
it encodes output with the OEM code page. A character set standardized
when the fax machine was aspirational technology. It has no `⚠`, so .NET
shrugged and substituted a question mark, turning a warning into an
existential one.

The fix is one line at the top of the status line script:

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

That warning glyph had been silently eaten on every Windows install since
day one, and nobody noticed, because noticing required your quota fetch to
fail *and* your typography standards to be unreasonably high at the same
time. Mine were. It's fixed in v1.0.0.

## v1.0.0, a plugin, and other signs of adulthood

The repo now has an actual tagged release, and it's installable as a
Claude Code plugin — the repo is its own marketplace:

```
/plugin marketplace add aweussom/claude-code-quota
/plugin install claude-code-quota@aweussom
```

That gives you a `/quota` skill immediately: ask Claude Code for your
quota and it reads the cache and tells you, including how stale the data
is and which version wrote it. Plugins can't touch your `statusLine`
setting (that's yours, in `settings.json`), so for the permanent display
you run the installer once:

```powershell
# Windows
pwsh -ExecutionPolicy Bypass -File .\install.ps1
```

```bash
# Linux / WSL2
bash install.sh
```

Or ask Claude to "set up my quota statusline" after installing the plugin,
and the skill walks it through the whole thing. We live in an age where
the installation instructions can install themselves. I have decided not
to think about this too hard.

## The honest part

- The endpoint is **undocumented**. The library pins a beta header
  (`oauth-2025-04-20`), and Anthropic can change any of it on any given
  Tuesday. If that happens, the status line degrades to showing stale data
  with a warning glyph — a *visible* one now — and I bump the header.
  That's the deal. That's also why there's finally a version number in the
  cache file.
- Claude Code has `/usage` built in, and it's fine. If you check your
  quota twice a week, you don't need me. This tool is for the people who
  want the number *continuously in view* without a daemon, across Windows
  and WSL2 at once.
- If what you actually want is cost analytics — tokens, models, spend over
  time — [ccusage](https://github.com/ryoppippi/ccusage) is genuinely
  excellent and you should use it. Different job.
- Not affiliated with Anthropic. They just make the thing I keep running
  out of.

## Things I learned

1. Before building a robot to read a number off a screen, spend one hour
   checking whether the number is available as a number.
2. Fresh-with-a-timestamp beats fresh-on-demand for anything a status
   line does. Return the old value, refresh in the background, and nobody
   ever waits.
3. If your output can contain anything invented after 1987, set your
   encoding explicitly. The OEM code page outlives us all.

## The repo

[aweussom/claude-code-quota](https://github.com/aweussom/claude-code-quota)
— MIT licensed, no dependencies on Windows, `jq` and `curl` on Linux.
Star it if you too have been personally victimized by Claude rate limits,
or if you just enjoy watching a warning glyph render correctly.

The robot's repo stays up as a monument. We do not delete our origin
stories; we link to them sheepishly.

---

*The author is a Systems Specialist who does not work in software
development. His Claude quota is now read by a cache file at a total cost
of zero parameters, and he has redirected the 235 billion he saved toward
asking Claude why the quota is always at 68%. He is not expecting a
satisfying answer.*
