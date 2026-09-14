# How Claude Saved My Marriage

A fake conference keynote, in the spirit of Reggie Watts' TED talk: total speaker confidence, a story that almost makes sense, and a psychedelic detour in the middle.

Marion built a wedding-planning website by describing it to an AI at three in the morning. Her fiancée Léa never wanted to learn to code. It turns out there was never a door, only a curtain.

**Watch it:** https://frenchcommando.github.io/wedding-ai/

## What's here

| Path | What it is |
|---|---|
| `SCRIPT.md` | The talk, with stage directions and slide cues. |
| `keynote.html` | The live deck. Press Play and it runs the slides with the spoken lines as captions. Arrow keys and space to drive it by hand. |
| `keynote.mp4` | The narrated 1080p video. Not committed; rendered by CI and by `render/`. |
| `render/` | The pipeline that turns the deck into the video. See its README. |

## How the video is made

Every push to `main` runs the workflow in `.github/workflows/render.yml`:

1. Reads the spoken lines out of `keynote.html`.
2. Synthesizes each line with the Windows built-in voice, one clip per line, and measures it.
3. Applies the sound design: hall slap on every line, and on the loop-pedal slide a long delay, pitch drift, a stacked self-loop of "There's no door", and a beat.
4. Plays the deck in headless Chrome with each slide timed to its clip, and screencasts it.
5. Muxes frames and audio with ffmpeg.

The result is uploaded as the `keynote` build artifact on the run, and the deck is deployed to GitHub Pages.

The CI runner only has English voices. A local render on a machine with the French voice installed pronounces Marion and Léa properly.
