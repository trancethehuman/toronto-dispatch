# Trailer

A 49-second trailer cut entirely from the game: every frame is a PyBoy frame of a built ROM, cropped and scaled by whole numbers, and every sound is the game's own (its title and chase themes and its effects). The video is not kept in Git; rebuild it from a ROM with the two scripts below.

## Rebuild

```bash
"$HOME/Library/Application Support/modretro-chromatic/toolchain/.local/pyboy-venv/bin/python3" scripts/capture_trailer.py --rom project/build/main-3199527.gbc --symbols project/build/ip13.noi --output project/build/trailer --music
```

```bash
"$HOME/Library/Application Support/modretro-chromatic/toolchain/.local/pyboy-venv/bin/python3" scripts/make_trailer.py
```

The first records 33 shots (RGB frames, the effects heard and, for every frame, the game state the editor cuts on: the HUD message just posted, cash, stars, health, ammo, the courier's screen position) and the title and chase songs into `project/build/trailer/` with a `manifest.json` of each shot's staging; the second writes `project/build/trailer/toronto-dispatch-trailer.mp4` (1920 x 1080, 60 fps, H.264 and AAC, loudness normalised to -14 LUFS). `--preview DIR` writes each shot's first and middle frame instead. The symbols file must match the ROM's code (the main build differs from the `ip13` candidate only in its header checksum and build stamp). Requires PyBoy 2.7.0, numpy, Pillow and ffmpeg.

## How the footage is staged

Every shot starts from a state saved in the city at Union (opening radio skipped, sound set to effects only on the pause menu), in the car or on foot after A+B. Shots are then staged the way the README screenshots are, by writing the courier's position, heading, the clock, stars, cash or the active contract in emulator memory, and played with ordinary button presses: driving along real streets, walking into doors, riding the CN Tower's elevator, delivering, talking, fighting, swimming. People in the street shots (the busker, the neighbour with a parcel tip, the goose, the road ragers) are found in the ordinary crowds, not placed. The fights are played: the courier lingers beside a rager until the fight starts, then punches during their telegraphed swing (a counter) or holds A and lets go as they close in (a haymaker). The shark shot swims out into the lake from the Islands, waits for a shark and swims at it until it bites. The carjack steps up to a car in King St traffic and takes it with A. The CN Tower sequence moves the courier past the lobby's ropes between three clips; the cut hides the move. The songs are recorded with sound effects held off by memory writes.

## Structure

Cut on the chase theme's beats (0.375 s), mostly one to three beats a shot. Each shot starts just before its event, found in the logged game state (for example the frame the HUD posts COUNTER or HAYMAKER, the cash changing at a delivery, BITTEN BY A SHARK), so the action lands inside the first beat. Fights, the carjack, the pistol, the goose and the shark are close-ups that follow the courier; mechanics carry a short label in the game's font.

- Cold open (0:00–0:06): a haymaker, a counter, a carjack and the police helicopter, then the title.
- The city (0:06–0:12): eight letterboxed streets with their names (Front St at Union Station, Chinatown, the 501 on Queen St, Yonge-Dundas, High Park, King St at night, the Danforth, the Islands).
- The story (0:12–0:18): the opening radio ("WELCOME TO MARGO'S DEPOT", "RUSHLY VANS ARE ALL OVER TOWN NOW"), the festival contract and Vance's "SHE SAYS NO? WE'LL SEE."
- The work (0:18–0:31): the job board, a drive and a delivery, the CN Tower elevator and the Sky Desk, talking to visitors in the art gallery, the museum, the Eaton Centre, Dragon City, BYTE BARN, a busker, a neighbour's tip and the Gallery.
- The trouble (0:31–0:43): a goose, the pistol, a three-punch combo, a drift into a crash, a shark bite, the tank, night and helicopter chases and the spray bay; then Margo's "SHOW THEM WHO DELIVERS THIS CITY."
- The logo on the title theme (0:43–0:49).

Every line of dialogue is the game's own (radio lines and `content/story.json`); the festival tag line restates the premise in `content/story.json`.
