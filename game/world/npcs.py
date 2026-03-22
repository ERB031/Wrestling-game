"""NPC wrestler generator.

Generates random NPC wrestlers with skills, personalities, and backstories
appropriate to the promotion tier they inhabit.
"""

import random
import uuid

from game.character.wrestler import Wrestler
from data.names import (
    FIRST_NAMES, LAST_NAMES, NICKNAMES, RING_NAME_PATTERNS,
    FINISHER_VERBS, FINISHER_NOUNS,
)
from data.constants import SKILLS, SKILL_MIN, SKILL_MAX


# ---------------------------------------------------------------------------
# Personality and alignment pools
# ---------------------------------------------------------------------------

PERSONALITIES = [
    "politician",
    "workrate_junkie",
    "partier",
    "company_man",
    "rebel",
    "mentor",
    "bully",
    "nice_guy",
]

STYLES = [
    "technical",
    "high_flying",
    "power",
    "brawling",
    "hardcore",
    "strong_style",
    "entertainment",
    "puroresu",
    "deathmatch",
    "comedy",
]

ALIGNMENT_RANGES = {
    "mega_heel": (-100, -60),
    "heel": (-59, -20),
    "tweener": (-19, 19),
    "face": (20, 59),
    "mega_face": (60, 100),
}

# Skill ranges by promotion tier (min, max)
TIER_SKILL_RANGES = {
    1: (5, 35),
    2: (20, 55),
    3: (35, 75),
    4: (50, 90),
}

# Popularity ranges by promotion tier
TIER_POPULARITY_RANGES = {
    1: (0, 10),
    2: (5, 30),
    3: (15, 60),
    4: (30, 85),
}


# ---------------------------------------------------------------------------
# Name generation
# ---------------------------------------------------------------------------

def _generate_ring_name():
    """Generate a random ring name from the name pools."""
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    nickname = random.choice(NICKNAMES)
    pattern = random.choice(RING_NAME_PATTERNS)
    return pattern.format(first=first, last=last, nickname=nickname)


def _generate_real_name():
    """Generate a mundane real name."""
    mundane_firsts = [
        "James", "John", "Robert", "Michael", "David", "William", "Richard",
        "Joseph", "Thomas", "Charles", "Daniel", "Matthew", "Anthony", "Mark",
        "Steven", "Paul", "Andrew", "Kenneth", "George", "Brian", "Edward",
        "Timothy", "Jason", "Jeffrey", "Ryan", "Gary", "Nicholas", "Eric",
        "Stephen", "Larry", "Scott", "Frank", "Kevin", "Greg", "Raymond",
    ]
    mundane_lasts = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
        "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Wilson",
        "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee",
        "Thompson", "White", "Harris", "Clark", "Lewis", "Robinson", "Walker",
        "Young", "Allen", "King", "Wright", "Hill", "Green", "Adams", "Baker",
    ]
    return f"{random.choice(mundane_firsts)} {random.choice(mundane_lasts)}"


def _generate_finisher():
    """Generate a random finisher name."""
    return f"{random.choice(FINISHER_VERBS)} {random.choice(FINISHER_NOUNS)}"


# ---------------------------------------------------------------------------
# NPC generation
# ---------------------------------------------------------------------------

def generate_npc(tier=2, style_override=None, promotion_id=""):
    """Generate a single NPC wrestler appropriate for the given promotion tier.

    Parameters
    ----------
    tier : int
        Promotion tier (1–4), determines skill ranges.
    style_override : str or None
        Force a specific wrestling style; otherwise picked at random.
    promotion_id : str
        The promotion the NPC belongs to (stored on the wrestler).

    Returns
    -------
    Wrestler
    """
    skill_lo, skill_hi = TIER_SKILL_RANGES.get(tier, (20, 55))
    pop_lo, pop_hi = TIER_POPULARITY_RANGES.get(tier, (5, 30))

    # Pick style
    style = style_override or random.choice(STYLES)

    # Build skills with some variance and style bias
    skills = {}
    for skill in SKILLS:
        base = random.randint(skill_lo, skill_hi)
        # Style biases
        if style == "technical" and skill in ("in_ring", "psychology"):
            base += random.randint(5, 15)
        elif style == "high_flying" and skill in ("athleticism", "in_ring"):
            base += random.randint(5, 15)
        elif style == "power" and skill in ("power", "durability", "look"):
            base += random.randint(5, 15)
        elif style == "brawling" and skill in ("power", "durability", "violence"):
            base += random.randint(5, 15)
        elif style == "hardcore" and skill in ("violence", "durability"):
            base += random.randint(10, 20)
        elif style == "strong_style" and skill in ("in_ring", "power", "durability"):
            base += random.randint(5, 15)
        elif style == "entertainment" and skill in ("charisma", "mic_work", "look"):
            base += random.randint(5, 15)
        elif style == "puroresu" and skill in ("in_ring", "psychology", "durability"):
            base += random.randint(5, 15)
        elif style == "deathmatch" and skill in ("violence", "durability"):
            base += random.randint(10, 20)
        elif style == "comedy" and skill in ("charisma", "mic_work"):
            base += random.randint(5, 15)
        skills[skill] = max(SKILL_MIN, min(SKILL_MAX, base))

    # Random alignment
    alignment_type = random.choice(list(ALIGNMENT_RANGES.keys()))
    align_lo, align_hi = ALIGNMENT_RANGES[alignment_type]
    alignment = random.randint(align_lo, align_hi)

    # Random personality
    personality = random.choice(PERSONALITIES)

    # Age depends loosely on tier
    if tier <= 1:
        age = random.randint(16, 25)
    elif tier == 2:
        age = random.randint(19, 35)
    elif tier == 3:
        age = random.randint(22, 40)
    else:
        age = random.randint(25, 45)

    npc = Wrestler(
        real_name=_generate_real_name(),
        ring_name=_generate_ring_name(),
        age=age,
        style_id=style,
        skills=skills,
        skill_xp={s: 0 for s in SKILLS},
        health=100,
        alignment=alignment,
        booked_alignment=alignment,
        popularity=random.randint(pop_lo, pop_hi),
        backstage_rep=random.randint(-30, 30),
        momentum=random.randint(-3, 3),
        money=random.randint(0, tier * 5000),
        current_promotion=promotion_id,
        finisher_name=_generate_finisher(),
        personality=personality,
        is_player=False,
        npc_id=str(uuid.uuid4())[:8],
    )

    # Some NPCs might use substances
    if personality == "partier":
        npc.alcohol_level = random.randint(20, 60)
        npc.drug_level = random.randint(10, 40)
    if random.random() < 0.15:
        npc.steroid_use = True
        npc.steroid_cumulative = random.randint(4, 52)
        # Slight stat bump already baked in via Wrestler.get_effective_skill

    return npc


def generate_roster(promotion):
    """Generate a full roster of NPC wrestlers for a promotion.

    Parameters
    ----------
    promotion : Promotion
        The promotion object (from game.world.promotions).

    Returns
    -------
    list[Wrestler]
    """
    # Roster size varies by tier
    size_ranges = {
        1: (6, 10),
        2: (10, 16),
        3: (14, 20),
        4: (16, 20),
    }
    lo, hi = size_ranges.get(promotion.tier, (8, 14))
    count = min(random.randint(lo, hi), promotion.roster_size)

    roster = []
    styles = promotion.style_preferences or STYLES

    for _ in range(count):
        style = random.choice(styles)
        npc = generate_npc(
            tier=promotion.tier,
            style_override=style,
            promotion_id=promotion.id,
        )
        roster.append(npc)

    return roster


def generate_all_rosters(promotions_dict):
    """Generate rosters for every promotion in the dict.

    Parameters
    ----------
    promotions_dict : dict[str, Promotion]

    Returns
    -------
    dict[str, list[Wrestler]]
        Mapping of promotion id -> list of NPC wrestlers.
    """
    rosters = {}
    for promo_id, promo in promotions_dict.items():
        rosters[promo_id] = generate_roster(promo)
    return rosters
