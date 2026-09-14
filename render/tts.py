"""Narration with Microsoft's neural voices (edge-tts, no key needed), one clip per line.

Reads out/beats.json, writes out/voice/NN.wav (22050 Hz mono) and out/timing.json.
Bracketed stage directions become 2.5 s of silence. VOICE env var picks the voice;
the default is a French multilingual voice, so Marion speaks English with a French
accent and says Marion and Léa the French way.
"""
import asyncio
import json
import os
import subprocess
import wave
from pathlib import Path

import edge_tts
import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
OUT = Path(__file__).parent / "out"
VOICE = os.environ.get("VOICE", "fr-FR-VivienneMultilingualNeural")
RATE = os.environ.get("RATE", "-5%")
SR = 22050
PAD = 0.6
SILENCE = 2.5


def run(*args):
    subprocess.run([FF, "-y", "-loglevel", "error", *args], check=True)


def wav_seconds(p: Path) -> float:
    with wave.open(str(p)) as w:
        return w.getnframes() / w.getframerate()


async def speak(text: str, dst: Path):
    mp3 = dst.with_suffix(".mp3")
    await edge_tts.Communicate(text, VOICE, rate=RATE).save(str(mp3))
    run("-i", str(mp3), "-ar", str(SR), "-ac", "1", str(dst))
    mp3.unlink()


async def main():
    beats = json.loads((OUT / "beats.json").read_text("utf-8"))
    voice_dir = OUT / "voice"
    voice_dir.mkdir(parents=True, exist_ok=True)
    timing = []
    for i, b in enumerate(beats):
        dst = voice_dir / f"{i:02d}.wav"
        if b["t"].startswith("["):
            run("-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=mono", "-t", str(SILENCE), str(dst))
        else:
            text = b["t"].replace("“", '"').replace("”", '"').replace("’", "'").replace("—", ", ")
            await speak(text, dst)
        dur = wav_seconds(dst)
        timing.append({"i": i, "s": b["s"], "j": b["j"], "t": b["t"], "dur": round(dur + PAD, 3), "file": str(dst)})
        print(f"{i:02d} {dur:5.2f}s  {b['t'][:60]}")
    (OUT / "timing.json").write_text(json.dumps(timing, indent=1), "utf-8")
    print("voice:", VOICE, "total:", round(sum(t["dur"] for t in timing), 1), "s")


asyncio.run(main())
