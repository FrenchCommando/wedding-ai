# Rendering keynote.mp4

Turns `../keynote.html` into a narrated 1080p video. Windows only (uses the built-in SAPI voice).

```
npm install                      # puppeteer-core, drives the installed Chrome
python -m venv venv && venv\Scripts\pip install imageio-ffmpeg
node extract.js                  # out/beats.json  — the spoken lines, read from SLIDES in keynote.html
powershell -File tts.ps1         # out/bNN.wav + out/timing.json — one clip per line, measured
node record.js                   # out/fNNNNN.jpg + out/frames.txt — screencast, slides timed to the clips
venv\Scripts\python encode.py    # ../keynote.mp4
```

Change the talk in `keynote.html` (the `SLIDES` array), then rerun from `extract.js`.
Voice, rate and the 0.6 s pause after each line are set in `tts.ps1`; the pause is mirrored in `encode.py`.
