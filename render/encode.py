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
run(
    "-f", "concat", "-safe", "0", "-i", str(OUT / "frames.txt"),
    "-i", str(OUT / "narration.wav"),
    "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-crf", "20", "-preset", "medium",
    "-c:a", "aac", "-b:a", "160k", "-shortest",
    str(Path(__file__).parent.parent / "keynote.mp4"),
)
print("wrote keynote.mp4")
