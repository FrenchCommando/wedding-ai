"""Mix narration + beat bed and mux with out/video.mp4 into keynote.mp4. Run with render/venv (imageio-ffmpeg)."""
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
MIX = OUT / "mix"
(MIX / "padded").mkdir(parents=True, exist_ok=True)
padded = []
for t in timing:
    src = Path(t["file"])
    dst = MIX / "padded" / f"{t['i']:02d}.wav"
    run("-i", str(src), "-af", f"apad=pad_dur={PAD}", str(dst))
    padded.append(dst)
(MIX / "padded.txt").write_text("".join(f"file 'padded/{p.name}'\n" for p in padded))

run("-f", "concat", "-safe", "0", "-i", str(MIX / "padded.txt"), str(MIX / "narration.wav"))

# beat bed under the loop-pedal slide: 90 bpm kick + noise hat, faded in and out
LOOP_SLIDE = 4
start = sum(t["dur"] for t in timing if t["s"] < LOOP_SLIDE)
length = sum(t["dur"] for t in timing if t["s"] == LOOP_SLIDE)
beat = 60 / 90
kick = f"sin(2*PI*52*t)*exp(-10*mod(t,{beat}))"
hat = f"(random(0)-0.5)*exp(-60*mod(t+{beat / 2},{beat}))"
run(
    "-f", "lavfi", "-i", f"aevalsrc='{kick}*0.9+{hat}*0.25':s=22050:d={length:.2f}",
    "-af", f"afade=t=in:d=2,afade=t=out:st={length - 3:.2f}:d=3,volume=0.35",
    str(MIX / "bed.wav"),
)
run(
    "-i", str(MIX / "narration.wav"), "-i", str(MIX / "bed.wav"),
    "-filter_complex", f"[1:a]adelay={int(start * 1000)}|{int(start * 1000)}[b];[0:a][b]amix=inputs=2:normalize=0:duration=first",
    str(MIX / "mix.wav"),
)
run(
    "-i", str(OUT / "video" / "stage.mp4"), "-i", str(MIX / "mix.wav"),
    "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest",
    str(Path(__file__).parent.parent / "keynote.mp4"),
)
print("wrote keynote.mp4")

# web bundle: the same mix as MP3 plus the timings, so the deck can narrate itself on GitHub Pages
WEB = OUT / "web"
WEB.mkdir(exist_ok=True)
run("-i", str(MIX / "mix.wav"), "-c:a", "libmp3lame", "-b:a", "96k", str(WEB / "narration.mp3"))
slim = [{"s": t["s"], "j": t["j"], "dur": t["dur"]} for t in timing]
(WEB / "timing.js").write_text("window.TIMING=" + json.dumps(slim) + ";\n", "utf-8")
# also next to keynote.html so the page narrates itself when opened from disk (both gitignored)
import shutil
for f in ("narration.mp3", "timing.js"):
    shutil.copy(WEB / f, Path(__file__).parent.parent / f)
print("wrote out/web and copied next to keynote.html")
