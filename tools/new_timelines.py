"""Write theme timelines (timelines/<name>.js) from short specs: same structure as school.js.

  python tools/new_timelines.py           # jungle, space, ocean

Structure (about 15 min): intro 10 s, chapters 1-4 = card + 8 parts (20 s, freeze games 24 s), water breaks after
chapters 2 and 4, chapter 5 = calm cool-down, outro 12 s. Every move/prop used here exists in engine/index.html:
moves  wave reach run highknees jump squat starjump freeze reachside frog hop tuckjump balance kick skater punch fly
       climb armcircles toetouch sidestretch rest breathe
props  balls books branches hopscotch hurdles lasers light puddles teacher
Voice: freeze parts get automatic "Freeze!/Dance!" calls ("Statue!" when the id is "statue"), reachside gets
"Left!/Right!". Scenes come from Google Flow clips: footage/flow/<name>/<id>.mp4 (prompts: tools/make_flow_prompts.py).
To add a theme: copy one build(...) block, change the words, run this file, then add its scenes to make_flow_prompts.py.
"""
import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
W = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five"}


def part(pid, move, cue, story, lines, prop=None, ch=1, dur=None, calm=False):
    d = {"id": pid, "scene": "footage", "move": move, "dur": dur or (24 if move == "freeze" else 20), "ch": ch}
    if prop:
        d["prop"] = prop
    if calm:
        d["calm"] = True
    d["cue"], d["story"] = cue, story
    if move in ("freeze", "reachside"):
        say = [[0, lines[0]]]
    elif move == "balance":
        say = [[0, lines[0]], [8, "Switch legs!"], [16, "Switch!"]]
    elif move == "breathe":
        say = [[0, lines[0]], [4, "and out."], [8, "Breathe in..."], [12, "and out."]]
    elif move == "frog":
        say = [[0, lines[0]], [10, lines[1]], [16, lines[2]]]
    elif calm and move in ("armcircles", "toetouch"):
        say = [[0, lines[0]], [10, lines[1]]]
    elif calm and move == "sidestretch":
        say = [[0, lines[0]], [8, lines[1]]]
    else:
        say = [[0, lines[0]], [9, lines[1]], [15, lines[2]]]
    d["say"] = say
    return d


def build(meta, intro, chapters, outro):
    title, output, name = meta
    segs = [dict(id="intro", scene="footage", move="wave", dur=10, ch=1, cue=intro[0], story=intro[1],
                 say=[[0.5, intro[2]], [3, intro[3]], [7.5, "Follow me!"]])]
    for n, (ctitle, parts, water) in enumerate(chapters, 1):
        calm = n == 5
        card = dict(id=f"c{n}", scene="card", move="wave", dur=6, ch=n, cue=f"CHAPTER {n}", story=ctitle,
                    say=[[0.5, f"Chapter {W[n]}. {ctitle.title()}." if calm else f"Chapter {W[n]}! {ctitle.title()}!"]])
        if calm:
            card["calm"] = True
        segs.append(card)
        for p in parts:
            segs.append(part(**p, ch=n, calm=calm))
        if water:
            segs.append(dict(id=water[0], scene="footage", move="rest", dur=16, ch=n, calm=True, cue="WATER BREAK",
                             story=water[1], say=[[0, water[2]], [10, water[3]]]))
    segs.append(dict(id="outro", scene="footage", move="wave", dur=12, ch=5, cue=outro[0], story=outro[1],
                     say=[[0.5, outro[2]], [5, "High five! See you next time!"]]))
    ids = [s["id"] for s in segs]
    assert len(ids) == len(set(ids)), f"duplicate part ids in {name}"
    tl = dict(title=title, output=output, character="line", bpm=120, fps=30, segments=segs)
    js = (f"// {title} - 15-minute warm-up. 120 BPM (1 beat = 0.5 s). Written by tools/new_timelines.py.\n"
          f"// Scenes: Google Flow clips in footage/flow/{name}/<id>.mp4 (prompts: flow_prompts/{name}.md)\n"
          f"window.TIMELINE = {json.dumps(tl, indent=1, ensure_ascii=False)};\n"
          'if (typeof module !== "undefined") module.exports = window.TIMELINE;\n')
    (ROOT / "timelines" / f"{name}.js").write_text(js, encoding="utf-8")
    print(f"  timelines/{name}.js: {len(segs)} parts, {sum(s['dur'] for s in segs) / 60:.1f} min")


def P(pid, move, cue, story, lines, **k):
    return dict(pid=pid, move=move, cue=cue, story=story, lines=lines, **k)


def cool(pre, arms, toes, side, bal, br2):
    return [P("breathe1", "breathe", "BREATHE", pre, ["Breathe in..."], dur=16),
            P("circles", "armcircles", arms[0], arms[1], [arms[2], "Now the other way."]),
            P("toes", "toetouch", toes[0], toes[1], [toes[2], "Slowly. And up."]),
            P("side", "sidestretch", side[0], side[1], [side[2], "And the other side."]),
            P("still", "balance", bal[0], bal[1], [bal[2]]),
            P("breathe2", "breathe", "BREATHE", br2, ["One more big breath in..."], dur=16)]


def jungle():
    build(("Jungle Safari Warm-Up", "JungleSafari_WarmUp_15min", "jungle"),
          ("JUNGLE SAFARI", "Warm-up adventure! Follow me!", "Hello, explorers!",
           "Today we go on a jungle safari. Let's warm up!"),
          [("INTO THE JUNGLE", [
              P("stretch", "reach", "WAKE UP THE JUNGLE", "The sun is up! Reach for the trees!",
                ["Good morning, jungle! Reach up high!", "Stretch side to side.", "Reach for the treetops!"]),
              P("jeep", "run", "RUN TO THE JEEP", "The safari jeep is leaving!",
                ["Run to the jeep! Run on the spot!", "Faster! Faster!", "Almost there!"]),
              P("vines", "squat", "DUCK THE VINES", "Watch out for the vines!",
                ["Low vines! Squat down, and up!", "Down, and up!", "Keep your back straight!"], prop="branches"),
              P("logs", "jump", "JUMP THE LOGS", "Fallen logs on the path!",
                ["Logs! Jump over them!", "Jump! Jump!", "Big jumps!"], prop="hurdles"),
              P("mud", "highknees", "STOMP THROUGH THE MUD", "Sticky mud! Lift your knees!",
                ["Muddy path! High knees!", "Knees up high!", "Stomp, stomp, stomp!"]),
              P("parrot", "starjump", "PARROT STAR JUMPS", "The parrots are dancing!",
                ["Parrot star jumps! Arms up, legs out!", "Open, close!", "Flap those wings!"]),
              P("tiger", "freeze", "TIGER IS WATCHING!", "Dance... and FREEZE when the tiger looks!",
                ["Dance! When the tiger looks, freeze!"]),
              P("frog1", "frog", "FROG JUMPS", "Hop like a jungle frog!",
                ["Frog jumps! Squat low, jump high!", "Ribbit! Jump!", "Last ones! Jump!"])], None),
           ("ANIMAL MOVES", [
              P("bunny", "hop", "BUNNY HOPS", "Little hops on every beat!",
                ["Bunny hops! Little hops on the beat!", "Hop, hop, hop!", "Light feet!"]),
              P("monkey", "climb", "CLIMB LIKE A MONKEY", "Reach up, knee up, climb!",
                ["Climb like a monkey! Reach and lift your knee!", "Keep climbing!", "Ooh ooh, aah aah!"]),
              P("flamingo", "balance", "FLAMINGO BALANCE", "Stand on one leg like a flamingo!",
                ["Flamingo balance! Stand on one leg!"]),
              P("gorilla", "punch", "GORILLA POWER", "Strong like a gorilla! Punch!",
                ["Gorilla power! Punch left, right!", "Strong arms!", "Super strong!"]),
              P("kangaroo", "kick", "KANGAROO KICKS", "Kick out to the side!",
                ["Kangaroo kicks! Kick to the side!", "Kick! And kick!", "Great kicks!"]),
              P("croc", "skater", "CROCODILE DODGE", "Hop side to side, away from the crocodile!",
                ["Crocodile! Hop side to side!", "Left! Right!", "Don't get snapped!"]),
              P("coconuts", "reachside", "CATCH THE COCONUTS", "Coconuts are falling!",
                ["Coconuts! Reach and catch them!"], prop="balls"),
              P("leopard", "tuckjump", "LEAPING LEOPARD", "Jump and tuck your knees!",
                ["Leaping leopard! Knees up high!", "Jump!", "Higher!"])],
            ("water1", "Take a sip of water!", "Water break! Take a sip of water.", "Next stop, the river!")),
           ("RIVER ADVENTURE", [
              P("stones", "jump", "JUMP THE STONES", "Jump from stone to stone!",
                ["Stepping stones! Jump!", "Jump! Jump!", "Don't fall in the river!"], prop="puddles"),
              P("riverrun", "run", "RACE THE RIVER", "Run along the river bank!",
                ["Race the river! Run on the spot!", "Pump your arms!", "Faster!"]),
              P("rocks", "skater", "SLIPPERY ROCKS", "Slide side to side!",
                ["Slippery rocks! Slide side to side!", "Left! Right!", "Stay low!"]),
              P("waterfall", "squat", "UNDER THE WATERFALL", "Squat down under the water!",
                ["Waterfall! Squat down, and up!", "Down, and up!", "Splash!"]),
              P("hippo", "highknees", "HIPPO STOMPS", "Big heavy hippo steps!",
                ["Hippo stomps! Knees up!", "Stomp, stomp!", "Big strong hippo!"]),
              P("toucan", "fly", "FLY LIKE A TOUCAN", "Arms out wide! Fly!",
                ["Arms out! Fly like a toucan!", "Lean left, lean right!", "Up, up and away!"]),
              P("crocfreeze", "freeze", "CROCODILE FREEZE", "Dance... FREEZE when the crocodile wakes up!",
                ["Dance! When the crocodile wakes up, freeze!"]),
              P("splash", "starjump", "SPLASH STAR JUMPS", "Make a big splash!",
                ["Splash star jumps! Arms up, legs out!", "Splash! Splash!", "Woo hoo!"])], None),
           ("TREETOP CHALLENGE", [
              P("tree", "climb", "CLIMB THE TREE", "Up to the treetops!",
                ["Climb the tree! Reach up and lift your knee!", "Keep climbing!", "Almost at the top!"]),
              P("bananas", "reachside", "CATCH THE BANANAS", "Bananas falling from the tree!",
                ["Bananas! Reach and catch them!"], prop="balls"),
              P("vineswing", "tuckjump", "VINE SWING JUMPS", "Swing and jump!",
                ["Vine swing! Jump and tuck!", "Jump!", "Higher!"]),
              P("jkick", "kick", "JUNGLE KICKS", "Kick the big leaves!",
                ["Jungle kicks! Kick to the side!", "Hi-yah!", "Strong kicks!"]),
              P("treefrog", "hop", "TREE FROG HOPS", "Little hops along the branch!",
                ["Tree frog hops! Hop, hop, hop!", "Light feet!", "Keep hopping!"]),
              P("bees", "skater", "DODGE THE BEES", "Buzz! Hop side to side!",
                ["Bees! Hop side to side to dodge them!", "Dodge!", "Keep dodging!"]),
              P("statue", "freeze", "JUNGLE STATUE", "Dance... then hold your explorer pose!",
                ["Dance! And when I say statue, hold your pose!"]),
              P("party", "starjump", "JUNGLE PARTY", "All the animals are dancing!",
                ["Jungle party! Star jumps!", "Make some noise!", "Woo hoo!"])],
            ("water2", "Great work, explorers! Sip some water.", "Water break! Great work, explorers!",
             "Time to cool down.")),
           ("COOL DOWN", cool("Slow and calm.",
                              ("BUTTERFLY WINGS", "Small circles with your arms.", "Butterfly wings. Small circles."),
                              ("SLEEPY SLOTH", "Reach down slowly... and up.", "Sleepy sloth. Reach down to your toes."),
                              ("PALM TREE SWAY", "Lean to the side and hold.", "Palm tree sway. Lean over."),
                              ("STILL AS A HERON", "Stand on one leg. Stay still.", "Still as a heron. Stand on one leg."),
                              "Great job today!"), None)],
          ("SAFARI COMPLETE!", "You're a jungle explorer!", "Safari complete! You're a real jungle explorer!"))


def space():
    build(("Space Mission Warm-Up", "SpaceMission_WarmUp_15min", "space"),
          ("SPACE MISSION", "Astronaut training! Follow me!", "Hello, astronauts!",
           "Today we fly to space! Let's warm up!"),
          [("ASTRONAUT TRAINING", [
              P("suit", "reach", "SPACE SUIT STRETCH", "Suit up! Stretch tall!",
                ["Space suit stretch! Reach up high!", "Stretch side to side.", "Reach for the stars!"]),
              P("rocket", "run", "RUN TO THE ROCKET", "The rocket is waiting!",
                ["Run to the rocket! Run on the spot!", "Faster! Faster!", "Almost there!"]),
              P("countdown", "squat", "COUNTDOWN SQUATS", "Ten, nine, eight... squat!",
                ["Countdown squats! Down, and up!", "Down, and up!", "Keep your back straight!"]),
              P("launch", "tuckjump", "ROCKET LAUNCH JUMPS", "Three, two, one... BLAST OFF!",
                ["Blast off! Jump and tuck your knees!", "Jump!", "Higher!"]),
              P("zerog", "highknees", "ZERO-G KNEES", "Float with high knees!",
                ["Zero gravity! High knees!", "Knees up high!", "Faster!"]),
              P("stars", "starjump", "STAR JUMPS", "Real star jumps... in space!",
                ["Star jumps! Arms up, legs out!", "Open, close!", "You're a superstar!"]),
              P("control", "freeze", "MISSION CONTROL FREEZE", "Dance... and FREEZE on the signal!",
                ["Dance! When mission control says freeze, freeze!"]),
              P("moonfrog", "frog", "MOON FROG JUMPS", "Big bouncy jumps!",
                ["Moon frog jumps! Squat low, jump high!", "Jump!", "Last ones! Jump!"])], None),
           ("ON THE MOON", [
              P("moonhop", "hop", "MOON HOPS", "Bounce on the moon!",
                ["Moon hops! Little hops on the beat!", "Hop, hop, hop!", "Light feet!"]),
              P("craters", "jump", "JUMP THE CRATERS", "Craters everywhere!",
                ["Craters! Jump over them!", "Jump! Jump!", "Big jumps!"], prop="puddles"),
              P("buggy", "skater", "MOON BUGGY SLIDES", "Slide side to side!",
                ["Moon buggy! Slide side to side!", "Left! Right!", "Stay low!"]),
              P("lowgrav", "balance", "LOW GRAVITY BALANCE", "Stand on one leg... don't float away!",
                ["Low gravity balance! Stand on one leg!"]),
              P("moonrocks", "reachside", "CATCH THE MOON ROCKS", "Moon rocks floating by!",
                ["Moon rocks! Reach and catch them!"], prop="balls"),
              P("alien", "kick", "ALIEN KICKS", "Kick like a friendly alien!",
                ["Alien kicks! Kick to the side!", "Kick! And kick!", "Great kicks!"]),
              P("ladder", "climb", "CLIMB THE LADDER", "Climb back into the rocket!",
                ["Climb the ladder! Reach up and lift your knee!", "Keep climbing!", "Almost at the top!"]),
              P("flag", "starjump", "PLANT THE FLAG", "We made it to the moon!",
                ["We made it! Celebration star jumps!", "Make some noise!", "Woo hoo!"])],
            ("water1", "Take a sip of water!", "Water break! Take a sip of water.", "Next stop, the asteroid belt!")),
           ("ASTEROID BELT", [
              P("asteroids", "skater", "DODGE THE ASTEROIDS", "Hop side to side!",
                ["Asteroids! Hop side to side to dodge them!", "Dodge!", "Keep dodging!"], prop="lasers"),
              P("smash", "punch", "SMASH THE SPACE ROCKS", "Punch them away! Left, right!",
                ["Smash the space rocks! Left, right!", "Pow! Pow!", "Super strong!"]),
              P("duck", "squat", "DUCK THE SPACE JUNK", "Squat down, quick!",
                ["Space junk! Squat down, and up!", "Down, and up!", "Watch out!"]),
              P("comet", "run", "ESCAPE THE COMET", "A comet is coming! Run!",
                ["Comet! Run as fast as you can!", "Super speed!", "Faster!"]),
              P("ship", "fly", "FLY THE SPACESHIP", "Arms out! Steer the ship!",
                ["Fly the spaceship! Arms out wide!", "Lean left, lean right!", "Full speed ahead!"]),
              P("redalert", "freeze", "RED ALERT FREEZE", "Dance... FREEZE on red alert!",
                ["Dance! On red alert, freeze!"]),
              P("hyper", "tuckjump", "HYPERSPACE JUMPS", "Jump into hyperspace!",
                ["Hyperspace jumps! Knees up high!", "Jump!", "Higher!"]),
              P("meteor", "jump", "METEOR JUMPS", "Jump over the meteors!",
                ["Meteors! Jump!", "Jump! Jump!", "Big jumps!"], prop="hurdles")], None),
           ("ALIEN PLANET", [
              P("aliendance", "starjump", "ALIEN DANCE", "The aliens want to dance!",
                ["Alien dance! Star jumps!", "Arms up! Legs out!", "Keep going!"]),
              P("bouncy", "hop", "BOUNCY PLANET HOPS", "This planet is super bouncy!",
                ["Bouncy planet! Hop, hop, hop!", "Light feet!", "Keep hopping!"]),
              P("robot", "kick", "ROBOT KICKS", "Beep boop! Kick!",
                ["Robot kicks! Kick to the side!", "Beep! Boop!", "Strong kicks!"]),
              P("crystal", "climb", "CLIMB THE CRYSTAL MOUNTAIN", "Reach up, knee up, climb!",
                ["Crystal mountain! Climb!", "Keep climbing!", "Almost at the top!"]),
              P("catchstars", "reachside", "CATCH THE STARS", "Shooting stars!",
                ["Shooting stars! Reach and catch them!"], prop="balls"),
              P("march", "highknees", "ROBOT MARCH", "March like a robot!",
                ["Robot march! Knees up!", "Left, right!", "Faster!"]),
              P("maze", "skater", "LASER MAZE", "Hop through the laser maze!",
                ["Laser maze! Hop side to side!", "Dodge!", "Keep going!"], prop="lasers"),
              P("statue", "freeze", "ROBOT STATUE", "Dance... then freeze like a robot statue!",
                ["Dance! And when I say statue, freeze like a robot!"])],
            ("water2", "Great work, astronauts! Sip some water.", "Water break! Great work, astronauts!",
             "Time to fly home.")),
           ("BACK TO EARTH", cool("Float in space. Slow and calm.",
                                  ("PLANET ORBITS", "Small circles with your arms.", "Planet orbits. Small circles."),
                                  ("MOON DUST", "Reach down slowly... and up.", "Reach down and touch the moon dust."),
                                  ("SATELLITE STRETCH", "Lean to the side and hold.", "Satellite stretch. Lean over."),
                                  ("STILL AS A STAR", "Stand on one leg. Stay still.", "Still as a star. Stand on one leg."),
                                  "Welcome home!"), None)],
          ("MISSION COMPLETE!", "You're a space hero!", "Mission complete! You're a real astronaut!"))


def ocean():
    build(("Under the Sea Warm-Up", "UnderTheSea_WarmUp_15min", "ocean"),
          ("UNDER THE SEA", "Ocean adventure! Follow me!", "Hello, ocean explorers!",
           "Today we dive under the sea! Let's warm up!"),
          [("DIVE IN", [
              P("starfish", "reach", "STRETCH LIKE A STARFISH", "Arms and legs out wide!",
                ["Starfish stretch! Reach up high!", "Stretch side to side.", "Reach for the sun!"]),
              P("beach", "run", "RUN TO THE BEACH", "The waves are calling!",
                ["Run to the beach! Run on the spot!", "Faster! Faster!", "Almost there!"]),
              P("waves", "jump", "JUMP THE WAVES", "Here come the waves!",
                ["Waves! Jump over them!", "Jump! Jump!", "Big jumps!"], prop="puddles"),
              P("dive", "squat", "DIVE DOWN", "Squat down and dive!",
                ["Dive down! Squat, and up!", "Down, and up!", "Keep your back straight!"]),
              P("splashy", "highknees", "SPLASHY KNEES", "Splash through the water!",
                ["Splashy knees! Knees up high!", "Splash, splash!", "Faster!"]),
              P("stars", "starjump", "STARFISH JUMPS", "Jump like a starfish!",
                ["Starfish jumps! Arms up, legs out!", "Open, close!", "Super starfish!"]),
              P("shark", "freeze", "SHARK ATTACK FREEZE", "Dance... FREEZE when the shark swims by!",
                ["Dance! When the shark comes, freeze!"]),
              P("frogfish", "frog", "FROG FISH JUMPS", "Squat low, jump high!",
                ["Frog fish jumps! Squat low, jump high!", "Jump!", "Last ones! Jump!"])], None),
           ("CORAL REEF", [
              P("crab", "skater", "CRAB SIDE SLIDES", "Scuttle side to side like a crab!",
                ["Crab slides! Side to side!", "Left! Right!", "Pinch, pinch!"]),
              P("seahorse", "hop", "SEAHORSE HOPS", "Little hops on every beat!",
                ["Seahorse hops! Little hops on the beat!", "Hop, hop, hop!", "Light feet!"]),
              P("bubbles", "reachside", "CATCH THE BUBBLES", "Bubbles everywhere!",
                ["Bubbles! Reach and catch them!"], prop="balls"),
              P("rock", "balance", "BALANCE ON THE ROCK", "Stand on one leg on the rock!",
                ["Balance on the rock! Stand on one leg!"]),
              P("octopus", "punch", "OCTOPUS PUNCHES", "Eight arms! Punch, punch!",
                ["Octopus punches! Left, right!", "Punch! Punch!", "So many arms!"]),
              P("dolphin", "kick", "DOLPHIN KICKS", "Kick like a dolphin's tail!",
                ["Dolphin kicks! Kick to the side!", "Kick! And kick!", "Great kicks!"]),
              P("coral", "climb", "CLIMB THE CORAL", "Reach up, knee up, climb!",
                ["Climb the coral! Reach and lift your knee!", "Keep climbing!", "Almost at the top!"]),
              P("fishparty", "starjump", "FISH PARTY", "All the fish are dancing!",
                ["Fish party! Star jumps!", "Make some bubbles!", "Woo hoo!"])],
            ("water1", "Take a sip of water!", "Water break! Take a sip of water.", "Next, the deep sea!")),
           ("DEEP SEA", [
              P("seaweed", "squat", "DUCK THE SEAWEED", "Squat under the seaweed!",
                ["Seaweed! Squat down, and up!", "Down, and up!", "Stay low!"], prop="branches"),
              P("manta", "fly", "SWIM LIKE A MANTA RAY", "Arms out wide! Glide!",
                ["Manta ray! Arms out wide!", "Lean left, lean right!", "Glide!"]),
              P("jelly", "skater", "DODGE THE JELLYFISH", "Hop side to side!",
                ["Jellyfish! Hop side to side to dodge them!", "Dodge!", "Keep dodging!"]),
              P("race", "run", "RACE THE DOLPHINS", "Can you beat the dolphins?",
                ["Race the dolphins! Run on the spot!", "Super speed!", "Faster!"]),
              P("leap", "tuckjump", "JUMPING DOLPHINS", "Leap out of the water!",
                ["Jumping dolphins! Knees up high!", "Jump!", "Higher!"]),
              P("seabed", "jump", "BOUNCE ON THE SEABED", "Bounce, bounce!",
                ["Bounce on the seabed! Jump!", "Jump! Jump!", "Big jumps!"]),
              P("statue", "freeze", "SUNKEN STATUE", "Dance... then freeze like a statue!",
                ["Dance! And when I say statue, freeze!"]),
              P("turtle", "highknees", "TURTLE PADDLE", "Paddle like a sea turtle!",
                ["Turtle paddle! Knees up!", "Paddle, paddle!", "Faster!"])], None),
           ("TREASURE HUNT", [
              P("map", "run", "FOLLOW THE MAP", "X marks the spot!",
                ["Follow the map! Run on the spot!", "This way!", "Faster!"]),
              P("wreck", "climb", "CLIMB THE SHIPWRECK", "Climb up the old ship!",
                ["Shipwreck! Climb!", "Keep climbing!", "Almost at the top!"]),
              P("coins", "reachside", "CATCH THE GOLD COINS", "Gold coins everywhere!",
                ["Gold coins! Reach and catch them!"], prop="balls"),
              P("chests", "jump", "JUMP THE TREASURE CHESTS", "Jump over every chest!",
                ["Treasure chests! Jump over them!", "Jump! Jump!", "Higher!"], prop="hurdles"),
              P("pirate", "kick", "PIRATE KICKS", "Ahoy! Kick to the side!",
                ["Pirate kicks! Kick to the side!", "Ahoy!", "Strong kicks!"]),
              P("anchor", "squat", "PULL UP THE ANCHOR", "Squat down, pull up!",
                ["Pull up the anchor! Squat down, and up!", "Pull!", "Heave ho!"]),
              P("pfreeze", "freeze", "PIRATE FREEZE", "Dance... FREEZE when the captain looks!",
                ["Dance! When the captain looks, freeze!"]),
              P("treasure", "starjump", "TREASURE PARTY", "We found the treasure!",
                ["We found the treasure! Star jumps!", "Make some noise!", "Woo hoo!"])],
            ("water2", "Great work, divers! Sip some water.", "Water break! Great work, divers!",
             "Time to cool down.")),
           ("COOL DOWN", cool("Bubble breaths. Slow and calm.",
                              ("JELLYFISH ARMS", "Small circles with your arms.", "Jellyfish arms. Small circles."),
                              ("TOUCH THE SAND", "Reach down slowly... and up.", "Reach down and touch the sand."),
                              ("SEAWEED SWAY", "Lean to the side and hold.", "Seaweed sway. Lean over."),
                              ("STILL AS A STARFISH", "Stand on one leg. Stay still.",
                               "Still as a starfish. Stand on one leg."),
                              "Great job today!"), None)],
          ("OCEAN HERO!", "You're an ocean explorer!", "You did it! You're a real ocean hero!"))


if __name__ == "__main__":
    jungle(); space(); ocean()
