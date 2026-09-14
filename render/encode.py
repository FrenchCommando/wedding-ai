"""Mux recorded frames + narration into keynote.mp4. Run with render/venv (imageio-ffmpeg)."""
import json
import subprocess
from pathlib import Path

import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
OUT = Path(__file__).parent / "out"
PAD = 0.6  # seconds of silence appended to each clip; must match tts.ps1


def run(*args):
    subprocess.run([FF, "-y", "-loglevel", "error", *args], check=True)


timing = json.loads((OUT / "timing.json").read_text("utf-8-sig"))
padded = []
for t in timing:
    src = Path(t["file"])
    dst = OUT / f"p{t['i']:02d}.wav"
    run("-i", str(src), "-af", f"apad=pad_dur={PAD}", str(dst))
    padded.append(dst)
(OUT / "audio.txt").write_text("".join(f"file '{p.name}'\n" for p in padded))

run("-f", "concat", "-safe", "0", "-i", str(OUT / "audio.txt"), str(OUT / "narration.wav"))

# beat bed under the loop-pedal slide: 90 bpm kick + noise hat, faded in and out
LOOP_SLIDE = 4
start = sum(t["dur"] for t in timing if t["s"] < LOOP_SLIDE)
length = sum(t["dur"] for t in timing if t["s"] == LOOP_SLIDE)
beat = 60 / 90
kick = f"sin(2*PI*52*t)*exp(-10*mod(t,{beat}))"
hat = f"(random(0)-0.5)*exp(-60*mod(t+{beat / 2},{beat}))"
run(
    "-f", "lavfi", "-i", f"aevalsrc={kick}*0.9+{hat}*0.25:s={22050}:d={length:.2f}",
    "-af", f"afade=t=in:d=2,afade=t=out:st={length - 3:.2f}:d=3,volume=0.35",
    str(OUT / "bed.wav"),
)
run(
    "-i", str(OUT / "narration.wav"), "-i", str(OUT / "bed.wav"),
    "-filter_complex", f"[1:a]adelay={int(start * 1000)}|{int(start * 1000)}[b];[0:a][b]amix=inputs=2:normalize=0:duration=first",
    str(OUT / "mix.wav"),
)
run(
    "-f", "concat", "-safe", "0", "-i", str(OUT / "frames.txt"),
    "-i", str(OUT / "mix.wav"),
    "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-crf", "20", "-preset", "medium",
    "-c:a", "aac", "-b:a", "160k", "-shortest",
    str(Path(__file__).parent.parent / "keynote.mp4"),
)
print("wrote keynote.mp4")
