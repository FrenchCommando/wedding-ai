# How Claude Saved My Marriage

A fake conference keynote, in the spirit of Reggie Watts' TED talk: total speaker confidence, a story that almost makes sense, and a psychedelic detour in the middle.

Marion built a wedding-planning website by describing it to an AI at three in the morning. Her fiancée Léa never wanted to learn to code. It turns out there was never a door, only a curtain.

**Watch it:** https://frenchcommando.github.io/wedding-ai/ — click **Stage**, then **Play**.

## Two views of the same deck

| View | URL | What you get |
|---|---|---|
| Plain | `/` | The slides fill the window. For presenting live. |
| Stage | `/?stage` | The deck on the big screen of a drawn auditorium: speaker at the lectern, audience, stage lights that follow the slide, camera cuts between wide, screen, three-quarter and lectern shots, a live bug and a lower third. This is what the video records. |

Both views narrate themselves when `narration.mp3` and `timing.js` sit next to the page. CI puts them there for GitHub Pages; the local render drops them next to `keynote.html`. Play, Prev, Next, space and the arrow keys all keep the audio in sync.

## What's here

| Path | What it is |
|---|---|
| `SCRIPT.md` | The talk, with stage directions and slide cues. |
| `keynote.html` | The deck, both views. The spoken lines live in its `SLIDES` array and are the single source for captions, narration and timing. |
| `keynote.mp4` | The narrated 1080p video. Not committed; rendered by CI and by `render/`. |
| `narration.mp3`, `timing.js` | Web narration, generated. Not committed. |
| `render/` | The pipeline that turns the deck into the video. See its README. |

## How the video is made

Every push to `main` runs the workflow in `.github/workflows/render.yml` on a Windows runner:

1. `extract.js` reads the spoken lines out of `keynote.html`.
2. `tts.py` synthesizes each line with a Microsoft neural voice through `edge-tts` (no key needed), one clip per line, and measures it.
3. `fx.py` applies the sound design: a hall slap on every line, and on the loop-pedal slide a long delay, pitch drift, a stacked self-loop of "There's no door", and a beat under it.
4. `record.js` plays the stage view in headless Chrome, each line timed to its clip, and pipes the screencast into ffmpeg at 30 fps.
5. `encode.py` mixes narration and beat, muxes them onto the video, and writes the web narration bundle.

The video is uploaded as the `keynote` build artifact on the run. The Pages job waits for it, then deploys the deck together with the narration.

The narrator is `fr-FR-VivienneMultilingualNeural`: Marion speaks English with a French accent and says Marion and Léa the French way. Same result locally and in CI. Override with the `VOICE` and `RATE` environment variables.
