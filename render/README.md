# Rendering keynote.mp4

Turns `../keynote.html` into a narrated 1080p video.

```
npm install                      # puppeteer-core, drives the installed Chrome
python -m venv venv && venv\Scripts\pip install imageio-ffmpeg edge-tts
node extract.js                  # out/beats.json — the spoken lines, read from SLIDES in keynote.html
venv\Scripts\python tts.py       # out/voice/NN.wav + out/timing.json — one neural-voice clip per line, measured
venv\Scripts\python fx.py        # out/fx/NN.wav — delay, pitch drift, the stacked loop; timing.json updated
node record.js                   # out/video/stage.mp4 — screencast piped into ffmpeg at 30 fps, slides timed to the clips
venv\Scripts\python encode.py    # out/mix/*.wav then ../keynote.mp4 — narration + beat bed, muxed onto the video
node snap.js 4 3                 # out/snaps/s4b3.png — one still of the stage view, for checking a slide
```

`out/` layout: `beats.json`, `timing.json`, `voice/`, `fx/`, `mix/`, `video/`, `snaps/`. All of it is regenerated; none is committed.

Change the talk in `keynote.html` (the `SLIDES` array), then rerun from `extract.js`.

The voice comes from Microsoft's neural text-to-speech via `edge-tts`, no key needed, network required.
Default is `fr-FR-VivienneMultilingualNeural`: English with a French accent, French names said properly.
Override with `VOICE=en-US-AvaMultilingualNeural` (or any from `edge-tts --list-voices`) and `RATE=-5%`.
The 0.6 s pause after each line is set in `tts.py` and mirrored in `fx.py` and `encode.py`.
