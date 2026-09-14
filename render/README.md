# Rendering keynote.mp4

Turns `../keynote.html` into a narrated 1080p video. Windows only (uses the built-in SAPI voice).

```
npm install                      # puppeteer-core, drives the installed Chrome
python -m venv venv && venv\Scripts\pip install imageio-ffmpeg
node extract.js                  # out/beats.json — the spoken lines, read from SLIDES in keynote.html
powershell -File tts.ps1         # out/voice/NN.wav + out/timing.json — one clip per line, measured
venv\Scripts\python fx.py        # out/fx/NN.wav — delay, pitch drift, the stacked loop; timing.json updated
node record.js                   # out/video/stage.mp4 — screencast piped into ffmpeg at 30 fps, slides timed to the clips
venv\Scripts\python encode.py    # out/mix/*.wav then ../keynote.mp4 — narration + beat bed, muxed onto the video
node snap.js 4 3                 # out/snaps/s4b3.png — one still of the stage view, for checking a slide
```

`out/` layout: `beats.json`, `timing.json`, `voice/`, `fx/`, `mix/`, `video/`, `snaps/`. All of it is regenerated; none is committed.

Change the talk in `keynote.html` (the `SLIDES` array), then rerun from `extract.js`.
Voice, rate and the 0.6 s pause after each line are set in `tts.ps1`; the pause is mirrored in `encode.py`.
