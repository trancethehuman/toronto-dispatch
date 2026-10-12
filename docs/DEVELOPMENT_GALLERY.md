# Development gallery

Screenshots and iteration notes from historical builds. Dates, build identities and staging details belong to each entry; see the [testing record](../TESTING.md) for verification and the [README](../README.md) for getting started.

![Title](screenshots/overhaul-title.png) ![Union Station at the new scale](screenshots/overhaul-union.png) ![Pause menu](screenshots/overhaul-pause.png) ![City map](screenshots/overhaul-map.png)

![Before: a car at 45 degrees](screenshots/overhaul-before-turning.png) ![After: full size through the turn](screenshots/overhaul-turning.png) ![Before: Queen and Spadina](screenshots/overhaul-before-scale.png) ![After: wider sidewalks, bigger blocks](screenshots/overhaul-scale.png)

![Running](screenshots/overhaul-running.png) ![Swimming, and a shark](screenshots/overhaul-shark.png) ![Police helicopter](screenshots/overhaul-heli.png) ![Rain](screenshots/overhaul-rain.png) ![A cloud and its shadow](screenshots/overhaul-cloud.png) ![Morning sun](screenshots/overhaul-sun.png)

Overhaul, 2026-10-10: the city drawn at double scale in sixteen scenes (blocks several screens across, 16 px sidewalks), heavier and slower driving with tail slides and clipping contacts, A and B together to get out, cars that keep their size through a turn, running, swimming with sharks, projectile combat where both sides can miss, police cruisers, SUVs, unmarked cars and a helicopter, weather (rain, cloud and shadow, sun rays) with gulls, a two-row radio strip, a full-screen title, smaller menus and four new songs. Unmodified PyBoy frames from the candidate build (SHA-256 `2189d60d…`; the "before" frames are the main build `b105ba2a…`), staged by writing positions, stars or the clock in emulator memory; [provenance](screenshots/provenance.json).

![Before: High Park](screenshots/greenery-high-park-before.png) ![After: maples, lindens, spruces, blossom and long grass](screenshots/greenery-high-park-after.png) ![Before: Dufferin Grove](screenshots/greenery-dufferin-grove-before.png) ![After: railings, clover and mixed trees](screenshots/greenery-dufferin-grove-after.png)

![Before: Allan Gardens](screenshots/greenery-allan-gardens-before.png) ![After](screenshots/greenery-allan-gardens-after.png) ![Before: a Swansea street](screenshots/greenery-swansea-street-before.png) ![After: hedges and bushes](screenshots/greenery-swansea-street-after.png)

Greenery, 2026-10-10: a second green palette (pale lime and yellow-green beside the park greens), tree species by place (maples, honey locusts, lindens, tiered spruces, white blossom, willows by the water), front-yard hedges and white pickets, iron railings round parks, flower beds by shops, bushes beside buildings and along park paths, and clover, long grass and wildflowers on the lawns. All decoration: collision, routes and the map are unchanged, and the frame rate is the same. Unmodified PyBoy frames at 12:41 on a clear day from the candidate build (SHA-256 `06909a78…`); "before" frames are the main build `0a925319…`; [provenance](screenshots/provenance.json).

![Before: the old helicopter](screenshots/overhaul-heli.png) ![After: the police helicopter, no weapon](screenshots/police-heli-tracking.png) ![Police boat standing off](screenshots/police-boat.png) ![Boats on the harbour](screenshots/harbour-boats.png)

![Officer aims before firing](screenshots/officer-aims.png) ![The round in flight](screenshots/officer-fires.png) ![Dodge roll](screenshots/combat-roll.png) ![A garbage truck in traffic](screenshots/traffic-garbage-truck.png) ![The tank at the Moss Park Armoury](screenshots/hidden-tank-moss-park.png) ![Driving the tank](screenshots/tank-driving.png)

Police, combat and vehicles, 2026-10-10: a redrawn police helicopter with no weapon that loses the courier under roofs and canopies and searches where it last saw them; patrol cars that hang back and box in rather than tailgate; stars that drain only out of sight of every officer, car, helicopter and police boat; bystanders and drivers who run from gunfire and crashes; officers who stop and aim (flashing) before they fire; punch combos, a running tackle, a dodge roll, hit-stop and dropped magazines; slower, heavier cars; rarer, slower sharks; motorboats, sailboats and a police boat; ambulances, fire trucks, TTC buses, box trucks and garbage trucks in traffic, and six special vehicles (a tank among them) parked beside fitting landmarks, each driving differently. Unmodified PyBoy frames from the candidate build (SHA-256 `a7c67b45…`; the "before" helicopter is the overhaul candidate `2189d60d…`), staged by writing positions or stars in emulator memory; [provenance](screenshots/provenance.json).

![Before: Spadina and Dundas](screenshots/chinatown-spadina-dundas-before.png) ![After: Chinatown's signboards and the Gateway dragons](screenshots/chinatown-spadina-dundas.png) ![Before: Spadina by Dragon City](screenshots/chinatown-dragon-city-before.png) ![After: Dragon City Mall](screenshots/chinatown-dragon-city.png)

![At the door of Dragon City Mall](screenshots/door-dragon-city.png) ![Inside Dragon City](screenshots/interior-dragon-city.png) ![A Chinatown bakery and BBQ shop](screenshots/interior-chinatown-bakery.png) ![The Eaton Centre](screenshots/interior-eaton.png)

![At the door of BYTE BARN](screenshots/door-byte-barn.png) ![Inside BYTE BARN](screenshots/interior-byte-barn.png) ![The art gallery](screenshots/interior-ago.png) ![A painting's card](screenshots/interior-ago-painting.png) ![The museum's dinosaur hall](screenshots/interior-rom.png)

![The CN Tower's lobby, beacon over the elevator](screenshots/interior-cn-base.png) ![The elevator ride](screenshots/cn-elevator-ride.png) ![The LookOut, 346 m up](screenshots/interior-cn-lookout.png) ![Delivered at the Sky Desk](screenshots/cn-sky-desk-delivered.png)

![GALLERY on the pause menu](screenshots/pause-gallery.png) ![The gallery hall](screenshots/gallery-hall.png) ![A person's card](screenshots/gallery-card-3.png) ![Another room](screenshots/gallery-room-4.png) ![The art direction room](screenshots/gallery-art-direction.png) ![A plaque](screenshots/gallery-art-plaque.png)

![A street fight starts](screenshots/street-fight-starts.png) ![The wind-up](screenshots/street-fight-windup.png) ![A counter](screenshots/street-fight-counter.png) ![A haymaker](screenshots/haymaker.png) ![A Canada goose stands its ground](screenshots/goose.png) ![A neighbour's tip about a lost parcel](screenshots/street-neighbour-tip.png) ![Tipping a busker](screenshots/busker-tip.png)

People, interiors and the gallery, 2026-10-10: Chinatown on Spadina and Dundas with Dragon City Mall, its signboards and the Gateway dragons; 144 doors you can walk through (A at the door), into 17 interiors: the CN Tower, whose elevator rides to the LookOut for deliveries, the art gallery, the museum, the Eaton Centre, Union Station, Dragon City, a Chinatown bakery, BYTE BARN (a fictional electronics superstore), cafes, corner stores, diners, shops, office lobbies and pubs, with people who do what people do there (looking at paintings, patrolling, serving, eating); 56 kinds of people and animals streamed into the eight walker slots, with crowds by neighbourhood and personalities (buskers, people sitting out, tourists taking photos, joggers, toughs, pickpockets, geese); Select to talk or give; six indoor contracts; a Gallery on the pause menu with a card for every person and a room on the art direction; counters, disarming, a held haymaker and street fights. No children appear anywhere in the game. Unmodified PyBoy frames from the candidate build (SHA-256 `ff9e42ea…`; the "before" frames are the main build `164a9f65…`), staged by writing the courier's position (outside and inside), the clock, cash, stars and the active contract in emulator memory; [provenance](screenshots/provenance.json).

Trailer, 2026-10-10: a 49-second trailer cut from the game itself (PyBoy footage of the main build, the game's music and effects); it is not kept in Git, and [docs/TRAILER.md](TRAILER.md) rebuilds it from a ROM.

**Status: Prototype 7 candidate.** The native game contains sixteen linked scenes (four districts at double scale), four vehicles of your own plus six special vehicles to find and take, 94 authored contracts, 17 interiors behind 144 doors, the downtown street plan from the City of Toronto Centreline, moving pedestrians and traffic, paid scheduled subway/bus/ferry travel, a scrollable city atlas, original music/effects, and SRAM progression. Roads have 48 pixels of asphalt plus sidewalks. Prototype 4's native tests completed nine distinct jobs and kept the car moving through the previously stopping turn while acceleration stayed held. Build-specific checks also cover walking/car entry, collision and roof occlusion, transit, timeout/retry, pause and reset recovery. The two-hour release target, full Old Toronto coverage, physical cartridge testing and further handling polish remain open.

![Financial District](screenshots/district-financial.png) ![MaRS and Hospital Row](screenshots/district-discovery.png) ![The ROM and the Gardiner Museum](screenshots/district-museums.png) ![Convocation Hall](screenshots/district-convocation-hall.png)

![King St theatres and Roy Thomson Hall](screenshots/district-entertainment.png) ![Kensington and Chinatown](screenshots/district-kensington-chinatown.png) ![St James Cathedral and St James Park](screenshots/district-st-james.png) ![Little Portugal and Little Italy](screenshots/district-little-italy-portugal.png)

![CityPlace and the Queens Quay boardwalk](screenshots/district-cityplace-waterfront.png) ![Greektown on the Danforth](screenshots/district-greektown.png) ![A junction and the neighbourhood](screenshots/nav-junction.png) ![A landmark](screenshots/nav-landmark.png)

![Before: Financial District](screenshots/before-district-financial.png) ![After](screenshots/district-financial.png) ![Before: University Ave at College](screenshots/before-district-discovery.png) ![After](screenshots/district-discovery.png)

Districts and navigation, 2026-10-07: the Financial District's black, gold and red granite towers; MaRS on College with Toronto General's helipad and Hospital Row; the ROM's Crystal and the Gardiner Museum across Queen's Park; Convocation Hall's dome at U of T; the King St theatres and Roy Thomson Hall; Chinatown's signboards beside Kensington's painted houses; St James Cathedral and its park; Little Portugal's blue houses and Little Italy's awnings; CityPlace and the Queens Quay boardwalk; Greektown on the Danforth. Sidewalks now have curbs, joints, lamps, street trees, benches and bike rings. Driving names each junction, landmark and neighbourhood ("SPADINA & DUNDAS", "ALEXANDRA PARK"). The last row compares the previous build. Unmodified PyBoy frames, staged by writing the car's position in emulator memory; [provenance](screenshots/provenance.json).

![Queen's Park from College St](screenshots/qp-legislature.png) ![Inside Queen's Park](screenshots/qp-park.png) ![The crescent's north end and the ROM](screenshots/qp-north.png) ![Driving onto the park](screenshots/qp-drive-onto-lawn.png)

![Trinity Bellwoods](screenshots/trinity-bellwoods.png) ![Allan Gardens](screenshots/allan-gardens.png) ![Grange Park](screenshots/grange-park.png) ![Sorauren Park](screenshots/sorauren-park.png)

![Grenadier Pond](screenshots/high-park-pond.png) ![High Park zoo](screenshots/high-park-zoo.png) ![Withrow Park](screenshots/withrow-park.png) ![Greenwood Park](screenshots/greenwood-park.png)

![Before: Queen's Park](screenshots/before-qp-legislature.png) ![After](screenshots/qp-legislature.png) ![Before: Allan Gardens](screenshots/before-allan-gardens.png) ![After](screenshots/allan-gardens.png)

Parks, 2026-10-07: Queen's Park as the ring of Queen's Park Crescent round the Legislative Building and the park with the King Edward VII statue (from the City Centreline, drawn about three times wider than true scale), a car crossing the crescent onto the lawn (flat ground is drivable everywhere), Trinity Bellwoods' gates and dog bowl, the Allan Gardens Palm House, The Grange, Sorauren Park's pitch and fieldhouse, Grenadier Pond, the High Park zoo's bison paddocks, Withrow Park's diamond and rink and Greenwood Park's pool. The last row compares the previous build. Unmodified PyBoy frames, staged by writing the car's position in emulator memory; [provenance](screenshots/provenance.json).

![Animated harbour by Centre Island](screenshots/water-islands.png) ![The Don](screenshots/water-don.png) ![Lake Ontario in the West scene](screenshots/water-west.png) ![Yonge-Dundas screen](screenshots/screen-yonge-dundas.png)

![Spray bay nearby](screenshots/spray-near.png) ![Resprayed](screenshots/spray-done.png) ![A lost parcel on the lawn](screenshots/parcel-seen.png) ![Lost parcel found](screenshots/parcel-found.png)

![Spray bay on The Queensway](screenshots/spray-done-queensway.png) ![Bloor West Village bay and Rosa's hint](screenshots/spray-near-bloor-west.png) ![Spray bay on Queen St East](screenshots/spray-done-queen-east.png) ![Lost parcels on the pause menu](screenshots/pause-parcels.png)

![Before: UI glyphs on the harbour](screenshots/before-water-islands.png) ![After](screenshots/water-islands.png) ![Before: glyphs on Front St roofs](screenshots/before-roofs-front-st.png) ![After](screenshots/roofs-front-st.png)

Gameplay and scenery, 2026-10-07: animated ripple water in every scene, with foam and sand at the shore; the video screen at Yonge and Dundas; a spray bay (one in each area), which clears the stars for $25; one of the 20 lost parcels; the bays on The Queensway, Bloor St West and Queen St East, with Rosa's hint; and the lost-parcel count on the pause menu. The last row compares the previous build with this one. The previous build showed UI glyphs on the water and on some roofs, because the UI art overwrote part of the core tileset; that is fixed. Unmodified PyBoy frames, some staged by writing position, cash or stars in emulator memory; [provenance](screenshots/provenance.json).

![Contract briefing](screenshots/story-briefing.png) ![Sal answers on delivery](screenshots/story-client.png) ![A contract waits for the story](screenshots/story-locked.png) ![A chapter opens](screenshots/story-chapter.png)

![Dev of Rushly](screenshots/story-rival.png) ![Margo's answer to Vance](screenshots/story-torn.png) ![Dev quits Rushly](screenshots/story-dev-quits.png) ![Dev at the depot](screenshots/story-dev-joins.png)

Story overhaul, 2026-10-07: Rosa's briefing, the client answering on delivery, a contract waiting for the story ("AFTER JOB 7"), Margo opening the second chapter, Dev of Rushly, Margo's answer to Vance, and Dev quitting Rushly and answering under the depot's card. Unmodified PyBoy frames; progress was staged by writing deliveries, completed contracts and the car's position in emulator memory, as listed in the [provenance](screenshots/provenance.json).

![Driving with nothing to report](screenshots/hud-none-driving.png) ![A new street](screenshots/hud-street-name.png) ![A new job](screenshots/hud-job-accepted.png) ![A shot shows ammunition](screenshots/hud-shot-ammo.png)

Pop-up HUD, 2026-10-07: nothing covers the city until there is something to say. Unmodified PyBoy frames (one staged by writing the car's position); [provenance](screenshots/provenance.json).

![Union Station on Front St](screenshots/union-station-front-st.png) ![CN Tower and Rogers Centre](screenshots/cn-tower-rogers-centre.png) ![City Hall and the Eaton Centre](screenshots/city-hall-eaton-centre.png) ![Kensington and Chinatown](screenshots/kensington-chinatown.png)

![Station prompt](screenshots/station-prompt.png) ![501 Queen streetcar](screenshots/queen-streetcar.png) ![Ferry arriving](screenshots/ferry-arriving.png) ![Larger cars](screenshots/bigger-cars-traffic.png)

Development build, 2026-10-07: the downtown street plan from the City of Toronto Centreline with neighbourhood blocks and landmarks in place, the station prompt, the 501 pulling in, the ferry coming in over the harbour and the larger cars. Unmodified PyBoy frames (some staged by writing the courier's position in emulator memory); [provenance](screenshots/provenance.json).

![Rosa's welcome call](screenshots/radio-welcome.png) ![Pause menu](screenshots/pause-menu.png) ![Pause menu scrolled](screenshots/pause-menu-scrolled.png) ![Dispatch board](screenshots/dispatch-board.png)

![Job briefing and distance](screenshots/job-briefing.png) ![Lock-on](screenshots/lock-on.png) ![Tracer round](screenshots/tracer-flight.png) ![Smoking engine](screenshots/engine-smoke.png) ![Stolen car at night](screenshots/night-stolen-car.png)

Development build: Rosa's radio calls, the pause menu and dispatch board as bottom sheets, a contract briefing with the distance readout, pistol lock-on and a long tracer round, a damaged car smoking and a stolen blue car with its own headlamp beam at night. Some frames are staged by writing car damage, paint or the play clock in emulator memory, as listed in the [provenance](screenshots/provenance.json).

![Title screen](screenshots/title-screen.png) ![Driving HUD](screenshots/driving-hud.png)

![Golden hour](screenshots/golden-hour.png) ![Dusk with headlamps](screenshots/dusk-headlamps.png) ![Night](screenshots/night-headlamps.png) ![Dawn](screenshots/dawn.png)

![Brake smoke](screenshots/brake-smoke.png) ![Pickup pop](screenshots/pickup-pop.png) ![Parcel pickup](screenshots/parcel-pop.png) ![Patrol light bar](screenshots/police-lightbar.png)

Development build: title, driving camera and the pause clock; the day/night cycle (golden hour, dusk, night, dawn); tyre smoke, a pickup and a parcel popping up and the patrol car's light bar. PyBoy frames, unmodified; some are staged by writing the play clock or position in emulator memory, as listed in the [provenance](screenshots/provenance.json).

![Native city atlas](screenshots/city-atlas.png)

Unmodified Prototype5 native emulator frame; [provenance](screenshots/provenance.json).
