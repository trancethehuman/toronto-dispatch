#!/usr/bin/env python3
"""Cut the trailer from the footage scripts/capture_trailer.py recorded.

Three parts on the game's own music: the city and the story on the title
theme (120 BPM, cuts every two-second bar), the work on the rest of the
title theme, and the trouble on the chase theme (160 BPM, cuts every
one-and-a-half-second bar), then the logo. Game frames are only cropped and
scaled by whole numbers (nearest neighbour); three presentations are used:
letterbox (a 160 x 67 strip at 12x, a place caption under it), full (a
160 x 90 strip at 12x, edge to edge) and screen (the whole 160 x 144 frame
at 7x on a blurred copy of itself, so the HUD and radio strip read). Cards
are set in the game's own font (scripts/ui_art.py). Sound effects recorded
with each shot sit under the music in the last part; the mix is normalised
to -14 LUFS.

  make_trailer.py [--footage project/build/trailer] [--output .../toronto-dispatch-trailer.mp4] [--preview DIR]

Requires numpy, Pillow and ffmpeg.
"""
import argparse
from pathlib import Path
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ui_art  # noqa: E402

GAME = Path(__file__).resolve().parents[1]
W, H, FPS, RATE = 1920, 1080, 60, 48000
WHITE, GOLD, GREY = (244, 240, 230), (240, 176, 48), (150, 150, 160)
TITLE_BAR, CHASE_BAR = 2.0, 1.5
CHASE_AT = 64.0  # the title theme's 32 bars

# (seconds, kind, args). Kinds: letterbox/full/screen (clip, first frame,
# crop row or caption), card (lines), logo. Keys: fade_in, fade_out, flash, sfx.
T, C = TITLE_BAR, CHASE_BAR
TIMELINE = [
    # The city, on the title theme.
    (2 * T, "letterbox", dict(clip="title", at=60, y0=34, fade_in=1.0)),
    (T, "card", dict(lines=[("TORONTO.", 16, WHITE)])),
    (T, "letterbox", dict(clip="front_golden", at=100, y0=30, caption="FRONT ST, UNION STATION")),
    (T, "letterbox", dict(clip="chinatown_walk", at=60, y0=26, caption="CHINATOWN, SPADINA AND DUNDAS")),
    (T, "letterbox", dict(clip="queen_rain", at=60, y0=16, caption="QUEEN ST, THE 501 IN THE RAIN")),
    (T, "letterbox", dict(clip="high_park_drive", at=100, y0=30, caption="PARKSIDE DR, HIGH PARK")),
    (T, "letterbox", dict(clip="king_night", at=100, y0=30, caption="KING ST AFTER DARK")),
    (2 * T, "screen", dict(clip="opening_radio", at=270)),
    (T, "letterbox", dict(clip="danforth", at=100, y0=30, caption="THE DANFORTH AT DAWN")),
    (T, "letterbox", dict(clip="harbour_swim", at=60, y0=40, caption="THE TORONTO ISLANDS")),
    (2 * T, "screen", dict(clip="opening_radio", at=555)),
    (2 * T, "screen", dict(clip="opening_radio", at=875)),
    # The work.
    (T, "card", dict(lines=[("WIN THE FESTIVAL CONTRACT.", 7, WHITE), ("OR LOSE THE DEPOT.", 7, GOLD)])),
    (T, "screen", dict(clip="delivery", at=100)),
    (T, "full", dict(clip="delivery", at=700, y0=20)),
    (T, "screen", dict(clip="delivery", at=850)),
    (T, "screen", dict(clip="cn_enter", at=80)),
    (T, "screen", dict(clip="cn_ride", at=60)),
    (T, "screen", dict(clip="cn_desk", at=10)),
    (T, "screen", dict(clip="ago_card", at=280)),
    (T, "full", dict(clip="rom_walk", at=40, y0=10)),
    (T, "full", dict(clip="eaton_walk", at=60, y0=20)),
    (T, "full", dict(clip="dragon_walk", at=60, y0=20)),
    (T, "full", dict(clip="byte_walk", at=60, y0=20)),
    (T, "screen", dict(clip="gallery", at=650)),
    (T, "screen", dict(clip="busker", at=40)),
    (T, "screen", dict(clip="neighbour", at=30)),
    (T, "screen", dict(clip="goose", at=30, fade_out=0.25)),
    # The trouble, on the chase theme.
    (2 * C, "card", dict(lines=[("SHE SAYS NO?", 9, WHITE), ("WE'LL SEE.", 9, WHITE), ("VANCE, RUSHLY", 4, GOLD)],
                         flash=0.15)),
    (C, "full", dict(clip="heli_chase", at=0, y0=20, sfx=True)),
    (C, "full", dict(clip="cops_on_foot", at=130, y0=10, sfx=True)),
    (C, "full", dict(clip="night_chase", at=100, y0=20, sfx=True)),
    (C, "screen", dict(clip="street_fight", at=200, sfx=True)),
    (C, "full", dict(clip="haymaker", at=10, y0=20, sfx=True)),
    (C, "full", dict(clip="pistol", at=60, y0=20, sfx=True)),
    (C, "full", dict(clip="tank", at=180, y0=20, sfx=True)),
    (C, "full", dict(clip="drift", at=120, y0=20, sfx=True)),
    (C, "full", dict(clip="shark", at=80, y0=20, sfx=True)),
    (C, "screen", dict(clip="heli_chase", at=150, sfx=True)),
    (C, "full", dict(clip="heli_chase", at=230, y0=20, sfx=True)),
    (C, "screen", dict(clip="spray", at=200, sfx=True)),
    (C, "full", dict(clip="pursuit", at=140, y0=20, sfx=True)),
    (C, "full", dict(clip="run", at=20, y0=20, sfx=True)),
    (2 * C, "card", dict(lines=[("SHOW THEM WHO", 9, WHITE), ("DELIVERS THIS CITY.", 9, WHITE), ("MARGO", 4, GOLD)])),
    # The logo.
    (5.0, "logo", dict(clip="title", at=200, flash=0.25)),
    (4.0, "card", dict(lines=[("A HOMEBREW GAME FOR", 4, GREY), ("MODRETRO CHROMATIC", 6, WHITE),
                              ("AND GAME BOY COLOR", 6, WHITE), ("", 3, GREY),
                              ("GITHUB.COM/TRANCETHEHUMAN/TORONTO-DISPATCH", 3, GREY)], fade_in=0.4, fade_out=1.5)),
]


class Footage:
    def __init__(self, folder):
        self.folder = folder
        self.frames, self.audio = {}, {}

    def clip(self, name):
        if name not in self.frames:
            self.frames[name] = np.load(self.folder / f"{name}.npz")["frames"]
        return self.frames[name]

    def frame(self, name, i):
        f = self.clip(name)
        return f[min(i, len(f) - 1)]

    def sound(self, name):
        if name not in self.audio:
            with wave.open(str(self.folder / f"{name}.wav")) as w:
                a = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2)
            self.audio[name] = a.astype(np.float32) / 32768
        return self.audio[name]


def text_image(lines, width=W):
    """Lines of (text, scale, colour) in the game's 8 x 8 font, centred."""
    rows = []
    for text, scale, colour in lines:
        line = np.zeros((8 * scale, max(1, 8 * scale * len(text)), 3), np.uint8)
        for n, ch in enumerate(text):
            glyph = np.array([[c == "#" for c in row] for row in ui_art.font_rows(ch if ch in ui_art.FONT else " ")])
            block = np.kron(glyph, np.ones((scale, scale), bool))
            line[:, n * 8 * scale:(n + 1) * 8 * scale][block] = colour
        rows.append((line, scale))
    gap = lambda s: 3 * s  # noqa: E731
    total = sum(r.shape[0] for r, _ in rows) + sum(gap(s) for _, s in rows[:-1])
    out = np.zeros((total, width, 3), np.uint8)
    y = 0
    for line, scale in rows:
        x = (width - line.shape[1]) // 2
        out[y:y + line.shape[0], max(0, x):max(0, x) + line.shape[1]] = line[:, :min(line.shape[1], width)]
        y += line.shape[0] + gap(scale)
    return out


def scale_up(img, k):
    return np.repeat(np.repeat(img, k, axis=0), k, axis=1)


def letterbox(frame, y0, caption=None):
    out = np.zeros((H, W, 3), np.uint8)
    out[138:138 + 804] = scale_up(frame[y0:y0 + 67], 12)
    if caption:
        t = text_image([(caption, 3, GREY)])
        out[1000:1000 + t.shape[0]] = np.maximum(out[1000:1000 + t.shape[0]], t)
    return out


def full(frame, y0):
    return scale_up(frame[y0:y0 + 90], 12)


def screen(frame):
    small = Image.fromarray(frame).resize((40, 36), Image.BILINEAR).filter(ImageFilter.GaussianBlur(1.2))
    bg = np.asarray(small.resize((W, int(W * 144 / 160)), Image.BILINEAR))
    top = (bg.shape[0] - H) // 2
    out = (bg[top:top + H].astype(np.float32) * 0.32).astype(np.uint8)
    x, y = (W - 1120) // 2, (H - 1008) // 2
    out[y - 6:y + 1008 + 6, x - 6:x + 1120 + 6] = 12
    out[y:y + 1008, x:x + 1120] = scale_up(frame, 7)
    return out


def card(lines):
    out = np.zeros((H, W, 3), np.uint8)
    t = text_image(lines)
    y = (H - t.shape[0]) // 2
    out[y:y + t.shape[0]] = t
    return out


def render(footage, kind, args, i):
    if kind == "card":
        return card(args["lines"])
    f = footage.frame(args["clip"], args["at"] + i)
    if kind == "letterbox":
        return letterbox(f, args["y0"], args.get("caption"))
    if kind == "full":
        return full(f, args["y0"])
    if kind == "screen":
        return screen(f)
    if kind == "logo":
        return full(f, 0)
    raise ValueError(kind)


def shade(img, i, n, args):
    fi, fo, fl = (round(args.get(k, 0) * FPS) for k in ("fade_in", "fade_out", "flash"))
    level = 1.0
    if fi and i < fi:
        level = min(level, i / fi)
    if fo and i >= n - fo:
        level = min(level, (n - i) / fo)
    out = img.astype(np.float32) * level if level < 1 else img
    if fl and i < fl:
        k = 1 - i / fl
        out = out.astype(np.float32) * (1 - k) + 255 * k
    return np.asarray(out, np.uint8) if out is not img else img


def soundtrack(footage, total):
    def song(name):
        with wave.open(str(footage.folder / f"music-{name}.wav")) as w:
            return np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).astype(np.float32) / 32768

    title, chase = song("title"), song("chase")
    out = np.zeros((int(total * RATE) + RATE, 2), np.float32)

    def lay(src, at, start, length, gain=1.0, fade_in=0.0, fade_out=0.0):
        a, n = int(at * RATE), int(length * RATE)
        seg = src[int(start * RATE):int(start * RATE) + n].copy()
        env = np.ones(len(seg), np.float32)
        if fade_in:
            k = min(len(seg), int(fade_in * RATE))
            env[:k] = np.linspace(0, 1, k)
        if fade_out:
            k = min(len(seg), int(fade_out * RATE))
            env[-k:] = np.minimum(env[-k:], np.linspace(1, 0, k))
        out[a:a + len(seg)] += seg * env[:, None] * gain

    end_chase = total - 9.0
    lay(title, 0.0, 0.0, CHASE_AT, 0.9, fade_in=0.5, fade_out=0.15)
    lay(chase, CHASE_AT, 0.0, end_chase - CHASE_AT + 1.5, 0.8, fade_out=1.5)
    lay(title, end_chase, 0.0, total - end_chase, 0.75, fade_in=0.2, fade_out=3.0)
    t = 0.0
    for seconds, kind, args in TIMELINE:
        if args.get("sfx"):
            fx = footage.sound(args["clip"])
            per = len(fx) / len(footage.clip(args["clip"]))
            start = int(args["at"] * per)
            seg = fx[start:start + int(seconds * RATE)]
            a = int(t * RATE)
            out[a:a + len(seg)] += seg * 2.4  # effects-only output is quiet
        t += seconds
    peak = np.abs(out).max()
    if peak > 0.95:
        out *= 0.95 / peak
    return (out[:int(total * RATE)] * 32767).astype(np.int16)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--footage", type=Path, default=GAME / "project/build/trailer")
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--preview", type=Path, default=None, help="write one still per shot instead of the video")
    args = parser.parse_args()
    footage = Footage(args.footage)
    total = sum(s for s, _, _ in TIMELINE)
    if args.preview:
        args.preview.mkdir(parents=True, exist_ok=True)
        for n, (seconds, kind, a) in enumerate(TIMELINE):
            frames = round(seconds * FPS)
            Image.fromarray(shade(render(footage, kind, a, frames // 2), frames // 2, frames, a)).resize(
                (W // 3, H // 3), Image.NEAREST).save(args.preview / f"{n:02d}-{kind}-{a.get('clip', 'card')}.png")
        print(f"{len(TIMELINE)} stills, {total:.1f} s")
        return
    output = args.output or args.footage / "toronto-dispatch-trailer.mp4"
    audio_path = args.footage / "trailer-audio.wav"
    with wave.open(str(audio_path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(soundtrack(footage, total).tobytes())
    ffmpeg = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
         "-i", "-", "-i", str(audio_path), "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
         "-tune", "animation", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
         "-movflags", "+faststart", "-shortest", str(output)],
        stdin=subprocess.PIPE)
    written = 0
    for seconds, kind, a in TIMELINE:
        frames = round(seconds * FPS)
        still = render(footage, kind, a, 0) if kind == "card" else None
        for i in range(frames):
            img = still if still is not None else render(footage, kind, a, i)
            ffmpeg.stdin.write(shade(img, i, frames, a).tobytes())
            written += 1
    ffmpeg.stdin.close()
    if ffmpeg.wait():
        raise SystemExit("ffmpeg failed")
    print(f"Wrote {output}: {written} frames, {written / FPS:.1f} s")


if __name__ == "__main__":
    main()
