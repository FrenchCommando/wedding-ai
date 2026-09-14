"""Sound design on the narration clips. Runs after tts.ps1, before record.js.

Reads out/timing.json, writes out/xNN.wav, rewrites timing.json so slide
timings follow the processed lengths. Slide 5 (index 4) is the loop-pedal
moment: pitch drift, delay, a stacked loop of "There's no door", and a beat.
"""
import json
import subprocess
from pathlib import Path

import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
OUT = Path(__file__).parent / "out"
SR = 22050
LOOP_SLIDE = 4
PAD = 0.6  # matches tts.ps1


def run(*args):
    subprocess.run([FF, "-y", "-loglevel", "error", *args], check=True)


def duration(p):
    return ((p.stat().st_size - 44) / 2) / SR


def pitch(semitones):
    r = 2 ** (semitones / 12)
    return f"asetrate={SR * r},aresample={SR},atempo={1 / r:.4f}"


STAGE = "aecho=0.9:0.3:60:0.18"  # every line: a little conference-hall slap
TRIP = "aecho=0.8:0.75:140|290|450:0.45|0.3|0.18"  # slide 5: long stacked delay


def main():
    timing = json.loads((OUT / "timing.json").read_text("utf-8-sig"))
    for t in timing:
        src = Path(t["file"])
        dst = OUT / f"x{t['i']:02d}.wav"
        text = t["t"]
        if text.startswith("["):
            run("-i", str(src), str(dst))
        elif t["s"] == LOOP_SLIDE and text.startswith("There's no door"):
            # stack the phrase: dry, then -3, -7, -12 semitones, each delayed and quieter
            layers = [
                f"[0:a]{TRIP}[a0]",
                f"[0:a]{pitch(-3)},adelay=900,volume=0.75,{TRIP}[a1]",
                f"[0:a]{pitch(-7)},adelay=1800,volume=0.6,{TRIP}[a2]",
                f"[0:a]{pitch(-12)},adelay=2700,volume=0.5,{TRIP}[a3]",
                "[a0][a1][a2][a3]amix=inputs=4:normalize=0,apad=pad_dur=1.2[out]",
            ]
            run("-i", str(src), "-filter_complex", ";".join(layers), "-map", "[out]", str(dst))
        elif t["s"] == LOOP_SLIDE:
            drift = -2 if t["j"] >= 3 else -1
            run("-i", str(src), "-af", f"{pitch(drift)},{TRIP}", str(dst))
        else:
            run("-i", str(src), "-af", STAGE, str(dst))
        t["file"] = str(dst)
        t["dur"] = round(duration(dst) + PAD, 3)
    (OUT / "timing.json").write_text(json.dumps(timing, indent=1), "utf-8")
    print("fx done; total", round(sum(t["dur"] for t in timing), 1), "s")


if __name__ == "__main__":
    main()
