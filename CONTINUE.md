# CONTINUE HERE: full brief for the next session / PC

> To Claude (or any dev) picking this up: read this file top to bottom, then `HANDOFF.md`, then work through **Tasks 1→5** in order. The owner is a small-business owner (kids' play venues). Use plain, simple English with them, give the answer first, and ask short questions only when you must.

---

## 0. What this project is

- **What it makes:** 15-minute follow-along warm-up videos for kids, played on a wall projector. They'll also be cut into 3-minute videos for a faceless YouTube channel that earns money.
- **Inspired by:** the YouTube video "Back to School Immersive Interactive Warm Up" (Daniel Sfilms). That video uses AI-made story scenes plus a **simple figure with a glowing white outline** showing the moves. **Don't copy it.** Everything we make is original.
- **How it's built:**
  - `engine/index.html` draws every frame on a canvas: the character, props, on-screen text and transitions.
  - `engine/warmup.py` runs that page in a hidden Chrome (Playwright), puts the footage behind it, and makes an MP4 with ffmpeg using several workers at once.
  - `engine/synth.py` makes the soundtrack: music, sound effects and voice, all on a **120 BPM grid** (1 beat = 0.5 s), so every move lands on the beat.
- **The content** is in `timelines/school.js` and `timelines/japan.js`: a list of parts, each with `id, scene, clip, move, dur, ch, cue, story, say, jsay, jp, prop, calm`.
- **Run it** with `python make_video.py <school|japan> [--preview secs...] [--sample FROM TO] [--new-audio] [--workers N]`.

### Decisions the owner already made (don't ask again)
- **Character:** the **line character** (dark faceless figure with a glowing white outline). It's already the default (`"character": "line"`).
- **Route:** **free/low-cost**, with no paid AI video subscription. **But** the owner has lots of **Google Flow** credits, so the AI scenes come from Flow:
  - We write the prompts; the owner pastes them into Flow and downloads the clips.
  - **No browser automation of Flow.** It's against Google's terms and could get the account flagged.
- **Video:** 720p, 30 fps, small files (about 12 MB per minute).

### Owner feedback still to fix
1. "The voice is so AI." The macOS `say` voice is robotic, **and** Apple's licence doesn't allow it in monetized videos.
2. "Need better song." The generated music is too basic.
3. "Not so smooth / not seamless like the video." Already improved: pose blending, crossfades, camera drift, 30 fps. The Flow scenes (Task 1) are the big remaining step.

---

## Task 1: Google Flow prompt pack + auto-import (do this first)

### 1a. Generate `flow_prompts/school.md` and `flow_prompts/japan.md`
Write a small script, `tools/make_flow_prompts.py`, that reads a timeline plus the scene list below and writes a numbered markdown file. Each entry has:
- the number
- the part `id`
- **Save as:** `<id>.mp4`
- the prompt, in a code block so it's easy to copy

Each prompt = **STYLE prefix + scene + COMMON suffix**.

**STYLE prefixes**
- **school:** `Bright, colorful 3D animated kids' movie style, soft warm lighting, cheerful and friendly.`
- **japan:** `Soft painterly anime-style background art, Japanese setting, warm pastel colors, gentle light.` (Don't name any real studio or character; Flow may block it, and it's an IP risk.)

**COMMON suffix (both versions)**
`Wide shot, eye level, locked-off static camera, only gentle ambient motion (light, leaves, background characters far away at the sides). Keep the CENTER of the frame empty and uncluttered — open floor in the middle for a dancer to be added later. No text, no logos, no captions, no one looking at the camera. 16:9.`

**Background characters (school only)**
`cute cartoon animal classmates (bunnies, bear cubs, puppies) at the far left and right edges`. Use them only where it says *animal kids*.

#### School scenes (part id → scene)
| id | scene |
|---|---|
| intro | sunny morning outside a friendly red-brick primary school, colorful bunting, animal kids waving at the sides |
| c1 | cozy town street at sunrise, a yellow school bus far away |
| stretch | cozy kid's bedroom at sunrise, alarm clock ringing on a nightstand at the side, sunlight through the window |
| run | town sidewalk, yellow school bus parked at the right with doors open, animal kids boarding |
| jump | rainy street with shiny puddles on the road, light rain, umbrellas at the sides |
| squat | autumn park path with low tree branches arching overhead, falling leaves |
| knees | long colorful school hallway with lockers on both sides, deep perspective |
| star | bright classroom, chalkboard and desks at the sides, animal students cheering |
| freeze1 | classroom with a friendly owl teacher at the chalkboard on the right, facing the board |
| books | cozy school library, tall bookshelves on both sides, a few books floating down |
| frog1 | indoor school gym, wooden floor, basketball hoop, green mats |
| c2 | sunny school playground, wide establishing shot |
| tag | playground, animal kids chasing each other at the edges |
| hop | playground with a chalk hopscotch drawn on the ground in the foreground center |
| hide | playground with bushes and a slide, animal kids peeking from hiding spots |
| carousel | colorful playground carousel turning slowly in the background |
| redlight | grassy field with a big cartoon traffic light on the right side |
| bridge | wooden rope bridge in an adventure playground |
| ball | grassy school field, a colorful ball flying in the air |
| swing | playground swings gently moving at the sides |
| water1 | shady tree, water fountain and water bottles on a bench |
| c3 | sports day: colorful bunting over a running track, animal fans in the stands |
| sprint | red running track with white lanes leading into the distance, finish line |
| hurdles | running track with hurdles lined up into the distance |
| defense | outdoor basketball court at sunset |
| shot | basketball hoop and net against a blue sky |
| goalie | soccer goal net on green grass, ball flying toward the goal |
| cheer | stadium stands full of cheering animal fans waving flags |
| relay | relay race track, a baton on the ground, teams at the sides |
| start | starting line on a track, starting blocks, morning light |
| c4 | superhero city skyline at sunset, glowing sky |
| herorun | city rooftop at sunset, animal heroes with capes at the sides |
| punch | superhero training gym, punching bags at the sides |
| fly | above the clouds at golden hour, birds flying |
| climb | giant rocky mountain wall with colorful handholds |
| herokick | wheat field at sunset with hay bales |
| superjump | trampoline park with glowing lights |
| lasers | futuristic training room, red laser beams at the sides |
| statue | city plaza with hero statues on pedestals at the sides |
| water2 | calm park bench with water bottles, sunset light |
| c5 | peaceful meadow at sunset |
| breathe1 | calm beach at sunset, gentle waves |
| circles | flower garden swaying in warm evening light |
| toes | grassy hill under a pastel sky |
| side | quiet lake with reflections at dusk |
| flamingo | pond with pink flamingos standing at the sides |
| breathe2 | starry night sky over a calm field |
| outro | fireworks over the school at night, confetti |

#### Japan scenes (part id → scene)
| id | scene |
|---|---|
| intro | Japanese town street, Mt Fuji in the distance, cherry blossoms |
| c1 | Tokyo street at sunrise |
| stretch | tatami room, sliding shoji doors open to a sunrise view of Mt Fuji |
| train | Tokyo train station platform, a train arriving at the side |
| gap | clean Tokyo subway platform, train doors open at the sides |
| shibuya | big scramble crossing in Tokyo, crowds far away |
| neon | Tokyo street at night with colorful neon signs |
| crowd | busy shopping street with paper lanterns |
| school | Japanese school crosswalk, pedestrian traffic light on the right |
| bow | entrance gate of a Japanese school, cherry trees |
| c2 | bamboo forest at dawn, mist |
| sneak | dense bamboo forest with light rays |
| nkick | wooden dojo, tatami floor, scrolls on the walls |
| npunch | temple courtyard with stone lanterns |
| nbalance | koi pond with stepping stones and a red bridge |
| stars | temple garden, colorful temari balls at the sides |
| nclimb | tall Japanese castle stone wall |
| statue | temple with stone guardian statues at the sides |
| water1 | bamboo water fountain in a zen garden |
| c3 | cherry blossom park in full bloom |
| sakurarun | path lined with cherry trees, petals falling |
| petals | cherry blossom branches, petals drifting down |
| river | calm river with stepping stones and cherry trees |
| relay | school sports field with colorful flags strung overhead |
| hurdles | school track with hurdles and bunting |
| fly | cherry petals swirling in the wind over a hill |
| cheer | school sports day crowd with red and white headbands, cheering |
| frog | lily pond with frogs on lily pads |
| c4 | summer festival street at dusk with red lanterns |
| taiko | festival stage with large taiko drums |
| bon | festival square, lantern-decorated tower, dancers circling far away |
| lantern | sky lanterns floating up at dusk over a river |
| fireworks | night sky full of colorful fireworks over a river |
| tower | Tokyo tower glowing at night |
| goldfish | festival game stalls with goldfish tubs and lights |
| festjump | fireworks over a festival crowd |
| water2 | festival stall with cold drinks and lanterns |
| c5 | Mt Fuji at sunset over a lake |
| breathe1 | lake with Mt Fuji reflection, calm water |
| circles | zen garden with raked sand at sunset |
| toes | green tea field on rolling hills |
| side | calm hot spring with steam, evening |
| crane | red-crowned cranes standing in a snowy marsh at the sides |
| breathe2 | fireflies over a rice field at night |
| outro | fireworks over Mt Fuji, cherry petals |

### 1b. Owner's workflow in Flow
1. Open `flow_prompts/<version>.md`.
2. For each entry, in Flow: choose **Text to Video**, 16:9, Veo "Fast" to save credits (or "Quality" for hero scenes), paste the prompt, generate, and pick the best of the results.
3. Download the clip into `footage/flow_inbox/<version>/`. Clips can keep any name, but **download them in the same order as the list.**
4. Run `python make_video.py <version> --import-flow`.

### 1c. Build `--import-flow` (in `make_video.py` + `engine/warmup.py`)
- Read `footage/flow_inbox/<version>/*.mp4`, sorted by modified time (oldest first).
- Match them, in order, to the part ids in the prompt list that don't have a clip yet.
- Move each one to `footage/flow/<version>/<id>.mp4`.
- If a file's name already matches a part id, use that id instead of the order.
- Print the result as `file → id`.
- **Already supported:** `load_timeline()` replaces a part's stock clip with `footage/flow/<version>/<id>.mp4` when it exists. It also turns cartoon-scene parts into footage parts and passes `&flow=` to the page.
- **Clip length:** Veo clips are about 8 s; parts are 16–24 s. `_clip_frame()` loops clips forward and backward, which suits static-camera shots. Option: if an `<id>_2.mp4` exists, chain the two clips before looping.

---

## Task 2: Natural voice (replace macOS `say`)

- **Recommended: Kokoro TTS.**
  - Open source, **Apache-2.0** (fine for commercial use), and natural-sounding.
  - Needs **Python 3.10–3.12** (torch doesn't support 3.14), so make a separate env: `uv venv --python 3.12 .tts-venv`, then `pip install kokoro soundfile "misaki[ja]"`, and install `espeak-ng` (Windows: from espeak-ng's GitHub releases; Mac: `brew install espeak-ng`).
  - English voices: try `af_heart`, `af_bella` or `af_nicole`, and pick the friendliest for kids.
  - Japanese voices: `jf_alpha` or `jf_nezumi` (`lang_code='j'`).
- **Implementation:**
  - Add `tools/tts_kokoro.py` with arguments `text lang out.wav`, run by `.tts-venv` Python.
  - In `engine/warmup.py` → `voice_clip()`: if `.tts-venv` exists, call it; otherwise fall back to `say` / edge-tts.
  - Put the engine name in the cache key so new and old voices don't mix, e.g. `kokoro|en|text`.
- **Keep the timing** `silenceremove` trims the silence at the start of each voice line, and `round(at/BEAT)*BEAT` snaps each line to the beat.
- Speed: Kokoro at speed about 1.05–1.1, with an energetic coach tone. Then run `python make_video.py school --new-audio` (and the same for japan).
- **Other options** if the owner wants: record a real voice (we provide the script), or ElevenLabs on a paid plan (commercial rights included).
- **Remove or replace** the committed `voice_cache/*.wav` files (they're `say` voices) before any monetized upload.

---

## Task 3: Real music, synced to the beat

- **Source:** the owner downloads tracks from the **YouTube Audio Library** (YouTube Studio → Audio Library). It's the safest source for monetized videos. Filter for upbeat kids, pop or electronic tracks, about 100–130 BPM. Pick one track per chapter, plus one calm track for the cool-down.
  - Mixkit music: its licence text loads in a popup we couldn't read, so **check it before using Mixkit tracks.**
- **Folder:** `music/<version>/ch1.mp3 … ch5.mp3`, and `calm.mp3`.
- **Code** (`engine/music.py`, using `librosa`; add it to `requirements.txt`):
  1. Detect the tempo and beat times: `librosa.beat.beat_track`.
  2. Stretch to exactly **120 BPM** with ffmpeg `atempo=120/bpm` (pitch stays the same). Allow tracks from 90–150 BPM; if a track is under 90, treat it as half-time.
  3. Find the first strong downbeat and shift the track so its beats land on our 0.5 s grid at the chapter's start time.
  4. Loop or crossfade the track to fill the chapter (chapter = from its `card` part up to the next card).
  5. Mix it into `Synth.render()` in place of `music_for()`. Keep the sound effects, voice and ducking. During **freeze** beats, drop the music volume to about 5% (that's the game).
  6. Keep the old generated music as a fallback when `music/<version>/` is empty.

---

## Task 4: YouTube export (3-minute chapter videos + Shorts)

- **Command:** `python make_video.py school --chapters` makes `output/youtube/<version>_ch<N>.mp4`, one per chapter, with:
  - a 3-second intro card (title + "Stand up! Let's move!")
  - the chapter's parts
  - a 4-second outro card ("Great job! Subscribe for more")
- **Shorts (later):** a 9:16 version at 1080×1920. Render the canvas at a portrait size, move the on-screen text, and crop the footage to the centre.
- **YouTube tips for the owner:**
  - Mark every video **"Made for Kids"**.
  - Make each upload clearly different (new theme, moves and scenes) to avoid the "reused / mass-produced content" rules.
  - Search words to use in titles: "PE warm up for kids", "brain break", "classroom exercise".

---

## Task 5: Test on Windows

- Run `setup_windows.bat`, then `python make_video.py school --sample 36 96`. Check speed and look.
- The full render uses `--workers` (default: half your CPU cores). Each worker = one hidden Chrome + one ffmpeg.
- If Playwright Chromium fails to start, run `python -m playwright install chromium` again.
- **Projector:** `player/Start_Warmup.bat` (Chrome kiosk mode, sound on, loops forever; Alt + F4 to close). Not tested on Windows yet.

---

## Status table

| Item | Status |
|---|---|
| Timelines school (14.5 min) / japan (13.4 min) | ✅ done (japan could get one more part to reach 15 min) |
| Line character, smooth blending, crossfades, camera drift, 30 fps | ✅ done (pushed) |
| Generated soundtrack + beat-synced sound effects | ✅ done; music needs upgrading (Task 3) |
| Google Flow clip replacement in the engine | ✅ done |
| Flow prompt pack + `--import-flow` | ✅ done: `flow_prompts/*.md`, `tools/make_flow_prompts.py`, `--import-flow` (tested). ⏳ waiting for the owner's Flow clips |
| Natural voice (Kokoro) | ✅ done: `.tts-venv` (Python 3.12, `tools/setup_voice.bat`), voices **af_heart** (EN) + **jf_alpha** (JA), both soundtracks rebuilt, old Mac `say` voices deleted. `voice_cache/` is no longer committed (rebuilds in ~3 min) |
| Real music beat-aligned | ⏳ Task 3 |
| Chapter / Shorts export | ⏳ Task 4 |
| Windows test | ✅ setup + `--sample 36 96` work on Windows (1 min rendered in 17 s on 16 threads, 13 MB). ⏳ full render + player test |

### Files to know
- `engine/index.html`: drawing code. Moves are in `pose()`; characters are `drawLine` (default), `drawKid` and `drawHana`; then `props()`, `hud()`, and `renderAt()` with the crossfades.
- `engine/warmup.py`: timeline loading, footage download, frame extraction, rendering and voice.
- `engine/synth.py`: soundtrack.
- `make_video.py`: the command-line tool.
- `player/`: projector launcher.
- **Not in git** (made automatically on each PC): `footage/`, `.frames/`, `.parts/`, `output/`, `.tts-venv/`.
