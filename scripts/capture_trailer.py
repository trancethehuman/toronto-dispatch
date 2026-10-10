#!/usr/bin/env python3
"""Record the trailer's footage and music from a native ROM in PyBoy 2.7.

Every shot starts from a state saved in the city (opening radio skipped,
sound set to effects only on the pause menu), either in the car or on foot
after getting out with A+B, and is staged the way the README screenshots
are: by writing the courier's position, heading, the clock, stars, cash or
the active contract in emulator memory, then playing with ordinary button
presses while every frame is recorded. Nothing is drawn over the game here;
scripts/make_trailer.py cuts the footage together.

Writes, inside project/build: <shot>.npz (RGB frames, 160 x 144), <shot>.wav
(the effects heard during the shot), music-title.wav and music-chase.wav
(the songs with sound effects held off) and manifest.json (the ROM hash, every shot's staging and
frame count). Requires PyBoy 2.7.0 and numpy; run with the plugin's PyBoy.

  capture_trailer.py --rom ROM --symbols NOI --output project/build/trailer [--only a,b] [--music]
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import struct
import wave

import numpy as np
from pyboy import PyBoy

GAME = Path(__file__).resolve().parents[1]
RATE = 48000
TD_FIELDS = (
    ("u", "H"), ("v", "H"), ("park_u", "H"), ("park_v", "H"), ("cash", "H"), ("seconds", "H"), ("left", "H"),
    ("speed", "h"), ("heading", "B"), ("vehicle", "B"), ("onfoot", "B"), ("mode", "B"), ("menu", "B"), ("job", "B"),
    ("stage", "B"), ("health", "B"), ("done", "B"), ("subsecond", "B"), ("complete", "16s"), ("transit_origin", "B"),
    ("transit_target", "B"), ("ride_left", "B"), ("cooldown", "B"), ("msg", "B"), ("reserved", "B"), ("safe_u", "H"),
    ("safe_v", "H"), ("vitality", "B"), ("ammo", "B"), ("wanted", "B"), ("heat", "B"), ("district", "B"),
    ("park_district", "B"))
SCENES = ("core_nw", "core_ne", "core_sw", "core_se", "west_nw", "west_ne", "west_sw", "west_se", "high_park_nw",
          "high_park_ne", "high_park_sw", "high_park_se", "east_nw", "east_ne", "east_sw", "east_se")
# Play clock (td.seconds): 1,024 a day from 08:00. Day two brings rain.
MIDDAY, GOLDEN, DUSK, NIGHT, DAWN, RAIN = 200, 455, 505, 620, 905, 1024 + 128 + 20
EAST, SOUTH, WEST, NORTH = 0, 4, 8, 12
# Logged with every recorded frame so the editor can cut on events (td.msg
# is the HUD message just posted; the courier's screen position frames the
# close-ups).
META = ("x", "y", "u", "v", "cash", "speed", "onfoot", "mode", "stage", "vitality", "ammo", "wanted", "msg",
        "interior", "hostile", "aim_who", "aim_time", "rolling", "shark", "radio")


class Rig:
    def __init__(self, rom, symbols):
        self.pb = PyBoy(io.BytesIO(rom), window="null", cgb=True, sound_emulated=True,
                        sound_sample_rate=RATE, sound_volume=100)
        self.pb.set_emulation_speed(0)
        self.mem = self.pb.memory
        self.syms = symbols
        self.held = set()
        self.frames = self.pcm = self.meta = None
        self.steps = []
        layout, off = {}, 0
        for name, fmt in TD_FIELDS:
            layout[name] = (off, "<" + fmt)
            off += struct.calcsize("<" + fmt)
        self.layout = layout

    # memory
    def sym(self, name):
        return self.syms["_" + name]

    def u8(self, name, off=0):
        return self.mem[self.sym(name) + off]

    def u16(self, name, off=0):
        a = self.sym(name) + off
        return self.mem[a] | (self.mem[a + 1] << 8)

    def set8(self, name, value, off=0):
        self.mem[self.sym(name) + off] = value & 255

    def set16(self, name, value):
        a = self.sym(name)
        self.mem[a], self.mem[a + 1] = value & 255, (value >> 8) & 255

    def td(self):
        base = self.sym("td")
        raw = bytes(self.mem[base + i] for i in range(58))
        return {name: struct.unpack_from(fmt, raw, off)[0] for name, (off, fmt) in self.layout.items()}

    def put(self, **fields):
        base = self.sym("td")
        for name, value in fields.items():
            off, fmt = self.layout[name]
            for i, b in enumerate(struct.pack(fmt, value)):
                self.mem[base + off + i] = b

    # time and buttons
    def hold(self, *buttons):
        for b in self.held - set(buttons):
            self.pb.button_release(b)
        for b in set(buttons) - self.held:
            self.pb.button_press(b)
        self.held = set(buttons)

    def tick(self, n=1, *buttons, each=None):
        if buttons:
            self.hold(*buttons)
        for i in range(n):
            if each:
                each(i)
            recording = self.frames is not None
            self.pb.tick(1, recording, True)
            if recording:
                self.frames.append(self.pb.screen.ndarray[:, :, :3].copy())
                self.pcm.append(self.pb.sound.ndarray.copy())
                self.meta.append(self.sample())

    def sample(self):
        t = self.td()
        inside = self.u8("td_interior") != 255
        u, v = (self.u16("in_u"), self.u16("in_v")) if inside else (t["u"] >> 4, t["v"] >> 4)
        return (u - self.u16("scroll_x"), v - self.u16("scroll_y"), u, v, t["cash"], t["speed"], t["onfoot"],
                t["mode"], t["stage"], t["vitality"], t["ammo"], t["wanted"], t["msg"], self.u8("td_interior"),
                self.u8("td_npc_hostile"), self.u8("lf_aim_who"), self.u8("lf_aim_time"), self.u8("td_rolling"),
                self.u8("shark_state"), self.u8("td_radio_script"))

    def press(self, button, frames=4, after=4):
        self.tick(frames, *([button] if isinstance(button, str) else button))
        self.hold()
        self.tick(after)

    def note(self, text):
        self.steps.append(text)

    # staging
    def place(self, u, v, heading=None):
        fields = dict(u=u * 16, v=v * 16, safe_u=u * 16, safe_v=v * 16)
        if heading is not None:
            fields["heading"] = heading
        for _ in range(8):
            self.put(**fields)
            self.tick(1)
            t = self.td()
            if t["u"] >> 4 == u and t["v"] >> 4 == v:
                return

    def warp(self, scene, u, v, heading=0, clock=None, settle=90):
        """Move the courier into a scene through the engine's own queued scene
        change; in the car, the car comes along, on foot it stays parked."""
        t = self.td()
        reload = t["district"] != scene or self.u8("td_interior") != 255
        fields = dict(district=scene, speed=0, heading=heading, wanted=0, heat=0, vitality=100)
        if not t["onfoot"]:
            fields.update(park_district=scene, park_u=u * 16, park_v=v * 16)
        if clock is not None:
            fields["seconds"] = clock
        self.put(**fields)
        if reload:
            self.put(u=u * 16, v=v * 16, safe_u=u * 16, safe_v=v * 16)
            self.set8("td_transition_pending", 2)
            n = 0
            while self.u8("td_transition_pending") and n < 600:
                self.tick(1)
                n += 1
        self.place(u, v, heading)
        self.tick(settle)
        self.note(f"courier written at {SCENES[scene]} ({u}, {v}) heading {heading}"
                  f"{' on foot' if t['onfoot'] else ' in the car'}" + (f", clock {clock}" if clock is not None else ""))

    def quiet_radio(self):
        for _ in range(16):
            if self.u8("td_radio_script") == 255 and self.td()["mode"] == 0:
                return
            self.press("b", 4, 8)

    def walk_in(self, x, y, limit=360):
        """Inside a building: walk with the D-pad to (x, y)."""
        best, stuck = None, 0
        for _ in range(limit):
            dx, dy = x - self.u16("in_u"), y - self.u16("in_v")
            if abs(dx) <= 2 and abs(dy) <= 2:
                break
            buttons = []
            if abs(dx) > 2:
                buttons.append("right" if dx > 0 else "left")
            if abs(dy) > 2:
                buttons.append("down" if dy > 0 else "up")
            self.tick(1, *buttons)
            d = abs(dx) + abs(dy)
            if best is None or d < best:
                best, stuck = d, 0
            else:
                stuck += 1
                if stuck > 30:
                    break
        self.hold()

    def wait_interior(self, key=None, limit=600):
        n = 0
        while n < limit and (self.u8("td_transition_pending") or self.u8("td_interior") == 255
                             or (key is not None and self.u8("td_interior") != KEYS.index(key))):
            self.tick(1)
            n += 1

    # recording
    def begin(self):
        self.frames, self.pcm, self.meta = [], [], []

    def end(self, out, name):
        video = np.stack(self.frames)
        audio = np.concatenate(self.pcm).astype(np.int16) << 8
        meta = np.array(self.meta, np.int32)
        self.frames = self.pcm = self.meta = None
        self.hold()
        np.savez_compressed(out / f"{name}.npz", frames=video, meta=meta, columns=np.array(META))
        write_wav(out / f"{name}.wav", audio)
        return len(video)

    def record(self, out, name, frames, *buttons, each=None):
        self.begin()
        self.tick(frames, *buttons, each=each)
        return self.end(out, name)


def write_wav(path, audio):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(audio.tobytes())


def read_symbols(path):
    out = {}
    for line in Path(path).read_text().splitlines():
        m = re.fullmatch(r"DEF (\S+) 0x([0-9A-Fa-f]+)", line.strip())
        if m:
            out[m[1]] = int(m[2], 16)
    return out


def content(name):
    return json.loads((GAME / "content" / name).read_text())


DOORS = content("doors.json")["scenes"]
INTERIORS = content("interiors.json")["interiors"]
KEYS = [i["key"] for i in INTERIORS]
CAMPAIGN = content("campaign.json")
PEOPLE = {l["index"]: l for l in content("people.json")["looks"]}


def door(name):
    for slug, doors in DOORS.items():
        for d in doors:
            if d["name"] == name:
                return SCENES.index(slug.removeprefix("toronto_")), d["u"], d["v"]
    raise KeyError(name)


def enter(r, name, clock=MIDDAY):
    scene, u, v = door(name)
    r.warp(scene, u, v, NORTH, clock)
    r.press("a", 4, 4)
    r.wait_interior()
    r.tick(90)
    r.note(f"A at the door of {name}")


def point(key, kind, n=0):
    return [p for p in INTERIORS[KEYS.index(key)]["points"] if p["kind"] == kind][n]


def actor_pos(r, k):
    b = r.sym("actors") + 56 * (9 + k)
    return (r.mem[b + 1] | (r.mem[b + 2] << 8)) >> 5, (r.mem[b + 3] | (r.mem[b + 4] << 8)) >> 5


def visible(r, k):
    sx, sy = r.u16("scroll_x"), r.u16("scroll_y")
    x, y = actor_pos(r, k)
    return not (r.mem[r.sym("actors") + 56 * (9 + k)] & 2) and 24 <= x - sx < 136 and 32 <= y - sy < 112


def behave(r, k):
    look = r.u8("td_slot_look", k)
    return PEOPLE[look]["behave"] if look in PEOPLE else None


def active(r, k):
    return not r.mem[r.sym("actors") + 56 * (9 + k)] & 2


def alone(r, k, room=28):
    x, y = actor_pos(r, k)
    return all(j == k or not active(r, j) or abs(actor_pos(r, j)[0] - x) + abs(actor_pos(r, j)[1] - y) > room
               for j in range(8))


def find_people(r, wanted, spots, limit=30):
    """Walk the spots until one of the eight nearby walkers has one of the
    behaviours (with nobody else close by), then stand where the camera
    shows them."""
    for scene, u, v in spots:
        r.warp(scene, u, v, EAST, MIDDAY)
        for step in range(limit):
            r.tick(15, "right" if (step // 8) % 2 == 0 else "left")
            r.quiet_radio()
            r.put(vitality=100, wanted=0, heat=0)
            for k in range(8):
                if active(r, k) and behave(r, k) in wanted and alone(r, k):
                    r.hold()
                    if not visible(r, k):
                        x, y = actor_pos(r, k)
                        r.place(x - 40, y)
                        r.tick(4)
                    if active(r, k) and behave(r, k) in wanted:
                        return k
    return None


STREETS = ((1, 300, 870), (0, 760, 860), (0, 924, 878), (11, 600, 870), (2, 500, 240), (6, 400, 600),
           (0, 300, 860), (13, 300, 140), (9, 480, 600), (1, 340, 880), (0, 700, 860), (6, 500, 600), (0, 900, 930))


def control(*plan):
    """A schedule of (frames, buttons) as an each-frame callback."""
    def each(r):
        def step(i):
            acc = 0
            for frames, buttons in plan:
                if i < acc + frames:
                    r.hold(*buttons)
                    return
                acc += frames
            r.hold()
        return step
    return each, sum(f for f, _ in plan)


# ---- shots

def shot_title(r, out, name):
    return r.record(out, name, 600)


def shot_opening_radio(r, out, name):
    r.note("A on the title; the opening radio plays at Union")
    return r.record(out, name, 1500)


def drive(scene, u, v, heading, clock, frames=420):
    def shot(r, out, name):
        r.warp(scene, u, v, heading, clock)
        return r.record(out, name, frames, "a")
    return shot


def walk(scene, u, v, heading, clock, button, frames=360, settle=60):
    def shot(r, out, name):
        r.warp(scene, u, v, heading, clock)
        r.tick(settle)
        return r.record(out, name, frames, button)
    return shot


def shot_queen_rain(r, out, name):
    r.warp(3, 230, 206, EAST, RAIN)
    r.tick(200)
    return r.record(out, name, 420, "a")


def swim(stars=0, frames=420):
    def shot(r, out, name):
        r.warp(3, 740, 740, SOUTH, MIDDAY)
        r.tick(150, "down")
        r.hold()
        r.tick(120)
        return r.record(out, name, frames, each=lambda i: r.put(wanted=stars, heat=8 if stars else 0, vitality=100))
    return shot


def shot_delivery(r, out, name):
    """Contract 1 played: Select opens dispatch, A accepts, Select collects,
    east along Front St, Select delivers at St Lawrence."""
    r.warp(3, 268, 564, EAST, MIDDAY - 100)
    r.begin()
    r.press("select", 4, 40)
    r.press("a", 4, 100)
    for _ in range(4):
        r.press("b", 4, 30)
    r.press("select", 4, 60)
    r.quiet_radio()
    stop_at(r, 504, 26)
    r.press("select", 4, 200)
    r.note("contract 1 from the dispatch board: collect at Union, drive east on Front St, deliver at St Lawrence")
    return r.end(out, name)


def stop_at(r, target, early, each=lambda: None):
    """Drive east and brake so the car stops near u = target."""
    for _ in range(900):
        each()
        r.tick(1, "a")
        if r.td()["u"] >> 4 >= target - early:
            break
    for _ in range(300):
        each()
        r.tick(1, "b")
        if r.td()["speed"] <= 0:
            break
    for _ in range(6):
        if r.td()["u"] >> 4 >= target - 8:
            break
        each()
        r.tick(10, "a")
        r.tick(20, "b")
    r.hold()
    r.tick(20)


def shot_drift(r, out, name):
    r.warp(3, 100, 396, EAST, MIDDAY)
    each, n = control((150, ("a",)), (16, ("b", "right")), (44, ("a", "right")), (150, ("a",)))
    return r.record(out, name, n, each=each(r))


def chase(stars, scene, u, v, heading, clock, *plan):
    def shot(r, out, name):
        r.warp(scene, u, v, heading, clock)
        for _ in range(30):
            r.put(wanted=stars, heat=12)
            r.tick(10)
        r.place(u, v, heading)
        each, n = control(*plan)
        step = each(r)

        def tick(i):
            r.put(wanted=stars, heat=12, vitality=100)
            step(i)
        return r.record(out, name, n, each=tick)
    return shot


def shot_tank(r, out, name):
    hidden = (GAME / "project/plugins/toronto-driving/engine/include/td_hidden.h").read_text()
    hu, hv, hs = (int(re.search(rf"td_hidden_{f}\[TD_HIDDEN_COUNT\]=\{{(\d+)", hidden).group(1))
                  for f in ("u", "v", "scene"))
    r.warp(hs, hu + 180, hv, WEST, MIDDAY)
    for _ in range(40):
        r.place(hu + 180, hv)
        r.tick(10)
        if r.u8("td_hidden_slot") != 255:
            break
    r.place(hu + 60, hv + 12)
    r.tick(30)
    r.begin()
    r.tick(40, "left")
    for _ in range(6):
        r.place(hu, hv + 12)
        r.tick(6)
        r.press("a", 4, 24)
        if r.u8("td_player_special"):
            break
    each, n = control((120, ("a",)), (30, ("a", "right")), (200, ("a",)))
    r.tick(n, each=each(r))
    r.note("the tank by the Moss Park Armoury, taken with A and driven")
    return r.end(out, name)


def fight(finish):
    """A tough or road rager found in the crowd: linger beside them until
    they start a fight, then finish it with a counter (a punch during their
    telegraphed swing) or a haymaker (A held standing still, let go as they
    close in)."""
    def shot(r, out, name):
        k = find_people(r, ("TOUGH", "RAGER"), STREETS * 3)
        if k is None:
            return 0
        x, y = actor_pos(r, k)
        r.place(x - 12, y, EAST)
        r.tick(1, "right")
        r.hold()
        r.note(f"beside a tough or road rager found in the crowd; lingering starts the fight; {finish}")
        r.begin()
        state = {"phase": 0, "held": 0, "after": 0}
        for _ in range(1200):
            r.put(vitality=100)
            fx, fy = actor_pos(r, k)
            hostile = r.u8("td_npc_hostile") & (1 << k)
            t = r.td()
            cu, cv = t["u"] >> 4, t["v"] >> 4
            if state["phase"] == 0:
                if hostile:
                    state["phase"] = 1
                    r.tick(1, "right" if fx >= cu else "left")
                    r.hold()
                    continue
                r.put(u=(fx - 12) * 16, v=fy * 16)
                r.tick(1)
            elif state["phase"] == 1 and finish == "counter":
                if r.u8("td_slot_pose", k) == 3:
                    r.tick(1, "right" if fx >= cu else "left")
                    r.press("a", 2, 1)
                    if t["msg"] == 43 or r.td()["msg"] == 43:
                        state["phase"] = 2
                else:
                    r.tick(1)
                if r.td()["msg"] == 43:
                    state["phase"] = 2
            elif state["phase"] == 1:
                ahead = 4 <= (fx - cu if fx >= cu else cu - fx) <= 18 and abs(fy - cv) < 10
                if state["held"] >= 64 and ahead:  # the charge counts every other update
                    r.hold()
                    r.tick(2)
                    if r.td()["msg"] == 46:
                        state["phase"] = 2
                    state["held"] = 0
                else:
                    state["held"] += 1
                    r.tick(1, "a")
            else:
                r.hold()
                r.tick(1)
                state["after"] += 1
                if state["after"] > 120:
                    break
        return r.end(out, name)
    return shot


def shot_goose(r, out, name):
    """Walk up to a Canada goose; it stands its ground and pecks."""
    k = find_people(r, ("GOOSE",), ((11, 600, 870), (6, 400, 600), (6, 500, 600), (3, 600, 720)) * 3)
    if k is None:
        return 0
    x, y = actor_pos(r, k)
    r.place(x - 44, y, EAST)
    state = {"t": 0}

    def each(i):
        r.put(vitality=100)
        x, y = actor_pos(r, k)
        if state["t"] == 0 and r.u8("td_npc_hostile") & (1 << k):
            state["t"] = i
        if state["t"] == 0 and i < 240:
            u = r.td()["u"] >> 4
            r.hold("right") if u < x - 14 else r.hold()
            if abs((r.td()["v"] >> 4) - y) > 2:
                r.put(v=y * 16)
        else:
            r.hold()
    r.note("walked up to a goose found in the waterfront crowd")
    return r.record(out, name, 360, each=each)


def beside(behaviours, gap, *plan, spots=STREETS * 2):
    """Find someone with one of the behaviours, stand gap px to their left
    and play the plan."""
    def shot(r, out, name):
        k = find_people(r, behaviours, spots)
        if k is None:
            return 0
        for attempt in range(60):  # free radio strip, nobody else beside them
            if attempt:
                r.tick(15)
                r.quiet_radio()
            x, y = actor_pos(r, k)
            if active(r, k) and alone(r, k, 32):
                for dx, dy, face in ((-gap, 0, EAST), (gap, 0, WEST), (0, gap, NORTH), (0, -gap, SOUTH)):
                    r.place(x + dx, y + dy, face)
                    t = r.td()
                    if abs((t["u"] >> 4) - x - dx) + abs((t["v"] >> 4) - y - dy) <= 2:
                        break
                r.tick(4)
                if alone(r, k, 32) and r.u8("td_radio_script") == 255:
                    break
        r.note(f"beside a walker found in the crowd ({'/'.join(behaviours)})")
        each, n = control(*plan)
        step = each(r)

        def tick(i):
            r.put(vitality=100)
            step(i)
        return r.record(out, name, n, each=tick)
    return shot


def shot_carjack(r, out, name):
    """On foot on King St: step up to a car in traffic and take it with A;
    the driver runs off."""
    r.warp(3, 300, 380, EAST, MIDDAY)
    r.tick(60)
    for _ in range(120):
        r.tick(5)
        sx, sy = r.u16("scroll_x"), r.u16("scroll_y")
        for i in range(6):
            a = r.sym("actors") + 56 * (2 + i)
            if r.mem[a] & 2:
                continue
            tu = (r.mem[r.sym("td_traffic_u") + 2 * i] | (r.mem[r.sym("td_traffic_u") + 2 * i + 1] << 8)) >> 4
            tv = (r.mem[r.sym("td_traffic_v") + 2 * i] | (r.mem[r.sym("td_traffic_v") + 2 * i + 1] << 8)) >> 4
            if 40 <= tu - sx < 120 and 40 <= tv - sy < 100:
                r.begin()
                r.place(tu - 12, tv, EAST)
                r.tick(6)
                r.press("a", 4, 30)
                if r.td()["onfoot"]:
                    r.frames = r.pcm = r.meta = None
                    continue
                r.tick(150, "a")
                r.note("on foot beside a car in King St traffic, A takes it")
                return r.end(out, name)
    return 0


def shot_punch(r, out, name):
    k = find_people(r, ("WALK", "SLOW"), STREETS)
    if k is None:
        return 0
    x, y = actor_pos(r, k)
    r.place(x - 10, y, EAST)
    r.note("beside a walker: three quick punches")
    each, n = control((6, ()), (3, ("a",)), (5, ()), (3, ("a",)), (5, ()), (3, ("a",)), (120, ()))
    return r.record(out, name, n, each=each(r))


def shot_pistol(r, out, name):
    r.warp(1, 300, 870, EAST, MIDDAY)
    r.put(ammo=40)
    r.tick(60)

    def each(i):
        r.put(vitality=100)
        if i < 30:
            r.hold("right")
        elif i < 200:
            r.hold("b") if (i // 6) % 4 else r.hold()
        else:
            r.hold()
    return r.record(out, name, 300, each=each)


def shot_spray(r, out, name):
    """Three stars, King St West: into the spray bay, which clears them."""
    r.warp(2, 330, 380, EAST, MIDDAY)
    r.put(cash=200)
    for _ in range(20):
        r.put(wanted=3, heat=12)
        r.tick(10)
    r.place(330, 380, EAST)
    r.begin()
    stop_at(r, 488, 22, lambda: r.put(wanted=3, heat=12, vitality=100))
    r.tick(240)
    r.note("three stars written; driven east into the King St West spray bay and stopped")
    return r.end(out, name)


def shot_cn_tower(r, out, name):
    """SKY HIGH LUNCH with the lunch aboard: into the CN Tower (cn_enter),
    the elevator to the LookOut (cn_ride) and the Sky Desk (cn_desk). The
    courier is moved between the clips (the lobby's ropes are in the way)."""
    job = [q["id"] for q in CAMPAIGN["quests"]].index("contract-89")
    stop = CAMPAIGN["stops"][51]
    r.put(job=job, stage=1, health=100, left=600, done=10)
    r.warp(2, 400, 400, EAST, MIDDAY)  # a scene change refreshes the job's route
    r.warp(stop["district"], stop["u"], stop["v"], NORTH, MIDDAY)
    r.note("contract 89 written at stage 1 (lunch aboard) at the CN Tower door")
    r.tick(40)
    r.begin()
    r.tick(30)
    r.press("a", 4, 4)
    r.wait_interior()
    r.tick(150, "up")
    total = r.end(out, "cn_enter")
    lift = point("cn_base", "elevator", 1)
    r.set16("in_u", lift["x"])
    r.set16("in_v", lift["y"] + 4)
    r.tick(20)
    r.begin()
    r.tick(10, "up")
    r.press("a", 4, 4)
    r.wait_interior("cn_lookout", 900)
    r.tick(150)
    total += r.end(out, "cn_ride")
    desk = point("cn_lookout", "desk")
    r.set16("in_u", desk["x"])
    r.set16("in_v", desk["y"])
    r.tick(20)
    r.begin()
    r.tick(10, "up")
    r.press("a", 4, 240)
    total += r.end(out, "cn_desk")
    r.note("A at the door; moved to the elevator, A rode up; moved to the Sky Desk, A delivered")
    return total


def interior_walk(door_name, *plan):
    def shot(r, out, name):
        enter(r, door_name)
        each, n = control(*plan)
        return r.record(out, name, n, each=each(r))
    return shot


def shot_ago_card(r, out, name):
    enter(r, "ART GALLERY (AGO)")
    p = point("ago", "painting")
    r.begin()
    r.walk_in(p["x"], p["y"] + 6)
    r.tick(8, "up")
    r.press("a", 4, 150)
    return r.end(out, name)


def shot_shark(r, out, name):
    """Out into open water off the Islands until a shark circles, then swim
    at it when it closes in, until it bites."""
    r.warp(3, 740, 740, SOUTH, MIDDAY)
    for _ in range(900):  # across the channel and the Island, into the lake
        r.tick(1, "down")
        if r.td()["v"] >> 4 >= 944:
            break
    r.hold()
    for _ in range(3600):
        r.put(vitality=100)
        r.tick(1)
        if r.u8("shark_state"):
            break
    r.note("swam out from the Islands until a shark circled; swam at it as it closed in")
    r.begin()
    after = 0
    for i in range(1500):
        t = r.td()
        if r.u8("shark_state") == 2:
            su = r.mem[r.sym("shark_u")] | (r.mem[r.sym("shark_u") + 1] << 8)
            sv = r.mem[r.sym("shark_v")] | (r.mem[r.sym("shark_v") + 1] << 8)
            pu, pv = t["u"] >> 4, t["v"] >> 4
            b = (["right"] if su > pu + 2 else ["left"] if su < pu - 2 else []) + \
                (["down"] if sv > pv + 2 else ["up"] if sv < pv - 2 else [])
            r.tick(1, *b) if b else (r.hold(), r.tick(1))
        else:
            r.hold()
            r.tick(1)
        if after or r.td()["msg"] == 37:
            after += 1
            if after > 120:
                break
    return r.end(out, name)


def shot_gallery(r, out, name):
    r.warp(3, 268, 600, EAST, MIDDAY)
    r.begin()
    r.press("start", 4, 20)
    for _ in range(7):
        r.press("down", 4, 6)
    r.tick(20)
    r.press("a", 4, 10)
    r.wait_interior()
    r.tick(60)
    for n in (2, 5):
        ex = point("gallery_hall", "exhibit", n)
        r.walk_in(ex["x"], ex["y"] + 6)
        r.tick(8, "up")
        r.press("a", 4, 130)
        r.press("b", 4, 20)
    r.note("Start, GALLERY, walked to two exhibits, A reads each card")
    return r.end(out, name)


CAR, FOOT = "car", "foot"
SHOTS = {
    # name: (start state, shot)
    "title": ("title", shot_title),
    "opening_radio": ("opening", shot_opening_radio),
    "front_golden": (CAR, drive(3, 100, 572, EAST, GOLDEN)),
    "king_night": (CAR, drive(3, 100, 396, EAST, NIGHT)),
    "queen_rain": (CAR, shot_queen_rain),
    "high_park_drive": (CAR, drive(9, 880, 660, SOUTH, GOLDEN - 40)),
    "danforth": (CAR, drive(13, 100, 140, EAST, DAWN)),
    "chinatown_walk": (FOOT, walk(0, 924, 878, WEST, MIDDAY, "left")),
    "yonge_dundas": (FOOT, walk(1, 330, 890, EAST, DUSK, "right")),
    "harbour_swim": (FOOT, swim()),
    "shark": (FOOT, shot_shark),
    "delivery": (CAR, shot_delivery),
    "drift": (CAR, shot_drift),
    "heli_chase": (CAR, chase(4, 3, 100, 396, EAST, MIDDAY, (260, ("a",)), (40, ("a", "left")), (180, ("a",)))),
    "pursuit": (CAR, chase(3, 3, 100, 572, EAST, DUSK, (480, ("a",)))),
    "night_chase": (CAR, chase(3, 3, 100, 206, EAST, NIGHT + 40, (480, ("a",)))),
    "tank": (FOOT, shot_tank),
    "street_fight": (FOOT, fight("counter")),
    "haymaker_fight": (FOOT, fight("haymaker")),
    "goose": (FOOT, shot_goose),
    "busker": (FOOT, beside(("BUSK",), 10, (12, ()), (4, ("select",)), (300, ()))),
    "neighbour": (FOOT, beside(("BEG", "SIT"), 10, (12, ()), (4, ("select",)), (300, ()), spots=STREETS * 4)),
    "pistol": (FOOT, shot_pistol),
    "carjack": (FOOT, shot_carjack),
    "punch": (FOOT, shot_punch),
    "spray": (CAR, shot_spray),
    "cn_tower": (FOOT, shot_cn_tower),
    "rom_walk": (FOOT, interior_walk("ROYAL ONT. MUSEUM", (200, ("up",)))),
    "eaton_walk": (FOOT, interior_walk("EATON CENTRE", (120, ("up",)), (120, ("left",)))),
    "dragon_walk": (FOOT, interior_walk("DRAGON CITY MALL", (180, ("up",)), (60, ("right",)))),
    "byte_walk": (FOOT, interior_walk("BYTE BARN", (180, ("up",)), (60, ("left",)))),
    "ago_card": (FOOT, shot_ago_card),
    "gallery": (FOOT, shot_gallery),
}


def capture_music(rom, symbols, out):
    """The two songs the trailer uses, with sound effects held off: the title
    theme on the title screen, and the chase standing still inside a cafe (no
    traffic or police) with three stars written. Each take starts when the
    engine loads the song."""
    r = Rig(rom, symbols)
    songs = {symbols[f"_td_song_{s}"] & 0xFFFF: s for s in ("title", "day", "night", "chase")}

    def take(name, seconds, setup=lambda i: None):
        n = 0
        while songs.get(r.u16("music_current_track")) != name:
            setup(0)
            r.tick(1)
            n += 1
            if n > 1200:
                raise SystemExit(f"the {name} song never started")
        pcm = []
        for i in range(int(seconds * 60)):
            setup(i)
            r.set8("sfx_play_bank", 0xFF)
            r.set8("music_mute_mask", 0)
            r.pb.tick(1, False, True)
            pcm.append(r.pb.sound.ndarray.copy())
        write_wav(out / f"music-{name}.wav", np.concatenate(pcm).astype(np.int16) << 8)

    take("title", 70)
    r.press("a", 4, 120)
    for _ in range(90):
        r.tick(10)
        if r.u8("td_radio_script") != 255 or r.td()["mode"] != 0:
            r.press("b", 4, 8)
    r.tick(30, "a", "b")
    r.hold()
    r.tick(60)
    enter(r, next(d["name"] for doors in DOORS.values() for d in doors if d["interior"] == "cafe"))
    take("chase", 55, lambda i: r.put(wanted=3, heat=12))
    r.pb.stop(save=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--rom", required=True, type=Path)
    parser.add_argument("--symbols", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--only", default="")
    parser.add_argument("--music", action="store_true", help="also record the songs")
    args = parser.parse_args()
    out = args.output.resolve()
    if not out.is_relative_to((GAME / "project/build").resolve()):
        raise SystemExit("write the footage inside project/build (it stays out of Git)")
    out.mkdir(parents=True, exist_ok=True)
    rom = args.rom.read_bytes()
    symbols = read_symbols(args.symbols)
    manifest_path = out / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {"shots": {}}
    manifest["rom_sha256"] = hashlib.sha256(rom).hexdigest()
    manifest["emulator"] = "PyBoy 2.7.0 (CGB), 48 kHz"

    # Start states: the title screen; just after A on it; the city at Union
    # with the opening calls skipped and sound set to effects only (Start,
    # up twice to SOUND, A, B); and the same on foot after A+B.
    r = Rig(rom, symbols)
    states = {}

    def save(name):
        states[name] = io.BytesIO()
        r.pb.save_state(states[name])

    r.tick(240)
    save("title")
    r.press("a", 4, 60)
    save("opening")
    for _ in range(90):
        r.tick(10)
        if r.u8("td_radio_script") != 255 or r.td()["mode"] != 0:
            r.press("b", 4, 8)
    r.press("start", 4, 20)
    r.press("up", 4, 6)
    r.press("up", 4, 6)
    r.press("a", 4, 20)
    r.press("b", 4, 30)
    save(CAR)
    r.tick(30, "a", "b")
    r.hold()
    r.tick(60)
    if not r.td()["onfoot"]:
        raise SystemExit("A+B did not get the courier out of the car")
    save(FOOT)
    wanted = [s for s in args.only.split(",") if s] or list(SHOTS)
    for name in wanted:
        start, shot = SHOTS[name]
        r.steps = []
        r.hold()
        states[start].seek(0)
        r.pb.load_state(states[start])
        frames = shot(r, out, name)
        manifest["shots"][name] = {"start": start, "frames": frames, "staging": r.steps}
        print(f"{name}: {frames} frames", flush=True)
    r.pb.stop(save=False)
    if args.music:
        capture_music(rom, symbols, out)
        manifest["music"] = "title on the title screen; chase inside a cafe with three stars; sound effects held off"
    manifest_path.write_text(json.dumps(manifest, indent=1) + "\n")


if __name__ == "__main__":
    main()
