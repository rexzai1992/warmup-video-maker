// Under the Sea Warm-Up - 15-minute warm-up. 120 BPM (1 beat = 0.5 s). Written by tools/new_timelines.py.
// Scenes: Google Flow clips in footage/flow/ocean/<id>.mp4 (prompts: flow_prompts/ocean.md)
window.TIMELINE = {
 "title": "Under the Sea Warm-Up",
 "output": "UnderTheSea_WarmUp_15min",
 "character": "line",
 "bpm": 120,
 "fps": 30,
 "segments": [
  {
   "id": "intro",
   "scene": "footage",
   "move": "wave",
   "dur": 10,
   "ch": 1,
   "cue": "UNDER THE SEA",
   "story": "Ocean adventure! Follow me!",
   "say": [
    [
     0.5,
     "Hello, ocean explorers!"
    ],
    [
     3,
     "Today we dive under the sea! Let's warm up!"
    ],
    [
     7.5,
     "Follow me!"
    ]
   ]
  },
  {
   "id": "c1",
   "scene": "card",
   "move": "wave",
   "dur": 6,
   "ch": 1,
   "cue": "CHAPTER 1",
   "story": "DIVE IN",
   "say": [
    [
     0.5,
     "Chapter one! Dive In!"
    ]
   ]
  },
  {
   "id": "starfish",
   "scene": "footage",
   "move": "reach",
   "dur": 20,
   "ch": 1,
   "cue": "STRETCH LIKE A STARFISH",
   "story": "Arms and legs out wide!",
   "say": [
    [
     0,
     "Starfish stretch! Reach up high!"
    ],
    [
     9,
     "Stretch side to side."
    ],
    [
     15,
     "Reach for the sun!"
    ]
   ]
  },
  {
   "id": "beach",
   "scene": "footage",
   "move": "run",
   "dur": 20,
   "ch": 1,
   "cue": "RUN TO THE BEACH",
   "story": "The waves are calling!",
   "say": [
    [
     0,
     "Run to the beach! Run on the spot!"
    ],
    [
     9,
     "Faster! Faster!"
    ],
    [
     15,
     "Almost there!"
    ]
   ],
   "game": "coin",
   "skin": "🐚"
  },
  {
   "id": "waves",
   "scene": "footage",
   "move": "jump",
   "dur": 20,
   "ch": 1,
   "prop": "puddles",
   "cue": "JUMP THE WAVES",
   "story": "Here come the waves!",
   "say": [
    [
     0,
     "Waves! Jump over them!"
    ],
    [
     9,
     "Jump! Jump!"
    ],
    [
     15,
     "Big jumps!"
    ]
   ],
   "game": "pop",
   "skin": "🫧"
  },
  {
   "id": "dive",
   "scene": "footage",
   "move": "squat",
   "dur": 20,
   "ch": 1,
   "cue": "DIVE DOWN",
   "story": "Squat down and dive!",
   "say": [
    [
     0,
     "Dive down! Squat, and up!"
    ],
    [
     9,
     "Down, and up!"
    ],
    [
     15,
     "Keep your back straight!"
    ]
   ],
   "game": "press"
  },
  {
   "id": "splashy",
   "scene": "footage",
   "move": "highknees",
   "dur": 20,
   "ch": 1,
   "cue": "SPLASHY KNEES",
   "story": "Splash through the water!",
   "say": [
    [
     0,
     "Splashy knees! Knees up high!"
    ],
    [
     9,
     "Splash, splash!"
    ],
    [
     15,
     "Faster!"
    ]
   ],
   "game": "stomp",
   "skin": "🫧"
  },
  {
   "id": "stars",
   "scene": "footage",
   "move": "starjump",
   "dur": 20,
   "ch": 1,
   "cue": "STARFISH JUMPS",
   "story": "Jump like a starfish!",
   "say": [
    [
     0,
     "Starfish jumps! Arms up, legs out!"
    ],
    [
     9,
     "Open, close!"
    ],
    [
     15,
     "Super starfish!"
    ]
   ],
   "game": "slap",
   "skin": "✋"
  },
  {
   "id": "shark",
   "scene": "footage",
   "move": "freeze",
   "dur": 24,
   "ch": 1,
   "cue": "SHARK ATTACK FREEZE",
   "story": "Dance... FREEZE when the shark swims by!",
   "say": [
    [
     0,
     "Dance! When the shark comes, freeze!"
    ]
   ]
  },
  {
   "id": "frogfish",
   "scene": "footage",
   "move": "frog",
   "dur": 20,
   "ch": 1,
   "cue": "FROG FISH JUMPS",
   "story": "Squat low, jump high!",
   "say": [
    [
     0,
     "Frog fish jumps! Squat low, jump high!"
    ],
    [
     10,
     "Jump!"
    ],
    [
     16,
     "Last ones! Jump!"
    ]
   ]
  },
  {
   "id": "c2",
   "scene": "card",
   "move": "wave",
   "dur": 6,
   "ch": 2,
   "cue": "CHAPTER 2",
   "story": "CORAL REEF",
   "say": [
    [
     0.5,
     "Chapter two! Coral Reef!"
    ]
   ]
  },
  {
   "id": "crab",
   "scene": "footage",
   "move": "skater",
   "dur": 20,
   "ch": 2,
   "cue": "CRAB SIDE SLIDES",
   "story": "Scuttle side to side like a crab!",
   "say": [
    [
     0,
     "Crab slides! Side to side!"
    ],
    [
     9,
     "Left! Right!"
    ],
    [
     15,
     "Pinch, pinch!"
    ]
   ],
   "game": "coin",
   "skin": "🐚"
  },
  {
   "id": "seahorse",
   "scene": "footage",
   "move": "hop",
   "dur": 20,
   "ch": 2,
   "cue": "SEAHORSE HOPS",
   "story": "Little hops on every beat!",
   "say": [
    [
     0,
     "Seahorse hops! Little hops on the beat!"
    ],
    [
     9,
     "Hop, hop, hop!"
    ],
    [
     15,
     "Light feet!"
    ]
   ],
   "game": "stomp",
   "skin": "🫧"
  },
  {
   "id": "bubbles",
   "scene": "footage",
   "move": "reachside",
   "dur": 20,
   "ch": 2,
   "prop": "balls",
   "cue": "CATCH THE BUBBLES",
   "story": "Bubbles everywhere!",
   "say": [
    [
     0,
     "Bubbles! Reach and catch them!"
    ]
   ]
  },
  {
   "id": "rock",
   "scene": "footage",
   "move": "balance",
   "dur": 20,
   "ch": 2,
   "cue": "BALANCE ON THE ROCK",
   "story": "Stand on one leg on the rock!",
   "say": [
    [
     0,
     "Balance on the rock! Stand on one leg!"
    ],
    [
     8,
     "Switch legs!"
    ],
    [
     16,
     "Switch!"
    ]
   ]
  },
  {
   "id": "octopus",
   "scene": "footage",
   "move": "punch",
   "dur": 20,
   "ch": 2,
   "cue": "OCTOPUS PUNCHES",
   "story": "Eight arms! Punch, punch!",
   "say": [
    [
     0,
     "Octopus punches! Left, right!"
    ],
    [
     9,
     "Punch! Punch!"
    ],
    [
     15,
     "So many arms!"
    ]
   ],
   "game": "whack",
   "skin": "🐙"
  },
  {
   "id": "dolphin",
   "scene": "footage",
   "move": "kick",
   "dur": 20,
   "ch": 2,
   "cue": "DOLPHIN KICKS",
   "story": "Kick like a dolphin's tail!",
   "say": [
    [
     0,
     "Dolphin kicks! Kick to the side!"
    ],
    [
     9,
     "Kick! And kick!"
    ],
    [
     15,
     "Great kicks!"
    ]
   ],
   "game": "kick",
   "skin": "🏐"
  },
  {
   "id": "coral",
   "scene": "footage",
   "move": "climb",
   "dur": 20,
   "ch": 2,
   "cue": "CLIMB THE CORAL",
   "story": "Reach up, knee up, climb!",
   "say": [
    [
     0,
     "Climb the coral! Reach and lift your knee!"
    ],
    [
     9,
     "Keep climbing!"
    ],
    [
     15,
     "Almost at the top!"
    ]
   ],
   "game": "grab",
   "skin": "🐚"
  },
  {
   "id": "fishparty",
   "scene": "footage",
   "move": "starjump",
   "dur": 20,
   "ch": 2,
   "cue": "FISH PARTY",
   "story": "All the fish are dancing!",
   "say": [
    [
     0,
     "Fish party! Star jumps!"
    ],
    [
     9,
     "Make some bubbles!"
    ],
    [
     15,
     "Woo hoo!"
    ]
   ],
   "game": "spin"
  },
  {
   "id": "water1",
   "scene": "footage",
   "move": "rest",
   "dur": 16,
   "ch": 2,
   "calm": true,
   "cue": "WATER BREAK",
   "story": "Take a sip of water!",
   "say": [
    [
     0,
     "Water break! Take a sip of water."
    ],
    [
     10,
     "Next, the deep sea!"
    ]
   ]
  },
  {
   "id": "c3",
   "scene": "card",
   "move": "wave",
   "dur": 6,
   "ch": 3,
   "cue": "CHAPTER 3",
   "story": "DEEP SEA",
   "say": [
    [
     0.5,
     "Chapter three! Deep Sea!"
    ]
   ]
  },
  {
   "id": "seaweed",
   "scene": "footage",
   "move": "squat",
   "dur": 20,
   "ch": 3,
   "prop": "branches",
   "cue": "DUCK THE SEAWEED",
   "story": "Squat under the seaweed!",
   "say": [
    [
     0,
     "Seaweed! Squat down, and up!"
    ],
    [
     9,
     "Down, and up!"
    ],
    [
     15,
     "Stay low!"
    ]
   ],
   "game": "switch"
  },
  {
   "id": "manta",
   "scene": "footage",
   "move": "fly",
   "dur": 20,
   "ch": 3,
   "cue": "SWIM LIKE A MANTA RAY",
   "story": "Arms out wide! Glide!",
   "say": [
    [
     0,
     "Manta ray! Arms out wide!"
    ],
    [
     9,
     "Lean left, lean right!"
    ],
    [
     15,
     "Glide!"
    ]
   ]
  },
  {
   "id": "jelly",
   "scene": "footage",
   "move": "skater",
   "dur": 20,
   "ch": 3,
   "cue": "DODGE THE JELLYFISH",
   "story": "Hop side to side!",
   "say": [
    [
     0,
     "Jellyfish! Hop side to side to dodge them!"
    ],
    [
     9,
     "Dodge!"
    ],
    [
     15,
     "Keep dodging!"
    ]
   ],
   "game": "coin",
   "skin": "💎"
  },
  {
   "id": "race",
   "scene": "footage",
   "move": "run",
   "dur": 20,
   "ch": 3,
   "cue": "RACE THE DOLPHINS",
   "story": "Can you beat the dolphins?",
   "say": [
    [
     0,
     "Race the dolphins! Run on the spot!"
    ],
    [
     9,
     "Super speed!"
    ],
    [
     15,
     "Faster!"
    ]
   ],
   "game": "coin",
   "skin": "🪙"
  },
  {
   "id": "leap",
   "scene": "footage",
   "move": "tuckjump",
   "dur": 20,
   "ch": 3,
   "cue": "JUMPING DOLPHINS",
   "story": "Leap out of the water!",
   "say": [
    [
     0,
     "Jumping dolphins! Knees up high!"
    ],
    [
     9,
     "Jump!"
    ],
    [
     15,
     "Higher!"
    ]
   ],
   "game": "pop",
   "skin": "🫧"
  },
  {
   "id": "seabed",
   "scene": "footage",
   "move": "jump",
   "dur": 20,
   "ch": 3,
   "cue": "BOUNCE ON THE SEABED",
   "story": "Bounce, bounce!",
   "say": [
    [
     0,
     "Bounce on the seabed! Jump!"
    ],
    [
     9,
     "Jump! Jump!"
    ],
    [
     15,
     "Big jumps!"
    ]
   ]
  },
  {
   "id": "statue",
   "scene": "footage",
   "move": "freeze",
   "dur": 24,
   "ch": 3,
   "cue": "SUNKEN STATUE",
   "story": "Dance... then freeze like a statue!",
   "say": [
    [
     0,
     "Dance! And when I say statue, freeze!"
    ]
   ]
  },
  {
   "id": "turtle",
   "scene": "footage",
   "move": "highknees",
   "dur": 20,
   "ch": 3,
   "cue": "TURTLE PADDLE",
   "story": "Paddle like a sea turtle!",
   "say": [
    [
     0,
     "Turtle paddle! Knees up!"
    ],
    [
     9,
     "Paddle, paddle!"
    ],
    [
     15,
     "Faster!"
    ]
   ],
   "game": "stomp",
   "skin": "🫧"
  },
  {
   "id": "c4",
   "scene": "card",
   "move": "wave",
   "dur": 6,
   "ch": 4,
   "cue": "CHAPTER 4",
   "story": "TREASURE HUNT",
   "say": [
    [
     0.5,
     "Chapter four! Treasure Hunt!"
    ]
   ]
  },
  {
   "id": "map",
   "scene": "footage",
   "move": "run",
   "dur": 20,
   "ch": 4,
   "cue": "FOLLOW THE MAP",
   "story": "X marks the spot!",
   "say": [
    [
     0,
     "Follow the map! Run on the spot!"
    ],
    [
     9,
     "This way!"
    ],
    [
     15,
     "Faster!"
    ]
   ],
   "game": "coin",
   "skin": "🪙"
  },
  {
   "id": "wreck",
   "scene": "footage",
   "move": "climb",
   "dur": 20,
   "ch": 4,
   "cue": "CLIMB THE SHIPWRECK",
   "story": "Climb up the old ship!",
   "say": [
    [
     0,
     "Shipwreck! Climb!"
    ],
    [
     9,
     "Keep climbing!"
    ],
    [
     15,
     "Almost at the top!"
    ]
   ],
   "game": "bell",
   "skin": "🔔"
  },
  {
   "id": "coins",
   "scene": "footage",
   "move": "reachside",
   "dur": 20,
   "ch": 4,
   "prop": "balls",
   "cue": "CATCH THE GOLD COINS",
   "story": "Gold coins everywhere!",
   "say": [
    [
     0,
     "Gold coins! Reach and catch them!"
    ]
   ]
  },
  {
   "id": "chests",
   "scene": "footage",
   "move": "jump",
   "dur": 20,
   "ch": 4,
   "prop": "hurdles",
   "cue": "JUMP THE TREASURE CHESTS",
   "story": "Jump over every chest!",
   "say": [
    [
     0,
     "Treasure chests! Jump over them!"
    ],
    [
     9,
     "Jump! Jump!"
    ],
    [
     15,
     "Higher!"
    ]
   ],
   "game": "pop",
   "skin": "🎈"
  },
  {
   "id": "pirate",
   "scene": "footage",
   "move": "kick",
   "dur": 20,
   "ch": 4,
   "cue": "PIRATE KICKS",
   "story": "Ahoy! Kick to the side!",
   "say": [
    [
     0,
     "Pirate kicks! Kick to the side!"
    ],
    [
     9,
     "Ahoy!"
    ],
    [
     15,
     "Strong kicks!"
    ]
   ],
   "game": "smash",
   "skin": "📦"
  },
  {
   "id": "anchor",
   "scene": "footage",
   "move": "squat",
   "dur": 20,
   "ch": 4,
   "cue": "PULL UP THE ANCHOR",
   "story": "Squat down, pull up!",
   "say": [
    [
     0,
     "Pull up the anchor! Squat down, and up!"
    ],
    [
     9,
     "Pull!"
    ],
    [
     15,
     "Heave ho!"
    ]
   ],
   "game": "press"
  },
  {
   "id": "pfreeze",
   "scene": "footage",
   "move": "freeze",
   "dur": 24,
   "ch": 4,
   "cue": "PIRATE FREEZE",
   "story": "Dance... FREEZE when the captain looks!",
   "say": [
    [
     0,
     "Dance! When the captain looks, freeze!"
    ]
   ]
  },
  {
   "id": "treasure",
   "scene": "footage",
   "move": "starjump",
   "dur": 20,
   "ch": 4,
   "cue": "TREASURE PARTY",
   "story": "We found the treasure!",
   "say": [
    [
     0,
     "We found the treasure! Star jumps!"
    ],
    [
     9,
     "Make some noise!"
    ],
    [
     15,
     "Woo hoo!"
    ]
   ],
   "game": "slap",
   "skin": "✋"
  },
  {
   "id": "water2",
   "scene": "footage",
   "move": "rest",
   "dur": 16,
   "ch": 4,
   "calm": true,
   "cue": "WATER BREAK",
   "story": "Great work, divers! Sip some water.",
   "say": [
    [
     0,
     "Water break! Great work, divers!"
    ],
    [
     10,
     "Time to cool down."
    ]
   ]
  },
  {
   "id": "c5",
   "scene": "card",
   "move": "wave",
   "dur": 6,
   "ch": 5,
   "cue": "CHAPTER 5",
   "story": "COOL DOWN",
   "say": [
    [
     0.5,
     "Chapter five. Cool Down."
    ]
   ],
   "calm": true
  },
  {
   "id": "breathe1",
   "scene": "footage",
   "move": "breathe",
   "dur": 16,
   "ch": 5,
   "calm": true,
   "cue": "BREATHE",
   "story": "Bubble breaths. Slow and calm.",
   "say": [
    [
     0,
     "Breathe in..."
    ],
    [
     4,
     "and out."
    ],
    [
     8,
     "Breathe in..."
    ],
    [
     12,
     "and out."
    ]
   ]
  },
  {
   "id": "circles",
   "scene": "footage",
   "move": "armcircles",
   "dur": 20,
   "ch": 5,
   "calm": true,
   "cue": "JELLYFISH ARMS",
   "story": "Small circles with your arms.",
   "say": [
    [
     0,
     "Jellyfish arms. Small circles."
    ],
    [
     10,
     "Now the other way."
    ]
   ]
  },
  {
   "id": "toes",
   "scene": "footage",
   "move": "toetouch",
   "dur": 20,
   "ch": 5,
   "calm": true,
   "cue": "TOUCH THE SAND",
   "story": "Reach down slowly... and up.",
   "say": [
    [
     0,
     "Reach down and touch the sand."
    ],
    [
     10,
     "Slowly. And up."
    ]
   ]
  },
  {
   "id": "side",
   "scene": "footage",
   "move": "sidestretch",
   "dur": 20,
   "ch": 5,
   "calm": true,
   "cue": "SEAWEED SWAY",
   "story": "Lean to the side and hold.",
   "say": [
    [
     0,
     "Seaweed sway. Lean over."
    ],
    [
     8,
     "And the other side."
    ]
   ]
  },
  {
   "id": "still",
   "scene": "footage",
   "move": "balance",
   "dur": 20,
   "ch": 5,
   "calm": true,
   "cue": "STILL AS A STARFISH",
   "story": "Stand on one leg. Stay still.",
   "say": [
    [
     0,
     "Still as a starfish. Stand on one leg."
    ],
    [
     8,
     "Switch legs!"
    ],
    [
     16,
     "Switch!"
    ]
   ]
  },
  {
   "id": "breathe2",
   "scene": "footage",
   "move": "breathe",
   "dur": 16,
   "ch": 5,
   "calm": true,
   "cue": "BREATHE",
   "story": "Great job today!",
   "say": [
    [
     0,
     "One more big breath in..."
    ],
    [
     4,
     "and out."
    ],
    [
     8,
     "Breathe in..."
    ],
    [
     12,
     "and out."
    ]
   ]
  },
  {
   "id": "outro",
   "scene": "footage",
   "move": "wave",
   "dur": 12,
   "ch": 5,
   "cue": "OCEAN HERO!",
   "story": "You're an ocean explorer!",
   "say": [
    [
     0.5,
     "You did it! You're a real ocean hero!"
    ],
    [
     5,
     "High five! See you next time!"
    ]
   ]
  }
 ]
};
if (typeof module !== "undefined") module.exports = window.TIMELINE;
