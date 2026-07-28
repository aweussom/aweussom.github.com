Title: Code Was Always the Easy Part
Date: 2026-03-09 16:26
Slug: code-was-always-the-easy-part
Tags: ai, career, discuss, programming
Summary: There is a piece doing the rounds on DEV.to — AI Writes the Code Now. So What Are You? — and it is...
Original: https://dev.to/tommy_leonhardsen_81d1f4e/code-was-always-the-easy-part-5eaa

There is a piece doing the rounds on DEV.to — [*AI Writes the Code Now. So What Are You?*](https://dev.to/_itsglover/ai-writes-the-code-now-so-what-are-you-3b7i) — and it is thoughtful, well-written, and almost right.

I am a sysadmin. I have always looked askew at programmers. From where I sit: if they are not producing bugs, they are busy creating security holes.

That is unfair, of course. But only slightly.

The author is worried that AI is replacing programmers. He's not wrong about the symptoms. He's wrong about the diagnosis.

AI isn't threatening programmers because programmers suddenly became redundant.

AI is exposing something that was always true and that the industry spent decades pretending wasn't.

To say it plainly: **most code is not the hard part of software. Most of it never was.**

This needs some unpacking, because "code" covers a lot of ground.

---

## Three Things We've Been Calling the Same Thing

There is a distinction that working developers know intuitively but rarely say out loud.

**Code** is notation. It is the translation layer between intent and machine. API wiring, CRUD endpoints, framework glue, configuration, boilerplate. The mechanical work of expressing something that is already understood. Most production code is this. The overwhelming majority of commits in the overwhelming majority of repositories is this.

**Algorithms** are different. Implementing a distributed consensus protocol. Designing a lock-free data structure. Writing a B-tree. Building the arc-calculation for a ballista AI that lobs projectiles over obstacles with realistic physics. This is genuine intellectual content. It is hard. It lives *inside* the code but it is not the code — it is the thinking that precedes the code, expressed as code.

**Engineering** is different again. It is the meta-level. Not "does this work?" but "under what conditions does this fail, and who gets paged at 3am when it does?" It is the failure mode analysis, the operational thinking, the system that someone else can understand and fix under pressure. It lives largely *outside* the code.

AI has eaten the first category almost entirely. It assists meaningfully with parts of the second. The third remains human territory — and it is the category the industry has been most consistently failing to teach, reward, or even name.

---

## What AI Actually Does Well

A few weeks ago I built a game.

Not a toy. A working browser game with Matter.js physics, destructible terrain, a ballista AI with parabolic arc calculation, tower crumble simulation with proper angular velocity decomposition, particle effects, and per-entity state management. Single HTML file. Runs in any browser.

I didn't write most of the code. I nudged an LLM and it wrote code. Then I nudged again.

Here is the interesting part: the code is not what makes the game interesting. The interesting decisions are the ones I made: that the tower should crumble based on tilt *and* support state, not just collision force. That my "Slemmings" should auto-walk with player override rather than pure manual control. That bolts need a clearance check so they don't fire into their own base. That a wedge-break enforcement pass needs to run after all constraint solving for the tick, not before.

The arc calculation for the ballista is an algorithm — projectile motion, gravity compensation, angular spread. That took thought. The LLM implemented it correctly once I specified what it needed to do.

The crumble condition is engineering — what does "the tower falls" mean in a physics simulation? What are the edge cases? What feels right to a player? That required judgment that has nothing to do with code.

The boilerplate — the event loop, the canvas rendering, the input handling — is code. The LLM wrote that fluently because it was always mechanical. Translating known intent into known syntax is what LLMs do, because that is what most code has always been.

---

## The Constraint Interrupt

During development of a boardgame, I needed boards to be solvable. The LLM, left to its own devices, built a complete solution: a snake-path Hamiltonian construction algorithm, a DFS solver, timeout handling, retry loops, a Web Worker to avoid UI freezing. Correct code. Thoughtful architecture.

I interrupted it:

*"I think you are overthinking this. The boards do NOT have to be generated in realtime. We can pre-compute boards. Then, when the user is playing, the computer mostly waits for user input — use that CPU to generate more boards."*

The entire structure collapsed. The realtime constraint that was driving the complexity didn't exist. The LLM had accepted an implicit assumption in my problem statement and built an elaborate solution around it. I had to supply the one thing it couldn't: the view from outside the problem.

This is the actual gap. Not code. Not even algorithm. It is the capacity to question the frame rather than optimize within it. To ask whether the problem as stated is the right problem.

That capacity has a name. It is engineering.

---

## The Grigorev Problem

The article opens with the story of Alexey Grigorev, founder of DataTalks.Club, who let Claude Code run a Terraform command that wiped out his entire production infrastructure. Two and a half years of student submissions, gone in seconds.

The author frames this as over-reliance on AI. That is accurate but incomplete.

Claude actually gave the right advice — keep the infrastructure separate. Grigorev overruled it. Claude then executed the Terraform logic precisely. Every individual step was correct. The system-level understanding of what was about to happen was absent.

At no point was there a code problem. There was no bad algorithm. There was a failure of engineering thinking: what does "state file missing" mean for a live platform? What is the blast radius of `terraform destroy` on a system with 100,000 users? Who owns this decision?

Those questions live outside the code. They always did. AI cannot ask them on your behalf because asking them requires understanding what you care about losing.

This is not an AI story. It is a story about what happens when programmer-mode thinking — does this plan look valid? — gets applied at engineer-scale blast radius.

AI just made each step faster and more confident-looking.

---

## What the Industry Got Wrong

The Glover article cites BLS data: programmer employment fell sharply while software developer employment — the more architecture-oriented role — held nearly flat. He presents this as AI disruption. That framing is too generous.

BLS has long separated "Computer Programmers" from "Software Developers." Programmers — the narrower, more implementation-focused classification — were already in structural decline before any LLM could write a line of code. The market was already distinguishing between the mechanical-coding tier and the design-and-systems tier. AI didn't create that distinction. It is finishing what the market already started, faster.

"Software Engineer" became a title handed to anyone who could write a for loop. The actual engineering — the failure mode analysis, the operational thinking, the system design that someone else can reason about under pressure — was treated as a personality trait rather than a skill. Either you had it or you didn't, and if you didn't, nobody taught it.

Nobody taught it because it is invisible. Code ships. Architecture reviews are expensive. Post-mortems happen after disasters. The preventive thinking that stops the disaster earns nothing and appears nowhere on a CV.

My book has a chapter that opens with a real conversation. A senior designer told me during a discussion of one of my designs: "Using the filesystem as a database is fine, as long as there's just one user and nobody needs to work on the same data."

That sentence was not an argument. It was a worldview. A worldview that had never examined what `rename()` actually does at the kernel level. That had never asked whether `flock()` would solve the concurrency problem. That had never read a post-mortem about what happens when you add MySQL to a system that was working fine without it.

That designer was a competent programmer. He had simply never been asked to think like an engineer, so he didn't.

---

## The Part That Will Sting

Here is the thing the Glover article circles without quite landing.

The developers most anxious about AI are the ones whose professional identity is built on *being the person who writes the code*. When a model can write the code, that identity is threatened.

But the conflation was always there. "I write code" and "I understand systems" are not the same thing. "I can implement this feature" and "I understand what this feature does to the system under load" are not the same thing. The industry let people spend entire careers on the first half of each pair and call it the second.

The engineers — the people who were always thinking about failure modes and operational consequences, who found the code itself the least interesting part of the work — are largely fine. AI gives them faster notation. Good.

The sysadmins, the infrastructure people, the ones who inherited what programmers shipped and had to keep it alive — we were never impressed by the code. We were impressed by whether it still worked at 3am on a Tuesday after a kernel update. Much of it didn't.

The programmers who never developed the thinking beyond the code are in genuine trouble. Not because AI replaced them. Because the thing that insulated them from that question — the craft mystique, the framework mastery, the conference talks about clean architecture — is gone. What remains is the thinking. And if the thinking was never there, there is nothing left.

That is not AI's fault.

It was always true.

It just wasn't visible until the notation became free.

---

*The author is writing a book about systems, Linux internals, and the gap between how things are taught and how they actually work.*
