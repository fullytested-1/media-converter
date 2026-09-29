import asyncio
import json
import subprocess
import uuid
from pathlib import Path
from config import FFMPEG_BIN, FFPROBE_BIN

def _run(*args):
    return subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)

def probe(path: str) -> dict:
    p = _run(FFPROBE_BIN, "-v", "error", "-show_entries", "format=duration:stream=codec_type", "-of", "json", path)
    if p.returncode != 0:
        raise RuntimeError(p.stderr[-1000:])
    return json.loads(p.stdout or "{}")

def duration(path: str) -> float:
    try:
        return float(probe(path).get("format", {}).get("duration", 0))
    except (TypeError, ValueError):
        return 0.0

def has_video(path: str) -> bool:
    return any(s.get("codec_type") == "video" for s in probe(path).get("streams", []))

async def run_ffmpeg(args: list[str], timeout: int = 3600):
    def work():
        p = _run(FFMPEG_BIN, "-y", *args)
        if p.returncode != 0:
            raise RuntimeError(p.stderr[-1800:])
    await asyncio.wait_for(asyncio.to_thread(work), timeout=timeout)

def out_path(suffix: str) -> str:
    return str(Path("output") / f"{uuid.uuid4().hex}{suffix}")

async def to_mp3(src):
    out = out_path(".mp3")
    await run_ffmpeg(["-i", src, "-vn", "-c:a", "libmp3lame", "-q:a", "2", out])
    return out

async def cut(src, start, end):
    ext = Path(src).suffix or ".mp4"
    out = out_path(ext)
    if has_video(src):
        await run_ffmpeg(["-ss", str(start), "-to", str(end), "-i", src, "-map", "0", "-c", "copy", out])
    else:
        await run_ffmpeg(["-ss", str(start), "-to", str(end), "-i", src, "-c", "copy", out])
    return out

async def change_speed(src, factor):
    out = out_path(Path(src).suffix or ".mp4")
    f = float(factor)
    if not 0.25 <= f <= 4:
        raise ValueError("Speed must be between 0.25x and 4x.")
    atempo = []
    remaining = f
    while remaining < 0.5:
        atempo.append("0.5"); remaining *= 2
    while remaining > 2:
        atempo.append("2"); remaining /= 2
    atempo.append(str(remaining))
    if has_video(src):
        vf = f"setpts={1/f:.8f}*PTS"
        await run_ffmpeg(["-i", src, "-vf", vf, "-filter:a", ",".join(f"atempo={x}" for x in atempo), "-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac", out])
    else:
        await run_ffmpeg(["-i", src, "-filter:a", ",".join(f"atempo={x}" for x in atempo), "-c:a", "libmp3lame", "-q:a", "2", out])
    return out

async def bass(src):
    out = out_path(Path(src).suffix or ".mp4")
    af = "bass=g=8:f=100:w=0.6"
    if has_video(src):
        await run_ffmpeg(["-i", src, "-af", af, "-c:v", "copy", "-c:a", "aac", out])
    else:
        await run_ffmpeg(["-i", src, "-af", af, "-c:a", "libmp3lame", "-q:a", "2", out])
    return out

async def resize(src, height):
    out = out_path(".mp4")
    await run_ffmpeg(["-i", src, "-vf", f"scale=-2:{height}", "-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac", out])
    return out

async def square(src):
    out = out_path(".mp4")
    vf = "crop=min(iw\,ih):min(iw\,ih):(iw-min(iw\,ih))/2:(ih-min(iw\,ih))/2,scale=720:720"
    await run_ffmpeg(["-i", src, "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac", out])
    return out

async def black_white(src):
    out = out_path(".mp4")
    await run_ffmpeg(["-i", src, "-vf", "hue=s=0", "-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac", out])
    return out

async def compress(src, level):
    out = out_path(".mp4" if has_video(src) else ".mp3")
    if has_video(src):
        crf = {"low": "28", "medium": "32", "high": "36"}[level]
        await run_ffmpeg(["-i", src, "-c:v", "libx264", "-crf", crf, "-preset", "veryfast", "-c:a", "aac", "-b:a", "96k", out])
    else:
        br = {"low": "128k", "medium": "96k", "high": "64k"}[level]
        await run_ffmpeg(["-i", src, "-c:a", "libmp3lame", "-b:a", br, out])
    return out

async def circle(src):
    out = out_path(".webm")
    vf = "crop=min(iw\,ih):min(iw\,ih):(iw-min(iw\,ih))/2:(ih-min(iw\,ih))/2,scale=512:512,format=yuva420p"
    await run_ffmpeg(["-i", src, "-vf", vf, "-c:v", "libvpx-vp9", "-auto-alt-ref", "0", "-c:a", "libopus", out])
    return out
