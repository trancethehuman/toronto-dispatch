# Toronto Dispatch

An open-source courier adventure for **Game Boy Color and ModRetro Chromatic**, built with GB Studio and an original C engine extension.

Work a shift in a pixel-art Toronto: deliver packages, weave through traffic, park and explore on foot. Visit neighbourhoods and interiors, ride transit, meet the locals, and see where the city takes you.

![Toronto Dispatch title](docs/screenshots/overhaul-title.png) ![High Park](docs/screenshots/greenery-high-park-after.png) ![CN Tower LookOut](docs/screenshots/interior-cn-lookout.png)

**A playable work in progress.** Current source includes four compressed Toronto districts, 94 courier contracts, interiors, day/night weather, original music and saved progression. Releases are snapshots and may lag behind `main`. See the [roadmap](ROADMAP.md) and [testing record](TESTING.md) for progress.

## Play

Download a ROM bundle from [GitHub Releases](https://github.com/trancethehuman/toronto-dispatch/releases), or [build the current source](docs/BUILD.md). ROMs are generated artifacts and are not committed to this repository.

Use a Game Boy Color-compatible emulator, or follow the [Chromatic loading guide](docs/LOADING.md) for the supported writable development cartridge.

| Action | Controls |
| --- | --- |
| Drive | A accelerates; left/right steer; B brakes and reverses |
| Park and get out | Stop, then hold A + B |
| Walk / run | D-pad; hold A while moving to run |
| Interact | Select for dispatch, deliveries and street conversations; A at doors or the parked car |
| Pause, map and save | Start opens the menu |

First shift: accept the first contract at the Union depot, collect the parcel with Select, then head east along Front Street to St. Lawrence Market. Stop at the marker and press Select to deliver.

[Full controls and gameplay guide →](docs/PLAYING.md)

## Remix it

**Fork it and make it your own.** Build your own city, write a new courier story, change the driving feel, draw new characters, or swap in your own music. The editable project, engine, content and art generators are all here.

Original code, art and music are [MIT licensed](LICENSE). Keep the licence and applicable [third-party notices](THIRD_PARTY_NOTICES.md) with your remix; include the [ROM notices](docs/ROM_NOTICES.txt) when distributing a compiled game.

Remixes do not have to come back as pull requests. If you make something, share a link or screenshots in a [GitHub issue](https://github.com/trancethehuman/toronto-dispatch/issues). We'd love to see what you build.

## Build and contribute

```sh
git clone https://github.com/trancethehuman/toronto-dispatch.git
cd toronto-dispatch
python3 -m pip install -r requirements-dev.txt
make check
```

Repository checks need Python 3.10+, Make and Clang or GCC with sanitizer support. They validate content and host engine behaviour; they do not build the ROM.

For ROM builds, select `project/project.gbsproj` with the **ModRetro Chromatic plugin** and follow the [build guide](docs/BUILD.md). The tested toolchain uses GB Studio CLI 4.3.2 and GBDK 4.5.0.

Bug reports, playtesting, documentation, original art and focused code changes are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for the workflow.

| Where | What's inside |
| --- | --- |
| [project/](project/) | Editable GB Studio project, assets and native engine extension |
| [content/](content/) | Contracts, dialogue, world and art specifications |
| [scripts/](scripts/) | Generators and validation tools |
| [tests/](tests/) | Host engine and content tests |
| [docs/](docs/) | Build, hardware, research and implementation guides |

## More

- [Design](DESIGN.md) · [Roadmap](ROADMAP.md) · [Decisions](DECISIONS.md)
- [Development gallery](docs/DEVELOPMENT_GALLERY.md) · [Audio](docs/AUDIO.md) · [Trailer](docs/TRAILER.md)
- [Toronto research](docs/TORONTO_RESEARCH.md) · [Test evidence](TESTING.md)

An independent homebrew project, unaffiliated with ModRetro, Nintendo, the City of Toronto or the TTC.
