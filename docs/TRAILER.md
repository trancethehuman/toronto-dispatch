# Trailer

A 100-second trailer cut entirely from the game: every frame is a PyBoy frame of a built ROM, cropped and scaled by whole numbers, and every sound is the game's own (its title and chase themes and its effects). The video is not kept in Git; rebuild it from a ROM with the two scripts below.

## Rebuild

```bash
"$HOME/Library/Application Support/modretro-chromatic/toolchain/.local/pyboy-venv/bin/python3" scripts/capture_trailer.py --rom project/build/main-3199527.gbc --symbols project/build/ip13.noi --output project/build/trailer --music
```

```bash
"$HOME/Library/Application Support/modretro-chromatic/toolchain/.local/pyboy-venv/bin/python3" scripts/make_trailer.py
```

The first records 36 shots (RGB frames and the effects heard) and the title and chase songs into `project/build/trailer/` with a `manifest.json` of each shot's staging; the second writes `project/build/trailer/toronto-dispatch-trailer.mp4` (1920 x 1080, 60 fps, H.264 and AAC, loudness normalised to -14 LUFS). `--preview DIR` writes one still per cut instead. The symbols file must match the ROM's code (the main build differs from the `ip13` candidate only in its header checksum and build stamp). Requires PyBoy 2.7.0, numpy, Pillow and ffmpeg.

## How the footage is staged

Every shot starts from a state saved in the city at Union (opening radio skipped, sound set to effects only on the pause menu), in the car or on foot after A+B. Shots are then staged the way the README screenshots are, by writing the courier's position, heading, the clock, stars, cash or the active contract in emulator memory, and played with ordinary button presses: driving along real streets, walking into doors, riding the CN Tower's elevator, delivering, talking, fighting, swimming. People in the street shots (the busker, the neighbour with a parcel tip, the goose, the road rager) are found in the ordinary crowds, not placed. The CN Tower sequence moves the courier past the lobby's ropes between three clips; the cut hides the move. The songs are recorded with sound effects held off by memory writes.

## Structure

- The city and the story (0:00–0:32, title theme, a cut every two-second bar): the title skyline, "TORONTO.", letterboxed drives and walks (Front St at Union Station at golden hour, Chinatown, the 501 on Queen St in the rain, Parkside Dr by High Park, King St at night, the Danforth at dawn, the Islands) with the opening radio calls between them.
- The work (0:32–1:04): "WIN THE FESTIVAL CONTRACT. OR LOSE THE DEPOT.", the first contract from the job board to St Lawrence Market, the CN Tower elevator to the Sky Desk, the art gallery, the museum, the Eaton Centre, Dragon City, BYTE BARN, the Gallery, a busker, a neighbour's tip and a goose.
- The trouble (1:04–1:31, chase theme, a cut every bar of 1.5 s): Vance's line, the police helicopter over the car and over the courier on foot, a night pursuit, a street fight, a haymaker, the pistol, the tank, a crash, a shark, the spray bay, then Margo's "SHOW THEM WHO DELIVERS THIS CITY."
- The logo (1:31–1:40): the title screen and the platforms.

Every line of dialogue is the game's own (radio lines and `content/story.json`); the festival tag line restates the premise in `content/story.json`.
