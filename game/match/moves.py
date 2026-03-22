"""Move sets organized by wrestling style, plus finishers, signatures, and standard moves."""


# Finisher suggestions by style - each is (name, move_type, damage, spectacle, injury_risk)
FINISHERS_BY_STYLE = {
    "technical": [
        ("Crossface Crippler", "submission", 85, 70, 0.15),
        ("Ankle Lock", "submission", 80, 65, 0.12),
        ("Dragon Sleeper", "submission", 75, 60, 0.10),
        ("Figure Eight", "submission", 80, 70, 0.14),
        ("Cattle Mutilation", "submission", 85, 75, 0.13),
        ("Sharpshooter", "submission", 78, 72, 0.11),
        ("STF", "submission", 72, 55, 0.08),
        ("Rings of Saturn", "submission", 82, 68, 0.12),
    ],
    "high_flyer": [
        ("Shooting Star Press", "aerial", 90, 95, 0.30),
        ("630 Senton", "aerial", 95, 100, 0.40),
        ("Phoenix Splash", "aerial", 92, 95, 0.35),
        ("Spiral Tap", "aerial", 93, 98, 0.38),
        ("Red Arrow", "aerial", 88, 92, 0.28),
        ("Corkscrew Moonsault", "aerial", 87, 90, 0.25),
        ("Swanton Bomb", "aerial", 85, 85, 0.22),
        ("Frog Splash", "aerial", 82, 80, 0.18),
    ],
    "powerhouse": [
        ("Jackknife Powerbomb", "power", 90, 85, 0.18),
        ("Muscle Buster", "power", 92, 80, 0.25),
        ("F-5", "power", 88, 88, 0.15),
        ("Burning Hammer", "power", 98, 90, 0.35),
        ("One-Winged Angel", "power", 95, 95, 0.22),
        ("Last Ride", "power", 86, 82, 0.16),
        ("Tombstone Piledriver", "power", 93, 90, 0.28),
        ("Steiner Screwdriver", "power", 97, 88, 0.40),
    ],
    "brawler": [
        ("Stunner", "strike", 85, 90, 0.08),
        ("Piledriver", "power", 90, 75, 0.30),
        ("Lariat From Hell", "strike", 88, 85, 0.12),
        ("GTS (Go To Sleep)", "strike", 87, 88, 0.14),
        ("Curb Stomp", "strike", 92, 82, 0.22),
        ("Punt Kick", "strike", 93, 78, 0.30),
        ("Package Piledriver", "power", 91, 80, 0.28),
        ("Brainbuster", "power", 86, 72, 0.20),
    ],
    "showman": [
        ("Rock Bottom", "power", 82, 92, 0.10),
        ("People's Elbow", "strike", 60, 100, 0.05),
        ("Sweet Chin Music", "strike", 88, 95, 0.08),
        ("Rainmaker", "strike", 85, 90, 0.10),
        ("Coup de Grace", "aerial", 86, 88, 0.18),
        ("The Worm", "strike", 40, 100, 0.02),
        ("Five Star Frog Splash", "aerial", 84, 88, 0.20),
        ("Attitude Adjustment", "power", 78, 85, 0.12),
    ],
    "strong_style": [
        ("Bomaye / Kinshasa", "strike", 90, 88, 0.15),
        ("Kamigoye", "strike", 92, 85, 0.18),
        ("Emerald Flowsion", "power", 88, 80, 0.20),
        ("Tiger Driver '91", "power", 95, 82, 0.32),
        ("Ganso Bomb", "power", 97, 75, 0.45),
        ("Kawada Kicks", "strike", 85, 78, 0.16),
        ("Backdrop Driver", "power", 90, 78, 0.25),
        ("Lariat", "strike", 86, 82, 0.12),
    ],
    "hybrid": [
        ("Destino", "power", 85, 90, 0.15),
        ("Canadian Destroyer", "power", 88, 95, 0.22),
        ("Codebreaker", "strike", 80, 85, 0.10),
        ("RKO", "strike", 82, 98, 0.08),
        ("Eclipse", "aerial", 86, 88, 0.18),
        ("Styles Clash", "power", 87, 85, 0.25),
        ("V-Trigger", "strike", 84, 82, 0.12),
        ("Paradigm Shift", "power", 83, 80, 0.14),
    ],
}


# Signature moves by style - mid-tier moves that build toward the finish
SIGNATURES_BY_STYLE = {
    "technical": [
        ("German Suplex", "power", 60, 55, 0.10),
        ("Backbreaker", "power", 55, 50, 0.08),
        ("Bridging Northern Lights Suplex", "power", 62, 60, 0.09),
        ("Snap Suplex", "power", 50, 45, 0.06),
        ("Belly-to-Belly Suplex", "power", 55, 50, 0.07),
        ("Abdominal Stretch", "submission", 40, 35, 0.03),
        ("Armbar Takedown", "submission", 45, 40, 0.05),
        ("Dragon Screw", "submission", 50, 50, 0.08),
    ],
    "high_flyer": [
        ("Springboard Clothesline", "aerial", 55, 70, 0.15),
        ("Hurricanrana", "aerial", 50, 72, 0.12),
        ("Suicide Dive", "aerial", 60, 78, 0.20),
        ("Moonsault", "aerial", 65, 80, 0.18),
        ("Tope Con Hilo", "aerial", 58, 75, 0.17),
        ("Springboard DDT", "aerial", 62, 74, 0.16),
        ("450 Splash (to standing opponent)", "aerial", 68, 82, 0.22),
        ("Frankensteiner", "aerial", 52, 68, 0.14),
    ],
    "powerhouse": [
        ("Military Press Slam", "power", 55, 65, 0.08),
        ("Running Powerslam", "power", 60, 60, 0.10),
        ("Spinebuster", "power", 62, 70, 0.12),
        ("Gorilla Press", "power", 50, 62, 0.07),
        ("Fallaway Slam", "power", 52, 55, 0.06),
        ("Chokeslam", "power", 65, 72, 0.14),
        ("Backbreaker Rack", "power", 58, 58, 0.08),
        ("Sidewalk Slam", "power", 48, 50, 0.05),
    ],
    "brawler": [
        ("DDT", "power", 55, 55, 0.10),
        ("Neckbreaker", "power", 50, 48, 0.08),
        ("Running Knee", "strike", 58, 60, 0.08),
        ("Discus Clothesline", "strike", 60, 62, 0.06),
        ("Chair Shot (if legal)", "weapon", 65, 55, 0.15),
        ("Headbutt", "strike", 45, 40, 0.12),
        ("Bite (if heel)", "dirty", 30, 45, 0.02),
        ("Eye Rake into DDT", "dirty", 52, 50, 0.08),
    ],
    "showman": [
        ("Diving Elbow Drop", "aerial", 55, 70, 0.10),
        ("Running Bulldog", "power", 48, 55, 0.06),
        ("Float-over DDT", "power", 52, 62, 0.08),
        ("Slingblade", "power", 50, 58, 0.07),
        ("Springboard Forearm", "aerial", 58, 68, 0.12),
        ("Disaster Kick", "strike", 55, 65, 0.10),
        ("Neckbreaker (with flair)", "power", 50, 60, 0.07),
        ("Blockbuster", "aerial", 56, 64, 0.11),
    ],
    "strong_style": [
        ("Stiff Forearm Exchange", "strike", 45, 55, 0.08),
        ("Roundhouse Kick", "strike", 60, 62, 0.10),
        ("Falcon Arrow", "power", 58, 58, 0.12),
        ("Brainbuster", "power", 65, 60, 0.18),
        ("Penalty Kick", "strike", 55, 55, 0.08),
        ("Half-and-Half Suplex", "power", 62, 58, 0.14),
        ("Koppu Kick", "strike", 50, 50, 0.06),
        ("Jumping Knee Strike", "strike", 58, 60, 0.09),
    ],
    "hybrid": [
        ("Enzuigiri", "strike", 48, 55, 0.06),
        ("Superkick", "strike", 55, 65, 0.05),
        ("Blue Thunder Bomb", "power", 60, 62, 0.10),
        ("Michinoku Driver", "power", 58, 58, 0.12),
        ("Springboard Cutter", "aerial", 62, 72, 0.15),
        ("Backstabber", "power", 55, 60, 0.08),
        ("Tornado DDT", "aerial", 56, 64, 0.12),
        ("Bicycle Knee", "strike", 52, 55, 0.07),
    ],
}


# Standard moves any wrestler can use - organized by category
STANDARD_MOVES = {
    "strikes": [
        ("Forearm Smash", "strike", 25, 20, 0.02),
        ("Knife Edge Chop", "strike", 20, 30, 0.01),
        ("European Uppercut", "strike", 28, 25, 0.02),
        ("Dropkick", "strike", 30, 35, 0.03),
        ("Big Boot", "strike", 32, 30, 0.03),
        ("Clothesline", "strike", 28, 25, 0.02),
        ("Back Elbow", "strike", 22, 18, 0.01),
        ("Spinning Heel Kick", "strike", 35, 40, 0.04),
        ("Punch Combo", "strike", 20, 15, 0.01),
        ("Jawbreaker", "strike", 30, 25, 0.03),
    ],
    "grapples": [
        ("Body Slam", "power", 25, 22, 0.02),
        ("Suplex", "power", 35, 30, 0.05),
        ("Hip Toss", "power", 20, 20, 0.02),
        ("Arm Drag", "power", 15, 25, 0.01),
        ("Scoop Slam", "power", 28, 22, 0.03),
        ("Snap Mare", "power", 18, 18, 0.02),
        ("Headlock Takeover", "power", 15, 12, 0.01),
        ("Gutwrench Suplex", "power", 38, 32, 0.06),
        ("Fisherman Suplex", "power", 40, 38, 0.06),
        ("Vertical Suplex", "power", 32, 28, 0.04),
    ],
    "submissions": [
        ("Headlock", "submission", 10, 8, 0.01),
        ("Armbar", "submission", 25, 20, 0.03),
        ("Sleeper Hold", "submission", 20, 15, 0.02),
        ("Boston Crab", "submission", 30, 28, 0.04),
        ("Chinlock", "submission", 12, 8, 0.01),
        ("Crossface", "submission", 35, 32, 0.05),
        ("Fujiwara Armbar", "submission", 28, 25, 0.04),
        ("Surfboard Stretch", "submission", 22, 30, 0.03),
    ],
    "aerial": [
        ("Elbow Drop", "aerial", 25, 28, 0.04),
        ("Leg Drop (from second rope)", "aerial", 28, 30, 0.05),
        ("Crossbody", "aerial", 32, 40, 0.08),
        ("Missile Dropkick", "aerial", 35, 42, 0.10),
        ("Diving Axe Handle", "aerial", 22, 25, 0.04),
        ("Senton", "aerial", 30, 35, 0.08),
    ],
    "dirty": [
        ("Eye Gouge", "dirty", 15, 10, 0.01),
        ("Low Blow", "dirty", 40, 35, 0.02),
        ("Rope Choke", "dirty", 12, 10, 0.01),
        ("Hair Pull", "dirty", 8, 10, 0.01),
        ("Thumb to the Eye", "dirty", 12, 12, 0.01),
        ("Foreign Object (hidden)", "dirty", 35, 20, 0.03),
        ("Exposed Turnbuckle Shot", "dirty", 30, 25, 0.06),
    ],
}


# Weapon moves for hardcore/no-DQ matches
WEAPON_MOVES = {
    "steel_chair": [
        ("Chair Shot to the Back", "weapon", 50, 55, 0.12),
        ("Chair Shot to the Head", "weapon", 70, 60, 0.35),
        ("Con-chair-to", "weapon", 80, 70, 0.45),
        ("Chair Wedged in Turnbuckle", "weapon", 55, 58, 0.15),
        ("Chair-assisted DDT", "weapon", 65, 62, 0.20),
    ],
    "steel_steps": [
        ("Steps to the Face", "weapon", 60, 55, 0.25),
        ("Drop Toe Hold into Steps", "weapon", 55, 58, 0.20),
        ("Powerbomb onto Steps", "weapon", 75, 72, 0.35),
    ],
    "kendo_stick": [
        ("Kendo Stick Strike", "weapon", 35, 45, 0.06),
        ("Kendo Stick Flurry", "weapon", 50, 55, 0.08),
        ("Kendo Stick Across the Back", "weapon", 40, 48, 0.07),
    ],
    "table": [
        ("Suplex Through Table", "weapon", 70, 80, 0.20),
        ("Powerbomb Through Table", "weapon", 75, 85, 0.25),
        ("Elbow Drop Through Table", "weapon", 72, 88, 0.28),
        ("Chokeslam Through Table", "weapon", 68, 82, 0.22),
        ("Spear Through Table", "weapon", 70, 85, 0.20),
    ],
    "ladder": [
        ("Ladder Shot", "weapon", 55, 50, 0.18),
        ("Suplex onto Ladder", "weapon", 65, 70, 0.28),
        ("Sunset Flip Powerbomb off Ladder", "weapon", 85, 95, 0.40),
        ("Splash off Ladder", "weapon", 80, 92, 0.38),
        ("Falling off Ladder", "weapon", 60, 75, 0.35),
    ],
    "barbed_wire": [
        ("Barbed Wire Bat Strike", "weapon", 60, 55, 0.25),
        ("Irish Whip into Barbed Wire", "weapon", 55, 58, 0.22),
        ("Barbed Wire Board Slam", "weapon", 75, 68, 0.35),
        ("Barbed Wire Wrapped Fist", "weapon", 50, 50, 0.18),
    ],
    "light_tubes": [
        ("Light Tube Shot", "weapon", 55, 60, 0.20),
        ("Light Tube Bundle", "weapon", 70, 72, 0.30),
        ("Suplex onto Light Tubes", "weapon", 78, 78, 0.38),
    ],
    "thumbtacks": [
        ("Back Body Drop onto Tacks", "weapon", 60, 75, 0.15),
        ("Slam onto Thumbtacks", "weapon", 65, 78, 0.18),
        ("Face-first into Tacks", "weapon", 70, 80, 0.22),
    ],
}


# Weapons available by match type violence level
WEAPONS_BY_VIOLENCE = {
    4: ["steel_chair", "kendo_stick"],
    5: ["steel_chair", "steel_steps", "kendo_stick", "table"],
    6: ["steel_chair", "steel_steps", "kendo_stick", "table", "ladder"],
    7: ["steel_chair", "steel_steps", "kendo_stick", "table", "ladder"],
    8: ["steel_chair", "steel_steps", "kendo_stick", "table", "ladder", "barbed_wire"],
    9: ["steel_chair", "steel_steps", "kendo_stick", "table", "ladder", "barbed_wire", "light_tubes"],
    10: ["steel_chair", "steel_steps", "kendo_stick", "table", "ladder", "barbed_wire", "light_tubes", "thumbtacks"],
}


# Crowd spot / taunt moves that build heat/pops
CROWD_SPOTS = [
    ("Play to the crowd", "taunt", 0, 40, 0.0),
    ("Flex and pose", "taunt", 0, 30, 0.0),
    ("Crotch chop", "taunt", 0, 35, 0.0),
    ("Throat slash gesture", "taunt", 0, 32, 0.0),
    ("Point to WrestleMania sign", "taunt", 0, 50, 0.0),
    ("Set up the finisher taunt", "taunt", 0, 55, 0.0),
    ("Trash talk the opponent", "taunt", 0, 28, 0.0),
    ("Remove elbow pad / wrist tape", "taunt", 0, 45, 0.0),
]


# Counter / reversal descriptions
COUNTERS = [
    "ducks the clothesline and hits a back elbow",
    "catches the kick and sweeps the leg",
    "reverses the Irish whip",
    "counters the suplex into a small package",
    "blocks the punch and fires back with a flurry",
    "sidesteps the charge and lets them crash into the turnbuckle",
    "catches the dive and turns it into a powerslam",
    "reverses the hold into one of their own",
    "slips out the back door of the suplex",
    "drops down and pulls the top rope, sending them tumbling to the floor",
]


# Near-fall descriptions for dramatic kickouts
NEAR_FALLS = [
    "ONE... TWO... KICKOUT! Just barely!",
    "ONE... TWO... THR-NO! Shoulder up at the last possible second!",
    "The cover! ONE... TWO... TWO AND A HALF! How did they kick out?!",
    "Hooks the leg! ONE... TWO... NO! They got the shoulder up!",
    "ONE... TWO... KICKOUT! The crowd cannot believe it!",
    "Lateral press! ONE... TWO... THR-KICKOUT! This match continues!",
    "ONE... TWO... FOOT ON THE ROPE! Ring awareness saves them!",
]


# Match pacing descriptions
PACING = {
    "feeling_out": [
        "Both wrestlers circle each other, testing the waters.",
        "A collar-and-elbow tie-up as they jockey for position.",
        "They lock up, neither giving an inch.",
        "Cautious start as both competitors size each other up.",
    ],
    "building": [
        "The pace is picking up now.",
        "They're trading blows back and forth!",
        "The momentum is shifting with every exchange.",
        "The crowd is getting into this one.",
    ],
    "heat_segment": [
        "The punishment continues relentlessly.",
        "Working over the injured body part with surgical precision.",
        "Wearing them down, grinding away at their will to fight.",
        "Every hold is locked in tighter. Escape seems impossible.",
    ],
    "comeback": [
        "They're fighting back! The crowd is on their feet!",
        "Second wind! Where is this energy coming from?!",
        "You can't keep a fighter down forever! Here comes the comeback!",
        "Feeding off the energy of the crowd!",
    ],
    "finishing_stretch": [
        "This has to be it! Everything they've got!",
        "Both wrestlers are running on fumes!",
        "Near fall after near fall! Neither one will stay down!",
        "The match has reached a fever pitch!",
    ],
}


def get_finishers_for_style(style_id):
    """Return the finisher list for a given wrestling style."""
    return FINISHERS_BY_STYLE.get(style_id, FINISHERS_BY_STYLE["hybrid"])


def get_signatures_for_style(style_id):
    """Return the signature move list for a given wrestling style."""
    return SIGNATURES_BY_STYLE.get(style_id, SIGNATURES_BY_STYLE["hybrid"])


def get_available_weapons(violence_level):
    """Return weapons available at a given violence level."""
    # Find the highest threshold that doesn't exceed the violence level
    available = []
    for threshold in sorted(WEAPONS_BY_VIOLENCE.keys()):
        if threshold <= violence_level:
            available = WEAPONS_BY_VIOLENCE[threshold]
    return available


def get_weapon_moves(weapon_id):
    """Return the move list for a specific weapon."""
    return WEAPON_MOVES.get(weapon_id, [])
