Title: Colour The Solstice: Turning Gestures Into a Living Neon Ecosystem
Date: 2026-06-06 08:48
Slug: colour-the-solstice-turning-gestures-into-a-living-neon-ecosystem
Tags: devchallenge, gamechallenge, gamedev
Summary: This is a submission for the June Solstice Game Jam.             What I Built   Colour The Solstice...
Original: https://dev.to/tommy_leonhardsen_81d1f4e/colour-the-solstice-turning-gestures-into-a-living-neon-ecosystem-3m7f

*This is a submission for the [June Solstice Game Jam](https://dev.to/challenges/june-game-jam-2026-06-03).*


![Play Colour The Solstice]({static}/images/colour-the-solstice-turning-gestures-into-a-living-neon-ecosystem/01.png)

## What I Built

**Colour The Solstice** is a scoreless psychedelic creation toy for the
browser.

Touch, click, hold, or sweep across the star field to release luminous beings.
They swim through trails of recursive colour, approach a young cosmic
Yggdrasil, and gradually become living vines around its trunk and branches.
Every arrival helps the tree grow.

There is no failure state, timer, score, final form, or correct way to play. My goal was to make a small digital place that feels calming, strange, and responsive: something between a game, a visualiser, and a living toy.

The June solstice suggested light, growth, seasonal transition, and Nordic
midsummer. The project's first centrepiece was therefore a Swedish maypole.
Unfortunately, its horizontal bar read too strongly as a cross once rendered in neon. That experiment evolved into **Yggdrasil**, the world tree from Norse mythology, which gave the creatures somewhere more organic to gather and grow.

The other major inspirations were:

- *flOw*, for low-control movement and a meditative rhythm.
- MilkDrop and Winamp visualisations, for recursive psychedelic colour.
- Jeff Minter's games, for unapologetic neon excess.
- *Townscaper*, for limited input that still produces pleasing results.

The central interaction is deliberately indirect. You influence a being, but you do not place it:

- A tap creates a balanced being.
- Holding or drawing a long stroke makes it longer and thicker.
- Stroke direction affects launch direction and spiral handedness.
- Stroke speed affects energy, swimming speed, movement, and colour.
- Long gestures tend to produce beings that embrace the trunk.

Yggdrasil interprets each arrival and finds somewhere for it to live.

![Colourful Yggdrasil]({static}/images/colour-the-solstice-turning-gestures-into-a-living-neon-ecosystem/02.png)

As the tree becomes crowded, the result develops into a small ecosystem. A
later arrival may eat the eldest being in a persistent clump. The eaten being flashes, falls slowly like a rocking leaf, and is consumed by the roots. Its colour then travels from the root tips into the trunk and toward the crown.

That mechanic began as a practical answer to visual crowding, but it became one of my favourite pieces of the project: a rendering problem turned into a tiny story about energy returning to the tree.

## Video Demo

<https://player.mux.com/I2UhEaxNd1HNiosmJkZY4vYaL5rsHXA4g3bgrbXJGh8>

## Code

The game is open source under the MIT License:

<https://github.com/aweussom/colourthesolstice>

- [Play the game](https://aweussom.github.io/colourthesolstice/)
- [Read the development log](https://github.com/aweussom/colourthesolstice/blob/main/DEVLOG.md)

There is no installation, package manager, server, build step, or network
dependency. The entire game can be downloaded and opened by double-clicking `index.html`.

## How I Built It

### One directly runnable HTML file

The complete runtime lives in one file: HTML, CSS, GLSL shaders, and plain
JavaScript.

I initially considered Three.js, but this experiment did not need a scene graph or general-purpose 3D engine. Native Canvas 2D and WebGL produced the effect I wanted while preserving the ability to run the game offline by opening one file.

The rendering pipeline has three layers:

1. An offscreen Canvas 2D scene draws stars, swimming beings, particles, and gesture previews.
2. Native WebGL feeds that scene through two alternating framebuffer textures.
3. A foreground Canvas 2D layer keeps Yggdrasil and its settled beings crisp.

The separation of the third layer was learned through failure. My first version sent the centrepiece through the feedback shader with everything else. It bloomed into a large grey capsule. Keeping the tree outside the recursive feedback preserved its structure while the surrounding colourscape remained fluid.

### Ping-pong framebuffer feedback

The psychedelic trails use a MilkDrop-style feedback loop. Each frame reads the previous framebuffer texture, applies a slight zoom, rotation, warp, fade, and hue shift, then adds the fresh Canvas 2D scene.

Two textures alternate between source and destination, allowing the image to retain a fading memory of earlier frames. A second shader tone-maps the result and adds the slow rainbow atmosphere behind the stars.

This is the technical core of the game's visual identity. The beings are
simple segmented shapes, but the feedback gives their movement weight and
history.

### Gestures become creature parameters

Pointer events record duration, distance, direction, and speed. Those values are mapped into body length, thickness, launch velocity, wiggle, energy, colour movement, and the geometry used when the being settles.

The goal was not precision drawing. A gesture provides intent, then the system responds with a related surprise.

Each being also receives a random seed. Save stores the gesture sequence and those seeds in `localStorage`, so Replay can rebuild the same creation
deterministically at half, normal, or double speed.

### Swimming bodies become living attachments

My first attachment system simply removed a swimmer and drew a mathematical helix around a branch. It worked technically, but the transition felt like the creature had died and been replaced by decoration.

The current system retains the original body points and progressively morphs them toward a densely sampled path around the tree. While morphing, the body continues swimming toward its landing point, so the tail flows inward rather than freezing in space.

After settling, beings still breathe, wave, migrate slowly, grow small fronds, and participate in absorption and crowding behavior. Multiple displaced, translucent layers make them read more like aurora or smoke than rigid coils.

### Growing only where the tree exists

One subtle bug let early creatures attach in empty space above the young tree. The simulation was using Yggdrasil's eventual full height, while the renderer showed only its current growth.

Attachment targets and creature aims now use the visibly grown trunk. This
fixed the floating beings and produced a welcome side effect: trunk-attached vines ride upward as the tree grows beneath them.

Tree growth itself is also continuous. Arrivals raise a target, and the roots, trunk, and branches ease toward it instead of appearing in discrete jumps.

## Growing a soundbed

The audio became another living system rather than a fixed soundtrack.
Short mono Ogg samples are embedded directly in the HTML and shaped through the Web Audio API. Drones repeat, pass through a long reverb and quiet echo, then crossfade automatically over twelve seconds. Gestures trigger seeded harps, percussion, or longer cinematic accents; attachment, absorption, population, and the root-to-crown ripple each change the soundbed in their own way. The result stays generative and responsive while preserving the game's offline, single-file form.

### Saving the colourscape

The lower-right controls can:

- Save the current gesture sequence locally.
- Replay it at three simulation speeds.
- Export the complete scene as PNG.
- Export the foreground tree on transparency.
- Record a silent WebM or MP4 through the browser's `MediaRecorder` support.

The transparent tree export exists because of another useful accident. The
first PNG implementation captured only the foreground canvas because WebGL's drawing buffer was no longer available when it was copied. That was wrong for a full screenshot, but useful for article graphics and compositing, so both exports now exist deliberately.

## Evolution and Lessons Learned

The game improved most when I treated visual problems as design prompts rather than only tuning defects.

- A maypole that read incorrectly became Yggdrasil.
- A centrepiece destroyed by feedback became a deliberate foreground layer.
- Abrupt helix replacement became a continuous creature-to-vine lifecycle.
- Empty-space attachments exposed disagreement between simulation and drawing.
- Branch clumping became consumption, leaf-fall, and root feeding.
- A broken PNG became a transparent artwork export.

The project also reinforced that procedural beauty depends on constraints. The player does not need unrestricted control; they need a readable relationship between gesture and consequence.

My design principles became:

- Creation matters more than competition.
- Every interaction should have a pleasing consequence.
- Control should remain limited but expressive.
- The world should stay alive when untouched without taking authorship away.
- Technical complexity must produce visible beauty or better interaction.
- Preserve successful accidents.

## AI-Assisted Development

I used coding agents during development, primarily OpenAI Codex and Claude Code. They helped inspect the single-file runtime, propose and implement changes, trace rendering and simulation bugs, update documentation, and run browser verification.

I remained responsible for the concept, visual direction, interaction choices, playtesting observations, and deciding which generated changes belonged in the game. Several of the most important iterations began with a subjective visual reaction such as "the attachment feels abrupt" or "the clump needs to become part of the world", followed by agent-assisted implementation and another playtest.

This entry does not use Google AI and is not submitted for the optional Google AI prize category. It is also not intended as an Alan Turing category entry.

## Possible Futures

The jam version is intentionally scoreless, but I have wondered what would
happen if several Yggdrasils shared one sky.

Competition could remain indirect: taller crowns might shade rivals, rhythmic waves of beings might encourage branch growth, and root systems might exchange energy. I think of it as reverse bonsai. Instead of pruning toward a shape, the player feeds toward one, while the tree continues to interpret.

That is a possible future, not a promise. For now, the scoreless toy is the project.

## Try It

[Grow your own Yggdrasil](https://aweussom.github.io/colourthesolstice)


Thank you for playing.
