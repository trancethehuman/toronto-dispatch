# Playing Toronto Dispatch

These controls describe the current source; published prototypes may differ. Start with the [README](../README.md) and [loading instructions](LOADING.md).

| Action | Controls |
| --- | --- |
| Accelerate / coast | Hold A / release A |
| Steer the vehicle | Left / right; brake for tighter corners |
| Brake / reverse | B; keep holding near rest to reverse |
| Accept or deliver a package | Select opens dispatch, then A accepts; Select at a beacon while stopped collects/delivers |
| Pause menu | Start; up/down scroll four actions at a time, A chooses |
| Park and exit | Stop, then hold A+B, or pause → Park / recover car |
| Walk | D-pad; A near the parked car animates entry |
| On foot | D-pad walks and aims; A beside a road vehicle takes it, otherwise punches (three quick punches knock down); hold A while moving to run; A and B together while moving rolls; B away from a stop fires at the locked-on target (red brackets), hold B to keep firing |
| Talk / give | On foot, Select beside someone: they answer; someone sitting out gets $2, a busker $1 |
| Haymaker / counter | Hold A while standing still, then release; punch while a fighter winds up (flashing red) to counter |
| Go inside | On foot, A at a named door (shown on the HUD); inside, A talks, reads and uses the elevator or desk; walk out the doors to leave |
| Gallery | Pause → Gallery; A at a plinth or plaque reads its card, arches lead between rooms |
| Pickups | Walk or drive over cash, first aid or ammunition on the pavement |
| Transit | On foot, B at a station/terminal/platform; left/right chooses destination, A waits/boards |
| Change service | Up/down at Wellesley switches Line 1 / 94 bus |
| Scrollable city map | Pause → map; D-pad pans, A centres job / booked transit stop / depot; Select changes focus, B returns |
| Change vehicle / save | Pause menu; change vehicle while stopped without an active job |
| Repair | Pause → Supplies ($20) heals, adds ammunition and repairs the car |
| Sound | Pause → Audio; cycle full music/effects, effects only, or silent |

First job: accept contract 1 at the Union depot, press Select to collect, drive east along Front Street to St. Lawrence Market, brake and press Select to deliver. The marker and HUD identify the next waypoint. Pickup is the first of the displayed stops. The 72 original contracts, plus eight western, eight eastern and six indoor jobs, have distinct routes/titles, brief instructions and twelve progression chapters. Indoor jobs end (or start) at a desk inside a building: park at the stop, walk in at its door and follow the beacon, which for the LookOut means the CN Tower's elevator. Completion unlocks truck/transit jobs, passenger work and Island walking rounds. Dispatch selects the next eligible unfinished contract. Replays pay but do not increment unique completion twice.

Transit runs on a repeating **fictional game clock**, even without the player. Fares are 3 for subway, 2 for bus and 4 for ferry; Queen also costs 3. These are game credits, not real TTC prices. At a Queen sign, choose a destination; the menu shows eastbound/westbound, departure countdown and trip cost/time. Each direction repeats every 64 seconds with a two-second boarding window, and a ride takes four seconds per selected stop interval. Choosing the current stop cannot board. Waiting/riding uses mission time; menus and the map pause it. Heavy freight and passenger jobs require their road vehicle. Parking leaves that vehicle behind for recovery. Island ferries connect through the mainland, and ordinary cars cannot reach the Islands.

Driving retains momentum through steering and glancing curb contact. A bounded sideways adjustment helps clear narrow tile corners while accelerating; broad walls still stop the vehicle. Fragile crates take greater crash damage. Fast passenger turns reduce comfort, and base rewards scale with condition. Two alternating CRC-checked save records retain a previous checkpoint if a write is interrupted. Paid rides resume from their latest second after a reset. Physical power-off persistence still needs a cartridge test.

The campaign is an original story told over the radio: Margo's independent depot against Rushly, an app courier, for the city's Lakelight festival contract. Rosa briefs each contract, clients answer on delivery, plot turns follow the contracts they belong to, and each chapter opens once the previous chapter's key contract is done (the board shows "AFTER JOB n" until then). Police warnings and city chatter fill the quiet while play continues. The screen stays clear: short pop-ups at the bottom show the next stop, street names, ammunition after a shot, changes in cash, health or car condition, and the job timer when it matters; stand still to see the status line. The car wears from crashes, smokes and loses power until repaired. Pedestrians follow fixed sidewalk routes across the four areas with eight nearby people rendered at a time, drawn from 56 people and animals that suit the neighbourhood (see the Gallery on the pause menu); road vehicles come in eight designs and seven paints, with ambulances, fire trucks, TTC buses, box trucks and garbage trucks mixed in. Traffic follows continuous loops, yields to the courier crossing on foot and keeps returning just beyond the screen edge so nearby streets stay busy. Crimes draw police attention in stars; the police chase without overwhelming speed and hang back rather than tailgate, arrests need a firm hold, officers only shoot from four stars and aim visibly first, and stars drain only while no officer, patrol car, helicopter or police boat can see the courier. Sidewalk pickups give cash, first aid or ammunition. Four original themes (title, day, night and police chase) switch with the game state; they, the engine, braking and event effects have been verified through emulator PCM capture; physical speaker/headphone testing remains open. See [audio design and reproduction](AUDIO.md).

For installation, use the [loading instructions](LOADING.md). ROM bundles require the [distribution notices](DISTRIBUTION.md). This prototype has not been verified for two hours of gameplay.
