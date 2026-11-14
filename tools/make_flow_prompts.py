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
        "jump": "rainy street with shiny puddles on the road, light rain, umbrellas at the sides",
        "squat": "autumn park path with low tree branches arching overhead, falling leaves",
        "knees": "long colorful school hallway with lockers on both sides, deep perspective",
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
    for v in sys.argv[1:] or list(SCENES):
        write(v)
