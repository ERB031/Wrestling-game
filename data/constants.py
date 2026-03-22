"""Game balance constants and tuning knobs."""

# Skill ranges
SKILL_MIN = 1
SKILL_MAX = 100
SKILL_DEFAULT = 20

# Skills list
SKILLS = [
    "mic_work",
    "in_ring",
    "durability",
    "violence",
    "charisma",
    "psychology",
    "athleticism",
    "power",
    "look",
]

SKILL_DISPLAY_NAMES = {
    "mic_work": "Mic Work",
    "in_ring": "In-Ring",
    "durability": "Durability",
    "violence": "Violence",
    "charisma": "Charisma",
    "psychology": "Psychology",
    "athleticism": "Athleticism",
    "power": "Power",
    "look": "Look",
}

# XP needed per skill level (base, scaled by current level)
XP_BASE = 10
XP_GROWTH_FACTOR = 1.08  # Each level costs 8% more XP

# Training XP gain per session
TRAINING_XP_BASE = 15
TRAINING_XP_VARIANCE = 5

# Alignment
ALIGNMENT_MIN = -100
ALIGNMENT_MAX = 100
ALIGNMENT_ZONES = {
    "mega_heel": (-100, -60),
    "heel": (-60, -20),
    "tweener": (-20, 20),
    "face": (20, 60),
    "mega_face": (60, 100),
}

ALIGNMENT_NAMES = {
    "mega_heel": "Mega Heel",
    "heel": "Heel",
    "tweener": "Tweener",
    "face": "Face",
    "mega_face": "Mega Face",
}

# Popularity
POPULARITY_MIN = 0
POPULARITY_MAX = 100

# Reputation (backstage)
REPUTATION_MIN = -100
REPUTATION_MAX = 100

# Body parts that can be damaged/injured
BODY_PARTS = ["head", "neck", "back", "left_knee", "right_knee", "left_shoulder", "right_shoulder", "ribs", "wrist"]

# Body damage thresholds
BODY_DAMAGE_WARNING = 50
BODY_DAMAGE_CRITICAL = 80
BODY_DAMAGE_MAX = 100

# Injury severity levels
INJURY_MINOR = 1
INJURY_MODERATE = 2
INJURY_MAJOR = 3
INJURY_CAREER_THREATENING = 4

# Weeks per severity
INJURY_RECOVERY_WEEKS = {
    1: (1, 2),
    2: (3, 8),
    3: (8, 24),
    4: (20, 52),
}

# Addiction scale
ADDICTION_MIN = 0
ADDICTION_MAX = 100
ADDICTION_CASUAL = 20
ADDICTION_CRAVING = 40
ADDICTION_PROBLEM = 60
ADDICTION_SEVERE = 80
ADDICTION_CRITICAL = 95

# Substance types
SUBSTANCES = ["alcohol", "painkillers", "recreational_drugs", "steroids"]

# Steroid stat boosts
STEROID_LIGHT_BOOST = {"power": 3, "look": 2, "athleticism": 1}
STEROID_HEAVY_BOOST = {"power": 6, "look": 4, "athleticism": 2}

# Age effects
PEAK_AGE_START = 25
PEAK_AGE_END = 33
DECLINE_AGE_START = 34
DECLINE_RATE = 0.5  # Stat points lost per year past decline age

# Career
RETIREMENT_MIN_AGE = 30
RETIREMENT_MAX_AGE = 55
WEEKS_PER_YEAR = 52

# Match rating
MATCH_RATING_MIN = 0.0
MATCH_RATING_MAX = 5.0
MATCH_RATING_MELTZER_BONUS = 0.5  # Can exceed 5.0 for legendary matches

# Financial
STARTING_MONEY = 500
WEEKLY_EXPENSES = 200

# Promotion tiers
TIER_BACKYARD = 1
TIER_INDIE = 2
TIER_MID = 3
TIER_MAJOR = 4

# Shows per week by tier
SHOWS_PER_WEEK = {
    1: 1,
    2: 1,
    3: 2,
    4: 3,
}

# Random event chances per week
RANDOM_EVENT_CHANCE = 0.4  # 40% chance per week
MAX_RANDOM_EVENTS_PER_WEEK = 2

# Relationship scale
RELATIONSHIP_MIN = -100
RELATIONSHIP_MAX = 100
