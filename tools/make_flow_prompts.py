"""Write the Google Flow prompt pack: flow_prompts/<version>.md (one prompt per timeline part).

  python tools/make_flow_prompts.py            # both versions
  python tools/make_flow_prompts.py school     # just one

Each prompt = STYLE prefix + scene + COMMON suffix. The order in the file is the order the
owner should download clips in, because `make_video.py <version> --import-flow` matches clips by that order.
"""
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

STYLE = {
    "school": "Realistic live-action video, real-world location, natural daylight, bright cheerful colors, cinematic and sharp.",
    "japan": "Realistic live-action video filmed in Japan, real-world location, natural light, soft warm colors, cinematic and sharp.",
}
COMMON = ("Wide shot, eye level, locked-off static camera, only gentle ambient motion (light, leaves, people far away "
          "at the sides). Keep the CENTER of the frame empty and uncluttered, open floor in the "
          "middle for a dancer to be added later. No text, no logos, no captions, no one looking at the camera. 16:9.")
ANIMAL_KIDS = ("Background characters: cute cartoon animal classmates (bunnies, bear cubs, puppies) "
               "at the far left and right edges.")

SCENES = {
    "school": {
        "intro": "sunny morning outside a friendly red-brick primary school, colorful bunting, children waving far away at the sides",
        "c1": "cozy town street at sunrise, a yellow school bus far away",
        "stretch": "cozy kid's bedroom at sunrise, alarm clock ringing on a nightstand at the side, sunlight through the window",
        "run": "town sidewalk, yellow school bus parked at the right with doors open, children boarding far away",
        "jump": "empty quiet town street in light rain, shiny puddles on the road, a few umbrellas far away at the edges, no people in the middle",
        "squat": "autumn park path with low tree branches arching overhead, falling leaves",
        "knees": "long empty colorful school hallway with lockers on both sides, deep perspective, no people",
        "star": "bright classroom, chalkboard and desks at the sides, students cheering at the edges",
        "freeze1": "classroom with a teacher at the chalkboard on the right, facing the board",
        "books": "cozy school library, tall bookshelves on both sides, a few books tumbling off a shelf at the side",
        "frog1": "indoor school gym, wooden floor, basketball hoop, green mats",
        "c2": "sunny school playground, wide establishing shot",
        "tag": "playground, children chasing each other far away at the edges",
        "hop": "playground with a chalk hopscotch drawn on the ground in the foreground center",
        "hide": "playground with bushes and a slide, children peeking from hiding spots at the edges",
        "carousel": "colorful playground carousel turning slowly in the background",
        "redlight": "grassy field with a traffic light on a pole on the right side",
        "bridge": "wooden rope bridge in an adventure playground",
        "ball": "grassy school field, a colorful ball flying in the air",
        "swing": "playground swings gently moving at the sides",
        "water1": "shady tree, water fountain and water bottles on a bench",
        "c3": "sports day: colorful bunting over a running track, fans in the stands",
        "sprint": "red running track with white lanes leading into the distance, finish line",
        "hurdles": "running track with hurdles lined up into the distance",
        "defense": "outdoor basketball court at sunset",
        "shot": "basketball hoop and net against a blue sky",
        "goalie": "soccer goal net on green grass, ball flying toward the goal",
        "cheer": "stadium stands full of cheering fans waving flags",
        "relay": "relay race track, a baton on the ground, teams at the sides",
        "start": "starting line on a track, starting blocks, morning light",
        "c4": "big city skyline at sunset, glowing sky",
        "herorun": "city rooftop at sunset, kids in superhero capes far away at the sides",
        "punch": "boxing training gym, punching bags at the sides",
        "fly": "above the clouds at golden hour, birds flying",
        "climb": "giant rocky mountain wall with colorful handholds",
        "herokick": "wheat field at sunset with hay bales",
        "superjump": "trampoline park with glowing lights",
        "lasers": "futuristic training room, red laser beams at the sides",
        "statue": "city plaza with bronze statues on pedestals at the sides",
        "water2": "calm park bench with water bottles, sunset light",
        "c5": "peaceful meadow at sunset",
        "breathe1": "calm beach at sunset, gentle waves",
        "circles": "flower garden swaying in warm evening light",
        "toes": "grassy hill under a pastel sky",
        "side": "quiet lake with reflections at dusk",
        "flamingo": "pond with pink flamingos standing at the sides",
        "breathe2": "starry night sky over a calm field",
        "outro": "fireworks over the school at night, confetti",
    },
    "japan": {
        "intro": "Japanese town street, Mt Fuji in the distance, cherry blossoms",
        "c1": "Tokyo street at sunrise",
        "stretch": "tatami room, sliding shoji doors open to a sunrise view of Mt Fuji",
        "train": "Tokyo train station platform, a train arriving at the side",
        "gap": "clean Tokyo subway platform, train doors open at the sides",
        "shibuya": "big scramble crossing in Tokyo, crowds far away",
        "neon": "Tokyo street at night with colorful neon signs",
        "crowd": "busy shopping street with paper lanterns",
        "school": "Japanese school crosswalk, pedestrian traffic light on the right",
        "bow": "entrance gate of a Japanese school, cherry trees",
        "c2": "bamboo forest at dawn, mist",
        "sneak": "dense bamboo forest with light rays",
        "nkick": "wooden dojo, tatami floor, scrolls on the walls",
        "npunch": "temple courtyard with stone lanterns",
        "nbalance": "koi pond with stepping stones and a red bridge",
        "stars": "temple garden, colorful temari balls at the sides",
        "nclimb": "tall Japanese castle stone wall",
        "statue": "temple with stone guardian statues at the sides",
        "water1": "bamboo water fountain in a zen garden",
        "c3": "cherry blossom park in full bloom",
        "sakurarun": "path lined with cherry trees, petals falling",
        "petals": "cherry blossom branches, petals drifting down",
        "river": "calm river with stepping stones and cherry trees",
        "relay": "school sports field with colorful flags strung overhead",
        "hurdles": "school track with hurdles and bunting",
        "fly": "cherry petals swirling in the wind over a hill",
        "cheer": "school sports day crowd with red and white headbands, cheering",
        "frog": "lily pond with frogs on lily pads",
        "c4": "summer festival street at dusk with red lanterns",
        "taiko": "festival stage with large taiko drums",
        "bon": "festival square, lantern-decorated tower, dancers circling far away",
        "lantern": "sky lanterns floating up at dusk over a river",
        "fireworks": "night sky full of colorful fireworks over a river",
        "tower": "Tokyo tower glowing at night",
        "goldfish": "festival game stalls with goldfish tubs and lights",
        "festjump": "fireworks over a festival crowd",
        "water2": "festival stall with cold drinks and lanterns",
        "c5": "Mt Fuji at sunset over a lake",
        "breathe1": "lake with Mt Fuji reflection, calm water",
        "circles": "zen garden with raked sand at sunset",
        "toes": "green tea field on rolling hills",
        "side": "calm hot spring with steam, evening",
        "crane": "red-crowned cranes standing in a snowy marsh at the sides",
        "breathe2": "fireflies over a rice field at night",
        "outro": "fireworks over Mt Fuji, cherry petals",
    },
}

# ---------------- new themes (timelines written by tools/new_timelines.py)
STYLE.update({
    "jungle": "Realistic live-action nature video, tropical rainforest, natural sunlight through the leaves, lush green colors, cinematic and sharp.",
    "space": "Realistic cinematic sci-fi film shot, photoreal space and planet scenery, soft glowing light, cinematic and sharp.",
    "ocean": "Realistic underwater and beach nature video, clear turquoise water, sun rays, bright natural colors, cinematic and sharp.",
})
SCENES["jungle"] = {
    "intro": "wide jungle clearing at sunrise with a dirt path into the rainforest, safari jeep far away at the side",
    "c1": "dense rainforest canopy seen from above at sunrise, mist between the trees",
    "stretch": "jungle clearing at sunrise, tall trees at both sides, soft light rays",
    "jeep": "dirt safari road through the jungle, an open safari jeep parked at the right side",
    "vines": "jungle path with hanging vines overhead, green leaves at both sides",
    "logs": "jungle trail with fallen mossy logs lying across the path into the distance",
    "mud": "muddy jungle trail with puddles, big leaves at both sides",
    "parrot": "colorful macaw parrots perched on branches at the left and right edges, rainforest background",
    "tiger": "jungle clearing with a tiger resting far away at the right edge among tall grass",
    "frog1": "rainforest floor with big green leaves, a small tree frog on a leaf at the side",
    "c2": "lush green rainforest valley with a waterfall far away",
    "bunny": "grassy jungle meadow with small rabbits at the far edges",
    "monkey": "rainforest trees with monkeys sitting on branches at the left and right edges",
    "flamingo": "shallow lagoon with pink flamingos standing at the left and right sides",
    "gorilla": "jungle clearing with a gorilla sitting far away at the left edge in the shade",
    "kangaroo": "open grassland at the edge of the forest, kangaroos far away at the sides",
    "croc": "muddy riverbank, a crocodile lying far away at the right edge",
    "coconuts": "tropical palm grove with coconuts hanging from the palm trees at both sides",
    "leopard": "tall savanna grass and acacia trees, a leopard resting on a branch at the far right",
    "water1": "clear jungle stream with smooth rocks, calm and shady",
    "c3": "wide jungle river winding through the rainforest, seen from above",
    "stones": "jungle river with flat stepping stones across the water",
    "riverrun": "sandy river bank along a wide jungle river, trees at both sides",
    "rocks": "wet mossy rocks along a jungle stream",
    "waterfall": "tropical waterfall falling into a pool, rocks at both sides",
    "hippo": "muddy river with hippos far away at the left and right edges",
    "toucan": "toucan birds perched on branches at the edges, rainforest canopy behind",
    "crocfreeze": "calm river bank with a sleeping crocodile far away at the left edge",
    "splash": "shallow jungle pool with gentle splashing water",
    "c4": "giant rainforest trees seen from below, sunlight through the canopy",
    "tree": "huge rainforest tree trunk with thick roots, ferns at both sides",
    "bananas": "banana trees with yellow banana bunches hanging at both sides",
    "vineswing": "long hanging vines between tall trees, open space in the middle",
    "jkick": "huge tropical leaves at both sides of a jungle path",
    "treefrog": "close view of a wide mossy branch with small tree frogs at the ends",
    "bees": "flowering jungle bushes with bees buzzing at the sides",
    "statue": "ancient stone ruins covered in vines in the jungle, statues at both sides",
    "party": "jungle clearing with colorful birds and butterflies flying at the edges",
    "water2": "calm jungle stream with a small waterfall, evening light",
    "c5": "rainforest at sunset, warm golden light over the trees",
    "breathe1": "calm misty jungle lake at sunset",
    "circles": "butterflies fluttering over jungle flowers at the edges",
    "toes": "sloth hanging from a branch at the far right edge, soft evening light",
    "side": "palm trees gently swaying on a tropical beach at sunset",
    "still": "heron standing in a calm lagoon at the edge, golden evening light",
    "breathe2": "fireflies glowing in the jungle at dusk",
    "outro": "sunset over the rainforest canopy, birds flying",
}
SCENES["space"] = {
    "intro": "rocket on a launch pad at dawn, launch tower at the side, wide open concrete ground",
    "c1": "astronaut training center hangar with a big rocket far away",
    "stretch": "bright astronaut training room with space suits hanging on the walls at both sides",
    "suit": "bright astronaut training room with space suits hanging on the walls at both sides",
    "rocket": "wide concrete path leading to a tall rocket on the launch pad",
    "countdown": "mission control room with screens at both sides, open floor in the middle",
    "launch": "rocket lifting off far away with bright flames and smoke clouds",
    "zerog": "inside a space station module, floating objects at the edges, Earth through a window",
    "stars": "starry night sky over a desert, milky way",
    "control": "mission control room with big screens and consoles at the sides",
    "moonfrog": "grey moon surface with small rocks, Earth rising on the horizon",
    "c2": "the moon seen from space, craters, black sky",
    "moonhop": "flat grey moon surface, black starry sky, Earth in the sky",
    "craters": "moon surface with round craters into the distance",
    "buggy": "moon surface with a lunar rover parked at the right side",
    "lowgrav": "smooth moon plain with distant mountains, black sky",
    "moonrocks": "moon surface with scattered rocks, black starry sky",
    "alien": "moon base with glowing domes at the left and right sides",
    "ladder": "lunar lander with a ladder at the side, moon surface",
    "flag": "moon surface with a flag far away at the right side",
    "water1": "space station window with a calm view of Earth",
    "c3": "asteroid field in space, rocks floating, distant sun",
    "asteroids": "spaceship window view of floating asteroids at the sides",
    "smash": "big rocky asteroids floating in space at the left and right edges",
    "duck": "space debris floating at the edges, blue planet below",
    "comet": "bright comet with a long glowing tail across a starry sky",
    "ship": "view from a spaceship cockpit flying through stars",
    "redalert": "spaceship corridor with red alert lights at the sides",
    "hyper": "stars stretching into light streaks, hyperspace tunnel",
    "meteor": "meteor shower over a rocky planet surface",
    "c4": "colorful alien planet with two moons in the sky",
    "aliendance": "alien planet landscape with glowing plants at both sides",
    "bouncy": "soft purple alien planet ground with round glowing rocks at the sides",
    "robot": "futuristic robot factory hall, robot arms at both sides",
    "crystal": "giant glowing crystal mountains on an alien planet",
    "catchstars": "shooting stars across a purple sky over an alien desert",
    "march": "futuristic city street with tall towers at both sides",
    "maze": "futuristic training hall with glowing blue lines on the walls",
    "statue": "alien plaza with tall stone statues at both sides",
    "water2": "spaceship lounge with a big window showing a colorful nebula",
    "c5": "Earth seen from space at sunrise, glowing atmosphere",
    "breathe1": "calm view of Earth turning slowly from space",
    "circles": "planets orbiting a bright sun, wide view of the solar system",
    "toes": "sparkling moon dust on the moon surface, soft light",
    "side": "satellite with solar panels floating above Earth at the side",
    "still": "single bright star in a calm night sky over mountains",
    "breathe2": "peaceful starry sky over a calm lake at night",
    "outro": "space shuttle landing on a runway at sunset",
}
SCENES["ocean"] = {
    "intro": "sunny tropical beach with turquoise water and palm trees at both sides",
    "c1": "turquoise ocean waves rolling onto a white sand beach",
    "starfish": "wet sand beach at low tide with starfish at the edges",
    "beach": "path through beach grass leading to the sea",
    "waves": "gentle waves washing onto the beach, foam on the sand",
    "dive": "boat deck view of clear blue water, sun rays",
    "splashy": "shallow clear water over white sand",
    "stars": "sandy sea floor with orange starfish at the edges",
    "shark": "underwater blue ocean with a shark swimming far away at the left edge",
    "frogfish": "colorful coral with small fish at the sides",
    "c2": "colorful coral reef seen from above in clear water",
    "crab": "beach rocks with small red crabs at the edges",
    "seahorse": "seagrass meadow underwater with seahorses at the sides",
    "bubbles": "underwater scene with bubbles rising at both sides, sun rays",
    "rock": "big smooth rock in a calm shallow lagoon",
    "octopus": "underwater rocky reef with an octopus at the far right edge",
    "dolphin": "dolphins swimming far away in clear blue water",
    "coral": "tall coral reef wall with colorful fish at both sides",
    "fishparty": "schools of colorful tropical fish swimming at the edges of a reef",
    "water1": "calm beach under palm trees, shade, gentle waves",
    "c3": "deep blue ocean with light rays from the surface",
    "seaweed": "underwater kelp forest with tall seaweed at both sides",
    "manta": "manta ray gliding far away in deep blue water",
    "jelly": "glowing jellyfish floating at the left and right edges in dark blue water",
    "race": "open blue ocean surface with dolphins jumping far away",
    "leap": "dolphins leaping out of the water far away at sunset",
    "seabed": "sandy sea floor with shells and small rocks, light rays",
    "statue": "sunken ancient stone statues on the sea floor at both sides",
    "turtle": "sea turtle swimming far away over a coral reef",
    "c4": "old sunken pirate ship on the sea floor",
    "map": "sandy beach with a palm tree and a wooden treasure chest at the side",
    "wreck": "wooden shipwreck covered in coral at the side, fish around",
    "coins": "sea floor with scattered gold coins sparkling in light rays",
    "chests": "sea floor with wooden treasure chests at the sides",
    "pirate": "deck of an old wooden pirate ship, ropes and barrels at the sides",
    "anchor": "big rusty anchor on the sea floor at the side, seaweed",
    "pfreeze": "pirate ship deck with a ship wheel at the far right side",
    "treasure": "open treasure chest full of gold at the side, sparkling light",
    "water2": "calm lagoon at sunset, palm trees",
    "c5": "ocean sunset with calm water",
    "breathe1": "slow bubbles rising in calm blue water",
    "circles": "jellyfish drifting slowly in soft blue light at the edges",
    "toes": "smooth white sand with gentle ripples underwater",
    "side": "seaweed swaying gently in calm water",
    "still": "starfish on a rock in a calm tide pool",
    "breathe2": "calm ocean at night under the moon",
    "outro": "dolphins jumping at sunset over the ocean",
}


# ---------------- reaction clips: real people/animals "reacting to the kids" (used by every video)
# Pop up as a framed reaction-cam: every 10 hits (praise), at mission complete, at the intro and the outro.
STYLE["reactions"] = ("Realistic live-action video, bright natural light, cheerful, shallow depth of field, "
                      "subject centered, looking straight into the camera as if reacting to the viewer.")
REACTIONS = {
    "r_wave": "a smiling little girl waving hello at the camera with both hands, colorful classroom behind her",
    "r_bye": "two happy kids waving goodbye at the camera, sunny playground behind them",
    "r_cheer": "a group of happy kids cheering and jumping with arms up, looking at the camera, school gym",
    "r_clap": "a smiling boy clapping his hands excitedly toward the camera, bright living room",
    "r_thumbs": "a cheerful girl giving two thumbs up to the camera and nodding, sunny park",
    "r_wow": "a kid with a surprised amazed face, mouth open saying wow, hands on cheeks, looking at the camera",
    "r_laugh": "a little boy laughing happily at the camera, bright kitchen behind him",
    "r_dance": "a girl doing a happy little dance and smiling at the camera, colorful bedroom",
    "r_highfive": "a smiling boy reaching his open hand toward the camera for a high five, playground",
    "r_coach": "a friendly young sports coach in a tracksuit smiling and giving a thumbs up to the camera, school gym",
    "r_cat": "a cute orange cat looking curiously at the camera and tilting its head",
    "r_dog": "a fluffy puppy tilting its head and wagging its tail, looking at the camera",
    "r_trophy": "a happy kid lifting a shiny golden trophy and celebrating, confetti falling, looking at the camera",
}
REACT_COMMON = "Medium close-up, static camera, no text, no logos, no captions. 16:9. Short clip."


def load_segments(version):
    src = (ROOT / "timelines" / f"{version}.js").read_text(encoding="utf-8")
    body = src[src.index("{"): src.rindex("};") + 1]
    body = "\n".join(l for l in body.splitlines() if not l.strip().startswith(("/*", "//")))
    return json.loads(body)["segments"]


def prompt_for(version, scene):
    s = scene[0].upper() + scene[1:]
    extra = ""
    return f"{STYLE[version]} {s}.{extra} {COMMON}"


def prompt_list(version):
    """[(id, cue, prompt)] in timeline order. Used by --import-flow too."""
    if version == "reactions":
        return [(k, "REACTION", f"{STYLE['reactions']} {v[0].upper() + v[1:]}. {REACT_COMMON}") for k, v in REACTIONS.items()]
    scenes = SCENES[version]
    segs = load_segments(version)
    missing = [s["id"] for s in segs if s["id"] not in scenes]
    if missing:
        sys.exit(f"[{version}] no Flow scene written for part(s): {', '.join(missing)} - add them to SCENES")
    return [(s["id"], s.get("cue", ""), prompt_for(version, scenes[s["id"]])) for s in segs]


def write(version):
    items = prompt_list(version)
    out = ROOT / "flow_prompts" / f"{version}.md"
    out.parent.mkdir(exist_ok=True)
    lines = [
        f"# Google Flow prompts: {version} ({len(items)} clips)",
        "",
        "How to use:",
        "1. In Flow pick **Text to Video**, **16:9**, Veo **Fast** (or **Quality** for the big scenes).",
        "2. Paste one prompt, generate, keep the best clip.",
        f"3. Download it into `footage/flow_inbox/{version}/`. Go **in this order** (any file name is fine),",
        "   or rename the file to the **Save as** name, and then the order doesn't matter.",
        f"4. Run `python make_video.py {version} --import-flow`.",
        "",
        "Optional: a second clip for the same part saved as `<id>_2.mp4` is joined to the first (less looping).",
        "",
    ]
    for n, (pid, cue, p) in enumerate(items, 1):
        lines += [f"## {n}. {pid} ({cue})", "", f"**Save as:** `{pid}.mp4`", "", "```", p, "```", ""]
    out.write_text("\n".join(lines), encoding="utf-8")
    js = [{"n": n, "id": pid, "cue": cue, "save_as": f"{pid}.mp4", "prompt": p}
          for n, (pid, cue, p) in enumerate(items, 1)]
    out.with_suffix(".json").write_text(json.dumps(js, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"  wrote {out.relative_to(ROOT)} + .json ({len(items)} prompts)")


if __name__ == "__main__":
    for v in sys.argv[1:] or list(SCENES) + ["reactions"]:
        write(v)
