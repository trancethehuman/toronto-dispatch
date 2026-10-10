#!/usr/bin/env python3
"""Cut the trailer from the footage scripts/capture_trailer.py recorded.

About fifty seconds on the game's chase theme (160 BPM, cuts on its beats),
ending on the title theme under the logo. Every shot starts just before the
thing it shows: in-points are found from the events capture_trailer.py logs
with each frame (the HUD message just posted, cash, stars, health, ammo, the
courier getting into a car), so the punch lands, the card pops or the shark
bites within the first beat. Fights and stunts are close-ups that follow
the courier; mechanics carry a short label.

Game frames are only cropped and scaled by whole numbers (nearest
neighbour). Presentations: letterbox (a 160 x 67 strip at 12x, the place
under it), full (160 x 90 at 12x), zoom (a smaller window at 16x or 20x that
follows the courier) and screen (the whole 160 x 144 frame at 6x on a
blurred copy of itself, so the HUD and radio strip read). Cards use the
game's own font (scripts/ui_art.py); the mix is normalised to -14 LUFS.

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
WHITE, GOLD, GREY, INK = (244, 240, 230), (240, 176, 48), (150, 150, 160), (16, 16, 24)
BEAT = 60 / 160  # the chase theme
# td.msg values (td_life.h) used as in-points.
CARJACK, SHOT_AT, CRASH, RESPRAYED, BITTEN, GOOSE, BRAWL, COUNTER, HAYMAKER, LIFT = 18, 19, 5, 33, 37, 41, 42, 43, 46, 51


def ev(field, value=None, offset=0):
    """An in-point: the first frame where field changes (to value, if
    given), plus offset frames."""
    return (field, value, offset)


# (beats, kind, args). Kinds: letterbox, full, zoom, screen, card, logo.
# args: clip, at (frame or ev(...)), y0 (crop row), z (zoom scale), dx/dy
# (zoom offset from the courier), label (label_top), caption, lines, flash,
# fade_in, fade_out, sfx.
TIMELINE = [
    # Cold open: the fight and the chase first.
    (3, "zoom", dict(clip="haymaker_fight", at=ev("msg", HAYMAKER, -34), z=20, dx=8, label="HAYMAKER", sfx=True)),
    (3, "zoom", dict(clip="street_fight", at=ev("msg", COUNTER, -20), z=20, dx=8, label="COUNTER", sfx=True)),
    (3, "zoom", dict(clip="carjack", at=0, z=20, dx=6, label="TAKE ANY CAR", sfx=True)),
    (3, "full", dict(clip="heli_chase", at=120, y0=14, label="OUTRUN THE POLICE", sfx=True)),
    (4, "logo", dict(clip="title", at=200, flash=0.12)),
    # The city.
    (2, "letterbox", dict(clip="front_golden", at=110, y0=30, caption="FRONT ST, UNION STATION")),
    (2, "letterbox", dict(clip="chinatown_walk", at=60, y0=26, caption="CHINATOWN, SPADINA AVE")),
    (2, "letterbox", dict(clip="queen_rain", at=40, y0=16, caption="QUEEN ST, THE 501")),
    (2, "letterbox", dict(clip="yonge_dundas", at=60, y0=30, caption="YONGE-DUNDAS")),
    (2, "letterbox", dict(clip="high_park_drive", at=100, y0=30, caption="HIGH PARK")),
    (2, "letterbox", dict(clip="king_night", at=100, y0=30, caption="KING ST AFTER DARK")),
    (2, "letterbox", dict(clip="danforth", at=100, y0=30, caption="THE DANFORTH")),
    (2, "letterbox", dict(clip="harbour_swim", at=60, y0=40, caption="THE TORONTO ISLANDS")),
    # The story.
    (4, "screen", dict(clip="opening_radio", at=330)),
    (4, "screen", dict(clip="opening_radio", at=650)),
    (4, "card", dict(lines=[("WIN THE FESTIVAL CONTRACT.", 7, WHITE), ("OR LOSE THE DEPOT.", 7, GOLD)])),
    (4, "card", dict(lines=[("SHE SAYS NO?", 9, WHITE), ("WE'LL SEE.", 9, WHITE), ("VANCE, RUSHLY", 4, GOLD)])),
    # The work.
    (2, "screen", dict(clip="delivery", at=8, label="TAKE THE JOB")),
    (2, "full", dict(clip="delivery", at=700, y0=20, label="DELIVER ACROSS TORONTO")),
    (3, "screen", dict(clip="delivery", at=ev("cash", None, -4))),
    (2, "screen", dict(clip="cn_enter", at=ev("msg", LIFT, 6), label="INTO THE CN TOWER")),
    (3, "screen", dict(clip="cn_ride", at=70, label="ELEVATOR TO 346 M")),
    (2, "screen", dict(clip="cn_desk", at=ev("cash", None, -2))),
    (3, "screen", dict(clip="ago_card", at=290, label="TALK TO ANYONE")),
    (2, "full", dict(clip="rom_walk", at=40, y0=10, caption="ROYAL ONTARIO MUSEUM")),
    (2, "full", dict(clip="eaton_walk", at=60, y0=20, caption="EATON CENTRE")),
    (2, "full", dict(clip="dragon_walk", at=60, y0=20, caption="DRAGON CITY MALL")),
    (2, "full", dict(clip="byte_walk", at=60, y0=20, caption="BYTE BARN")),
    (3, "screen", dict(clip="busker", at=ev("cash", None, 24), label="TIP THE BUSKERS")),
    (3, "screen", dict(clip="neighbour", at=ev("cash", None, 24), label="ASK AROUND")),
    (3, "screen", dict(clip="gallery", at=650, label="THE GALLERY")),
    # The trouble.
    (3, "zoom", dict(clip="goose", at=ev("msg", GOOSE, -8), z=20, dx=14, label="MIND THE GEESE", sfx=True)),
    (3, "zoom", dict(clip="pistol", at=24, z=12, dx=20, label="SHOOT", sfx=True)),
    (3, "zoom", dict(clip="punch", at=0, z=20, dx=6, label="PUNCH", sfx=True)),
    (3, "full", dict(clip="drift", at=140, y0=14, label="DRIFT", sfx=True)),
    (2, "full", dict(clip="drift", at=ev("msg", CRASH, -6), y0=14, sfx=True)),
    (3, "zoom", dict(clip="shark", at=ev("msg", BITTEN, -40), z=12, label="MIND THE SHARKS", label_top=True, sfx=True)),
    (3, "full", dict(clip="tank", at=120, y0=20, label="STEAL A TANK", sfx=True)),
    (2, "full", dict(clip="night_chase", at=150, y0=20, sfx=True)),
    (2, "full", dict(clip="heli_chase", at=ev("msg", CRASH, -10), y0=14, sfx=True)),
    (2, "full", dict(clip="pursuit", at=110, y0=20, sfx=True)),
    (4, "screen", dict(clip="spray", at=ev("msg", RESPRAYED, -20), label="LOSE THE STARS", sfx=True)),
    (4, "card", dict(lines=[("SHOW THEM WHO", 9, WHITE), ("DELIVERS THIS CITY.", 9, WHITE), ("MARGO", 4, GOLD)])),
    # The logo, on the title theme.
    (8, "logo", dict(clip="title", at=200, flash=0.2, title_theme=True)),
    (6, "card", dict(lines=[("A HOMEBREW GAME FOR", 4, GREY), ("MODRETRO CHROMATIC", 6, WHITE),
                            ("AND GAME BOY COLOR", 6, WHITE), ("", 3, GREY),
                            ("GITHUB.COM/TRANCETHEHUMAN/TORONTO-DISPATCH", 3, GREY)], fade_in=0.3, fade_out=1.2)),
]


class Footage:
    def __init__(self, folder):
        self.folder = folder
        self.data, self.audio = {}, {}

    def load(self, name):
        if name not in self.data:
            d = np.load(self.folder / f"{name}.npz")
            cols = list(d["columns"]) if "columns" in d else []
            self.data[name] = (d["frames"], d["meta"] if "meta" in d else None, cols)
        return self.data[name]

    def frames(self, name):
        return self.load(name)[0]

    def frame(self, name, i):
        f = self.frames(name)
        return f[max(0, min(i, len(f) - 1))]

    def meta(self, name, i, field):
        _, meta, cols = self.load(name)
        if meta is None or field not in cols:
            return None
        return meta[max(0, min(i, len(meta) - 1)), cols.index(field)]

    def start(self, name, at):
        """Resolve an in-point (a frame number or ev(...))."""
        if isinstance(at, int):
            return at
        field, value, offset = at
        _, meta, cols = self.load(name)
        col = meta[:, cols.index(field)]
        for i in range(1, len(col)):
            if col[i] != col[i - 1] and (value is None or col[i] == value):
                return max(0, i + offset)
        raise SystemExit(f"{name}: no {field} event {value}")

    def sound(self, name):
        if name not in self.audio:
            with wave.open(str(self.folder / f"{name}.wav")) as w:
                a = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2)
            self.audio[name] = a.astype(np.float32) / 32768
        return self.audio[name]


def text_image(lines, width=W, outline=False):
    """Lines of (text, scale, colour) in the game's 8 x 8 font, centred; with
    outline, every glyph gets a one-pixel (game pixel) ink border."""
    rows = []
    for text, scale, colour in lines:
        mask = np.zeros((8, max(1, 8 * len(text))), bool)
        for n, ch in enumerate(text):
            glyph = ui_art.font_rows(ch if ch in ui_art.FONT else " ")
            mask[:, n * 8:(n + 1) * 8] = [[c == "#" for c in row] for row in glyph]
        if outline:
            pad = np.pad(mask, 1)
            ring = np.zeros_like(pad)
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ring |= np.roll(np.roll(pad, dy, 0), dx, 1)
            line = np.zeros(pad.shape + (4,), np.uint8)
            line[ring] = INK + (255,)
            line[pad] = colour + (255,)
        else:
            line = np.zeros(mask.shape + (4,), np.uint8)
            line[mask] = colour + (255,)
        rows.append((np.kron(line, np.ones((scale, scale, 1), np.uint8)), scale))
    gap = lambda s: 3 * s  # noqa: E731
    total = sum(r.shape[0] for r, _ in rows) + sum(gap(s) for _, s in rows[:-1])
    out = np.zeros((total, width, 4), np.uint8)
    y = 0
    for line, scale in rows:
        w = min(line.shape[1], width)
        x = (width - w) // 2
        out[y:y + line.shape[0], x:x + w] = line[:, :w]
        y += line.shape[0] + gap(scale)
    return out


def paste(dst, rgba, x, y):
    h, w = rgba.shape[:2]
    region = dst[y:y + h, x:x + w]
    a = rgba[:, :, 3:4].astype(np.float32) / 255
    region[:] = (region * (1 - a) + rgba[:, :, :3] * a).astype(np.uint8)


def label_image(text, scale=6):
    t = text_image([(text, scale, WHITE)], width=8 * scale * (len(text) + 2), outline=True)
    cols = np.nonzero(t[:, :, 3].max(axis=0))[0]
    return t[:, cols[0]:cols[-1] + 1]


def scale_up(img, k):
    return np.repeat(np.repeat(img, k, axis=0), k, axis=1)


def letterbox(frame, y0, caption=None):
    out = np.zeros((H, W, 3), np.uint8)
    out[138:138 + 804] = scale_up(frame[y0:y0 + 67], 12)
    if caption:
        t = text_image([(caption, 3, GREY)])
        paste(out, t, 0, 1000)
    return out


def window(frame, z, cx, cy):
    """A W/z x H/z window of the frame centred near (cx, cy), at z x."""
    w, h = -(-W // z), -(-H // z)
    x0 = int(round(min(max(cx - w / 2, 0), 160 - w)))
    y0 = int(round(min(max(cy - h / 2, 0), 120 - h)))  # above the HUD rows
    big = scale_up(frame[y0:y0 + h, x0:x0 + w], z)
    return big[:H, :W]


def screen(frame):
    small = Image.fromarray(frame).resize((40, 36), Image.BILINEAR).filter(ImageFilter.GaussianBlur(1.2))
    bg = np.asarray(small.resize((W, int(W * 144 / 160)), Image.BILINEAR))
    top = (bg.shape[0] - H) // 2
    out = (bg[top:top + H].astype(np.float32) * 0.3).astype(np.uint8)
    x, y = (W - 960) // 2, 72
    out[y - 6:y + 864 + 6, x - 6:x + 960 + 6] = 12
    out[y:y + 864, x:x + 960] = scale_up(frame, 6)
    return out


def card(lines):
    out = np.zeros((H, W, 3), np.uint8)
    t = text_image(lines)
    paste(out, t, 0, (H - t.shape[0]) // 2)
    return out


class Shot:
    def __init__(self, footage, kind, args):
        self.f, self.kind, self.a = footage, kind, args
        self.start = footage.start(args["clip"], args["at"]) if "clip" in args else 0
        self.label = label_image(args["label"], 6 if kind != "screen" else 5) if args.get("label") else None
        self.still = card(args["lines"]) if kind == "card" else None
        self.track = None
        if kind == "zoom":
            # Follow the courier, smoothed over a third of a second.
            n = len(footage.frames(args["clip"]))
            xs = np.array([footage.meta(args["clip"], i, "x") for i in range(n)], np.float32)
            ys = np.array([footage.meta(args["clip"], i, "y") for i in range(n)], np.float32)
            k = np.ones(21) / 21
            pad = lambda a: np.pad(a, 10, mode="edge")  # noqa: E731
            self.track = (np.convolve(pad(xs), k, "valid"), np.convolve(pad(ys), k, "valid"))

    def render(self, i):
        a, kind = self.a, self.kind
        if kind == "card":
            return self.still
        j = self.start + i
        f = self.f.frame(a["clip"], j)
        if kind == "letterbox":
            out = letterbox(f, a["y0"], a.get("caption"))
        elif kind == "full":
            out = scale_up(f[a["y0"]:a["y0"] + 90], 12)
        elif kind == "zoom":
            xs, ys = self.track
            j = max(0, min(j, len(xs) - 1))
            out = window(f, a["z"], xs[j] + a.get("dx", 0), ys[j] + a.get("dy", 0) - 8)  # y is the feet
        elif kind == "screen":
            out = screen(f)
        elif kind == "logo":
            out = scale_up(f[0:90], 12)
        else:
            raise ValueError(kind)
        if kind in ("full", "zoom") and a.get("caption"):
            out = out.copy()
            paste(out, text_image([(a["caption"], 4, WHITE)], outline=True), 0, H - 96)
        if self.label is not None:
            out = out.copy()
            if kind == "screen":
                paste(out, self.label, (W - self.label.shape[1]) // 2, 72 + 864 + 30)
            else:
                paste(out, self.label, 72, 72 if a.get("label_top") else H - 72 - self.label.shape[0])
        return out


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


def schedule():
    """Each shot's (first, last) output frame, cut on the beat."""
    out, t = [], 0.0
    for beats, kind, args in TIMELINE:
        a, b = round(t * FPS), round((t + beats * BEAT) * FPS)
        out.append((a, b))
        t += beats * BEAT
    return out, t


def soundtrack(footage, spans, total):
    def song(name):
        with wave.open(str(footage.folder / f"music-{name}.wav")) as w:
            return np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).astype(np.float32) / 32768

    title, chase = song("title"), song("chase")
    out = np.zeros((int(total * RATE) + RATE, 2), np.float32)

    def lay(src, at, start, length, gain, fade_in=0.0, fade_out=0.0):
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

    logo = next(spans[n][0] for n, (_, _, a) in enumerate(TIMELINE) if a.get("title_theme")) / FPS
    lay(chase, 0.0, 0.0, logo + 0.6, 0.8, fade_out=0.6)
    lay(title, logo, 0.0, total - logo, 0.8, fade_in=0.05, fade_out=2.5)
    for (a, b), (_, kind, args) in zip(spans, TIMELINE):
        if args.get("sfx"):
            fx = footage.sound(args["clip"])
            per = len(fx) / len(footage.frames(args["clip"]))
            start = int(footage.start(args["clip"], args["at"]) * per)
            seg = fx[start:start + int((b - a) / FPS * RATE)]
            out[int(a / FPS * RATE):int(a / FPS * RATE) + len(seg)] += seg * 2.4  # effects-only output is quiet
    peak = np.abs(out).max()
    if peak > 0.95:
        out *= 0.95 / peak
    return (out[:int(total * RATE)] * 32767).astype(np.int16)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--footage", type=Path, default=GAME / "project/build/trailer")
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--preview", type=Path, default=None, help="write each shot's first and middle frame instead")
    args = parser.parse_args()
    footage = Footage(args.footage)
    spans, total = schedule()
    shots = [Shot(footage, kind, a) for _, kind, a in TIMELINE]
    if args.preview:
        args.preview.mkdir(parents=True, exist_ok=True)
        for n, ((a, b), shot) in enumerate(zip(spans, shots)):
            for tag, i in (("a", 0), ("b", (b - a) // 2)):
                img = shade(shot.render(i), i, b - a, shot.a)
                Image.fromarray(img).resize((W // 4, H // 4), Image.NEAREST).save(
                    args.preview / f"{n:02d}{tag}-{shot.kind}-{shot.a.get('clip', 'card')}.png")
        print(f"{len(shots)} shots, {total:.1f} s")
        return
    output = args.output or args.footage / "toronto-dispatch-trailer.mp4"
    audio_path = args.footage / "trailer-audio.wav"
    with wave.open(str(audio_path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(soundtrack(footage, spans, total).tobytes())
    ffmpeg = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
         "-i", "-", "-i", str(audio_path), "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
         "-tune", "animation", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
         "-movflags", "+faststart", "-shortest", str(output)],
        stdin=subprocess.PIPE)
    written = 0
    for (a, b), shot in zip(spans, shots):
        for i in range(b - a):
            ffmpeg.stdin.write(shade(shot.render(i), i, b - a, shot.a).tobytes())
            written += 1
    ffmpeg.stdin.close()
    if ffmpeg.wait():
        raise SystemExit("ffmpeg failed")
    print(f"Wrote {output}: {len(shots)} shots, {written} frames, {written / FPS:.1f} s")


if __name__ == "__main__":
    main()
