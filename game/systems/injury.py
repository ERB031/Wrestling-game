"""Injury system - types, rolling, recovery, and graphic descriptions."""

import random
from game.character.wrestler import Injury
from game.display import colored, Colors, print_injury_report, bold, dim
from data.constants import (
    INJURY_MINOR, INJURY_MODERATE, INJURY_MAJOR, INJURY_CAREER_THREATENING,
    BODY_PARTS, BODY_DAMAGE_CRITICAL,
)


INJURY_TABLE = {
    "head": [
        {"name": "Mild Concussion", "severity": INJURY_MINOR, "weeks": (1, 2), "chronic_chance": 0.05,
         "stat_penalties": {"in_ring": 3, "psychology": 2}, "damage": 8},
        {"name": "Concussion", "severity": INJURY_MODERATE, "weeks": (2, 5), "chronic_chance": 0.15,
         "stat_penalties": {"in_ring": 5, "psychology": 5, "charisma": 3}, "damage": 15},
        {"name": "Severe Concussion", "severity": INJURY_MAJOR, "weeks": (6, 14), "chronic_chance": 0.3,
         "stat_penalties": {"in_ring": 10, "psychology": 8, "charisma": 5, "athleticism": 5}, "damage": 25},
        {"name": "Fractured Skull", "severity": INJURY_CAREER_THREATENING, "weeks": (16, 40), "chronic_chance": 0.5,
         "stat_penalties": {"in_ring": 15, "psychology": 10, "athleticism": 10}, "damage": 40},
    ],
    "neck": [
        {"name": "Stinger", "severity": INJURY_MINOR, "weeks": (1, 2), "chronic_chance": 0.05,
         "stat_penalties": {"power": 3}, "damage": 5},
        {"name": "Neck Strain", "severity": INJURY_MODERATE, "weeks": (3, 6), "chronic_chance": 0.1,
         "stat_penalties": {"power": 5, "in_ring": 3}, "damage": 12},
        {"name": "Herniated Disc (Cervical)", "severity": INJURY_MAJOR, "weeks": (10, 24), "chronic_chance": 0.4,
         "stat_penalties": {"power": 8, "in_ring": 8, "athleticism": 5}, "damage": 30},
        {"name": "Broken Neck", "severity": INJURY_CAREER_THREATENING, "weeks": (24, 52), "chronic_chance": 0.7,
         "stat_penalties": {"power": 15, "in_ring": 15, "athleticism": 15, "durability": 10}, "damage": 50},
    ],
    "back": [
        {"name": "Back Spasm", "severity": INJURY_MINOR, "weeks": (1, 2), "chronic_chance": 0.05,
         "stat_penalties": {"power": 2, "athleticism": 2}, "damage": 5},
        {"name": "Strained Lower Back", "severity": INJURY_MODERATE, "weeks": (2, 6), "chronic_chance": 0.15,
         "stat_penalties": {"power": 5, "athleticism": 5}, "damage": 10},
        {"name": "Herniated Disc (Lumbar)", "severity": INJURY_MAJOR, "weeks": (8, 20), "chronic_chance": 0.4,
         "stat_penalties": {"power": 10, "athleticism": 8, "durability": 5}, "damage": 30},
        {"name": "Spinal Stenosis", "severity": INJURY_CAREER_THREATENING, "weeks": (20, 52), "chronic_chance": 0.8,
         "stat_penalties": {"power": 15, "athleticism": 15, "durability": 15, "in_ring": 10}, "damage": 45},
    ],
    "left_knee": [
        {"name": "Hyperextended Knee", "severity": INJURY_MINOR, "weeks": (1, 3), "chronic_chance": 0.05,
         "stat_penalties": {"athleticism": 3}, "damage": 5},
        {"name": "Torn Meniscus", "severity": INJURY_MODERATE, "weeks": (4, 8), "chronic_chance": 0.2,
         "stat_penalties": {"athleticism": 8, "in_ring": 3}, "damage": 15},
        {"name": "Torn ACL", "severity": INJURY_MAJOR, "weeks": (12, 36), "chronic_chance": 0.5,
         "stat_penalties": {"athleticism": 15, "in_ring": 8, "power": 5}, "damage": 35},
        {"name": "Shattered Kneecap", "severity": INJURY_CAREER_THREATENING, "weeks": (26, 52), "chronic_chance": 0.7,
         "stat_penalties": {"athleticism": 20, "in_ring": 15, "power": 10}, "damage": 50},
    ],
    "right_knee": [
        {"name": "Hyperextended Knee", "severity": INJURY_MINOR, "weeks": (1, 3), "chronic_chance": 0.05,
         "stat_penalties": {"athleticism": 3}, "damage": 5},
        {"name": "Torn Meniscus", "severity": INJURY_MODERATE, "weeks": (4, 8), "chronic_chance": 0.2,
         "stat_penalties": {"athleticism": 8, "in_ring": 3}, "damage": 15},
        {"name": "Torn ACL", "severity": INJURY_MAJOR, "weeks": (12, 36), "chronic_chance": 0.5,
         "stat_penalties": {"athleticism": 15, "in_ring": 8, "power": 5}, "damage": 35},
        {"name": "Shattered Kneecap", "severity": INJURY_CAREER_THREATENING, "weeks": (26, 52), "chronic_chance": 0.7,
         "stat_penalties": {"athleticism": 20, "in_ring": 15, "power": 10}, "damage": 50},
    ],
    "left_shoulder": [
        {"name": "Shoulder Strain", "severity": INJURY_MINOR, "weeks": (1, 2), "chronic_chance": 0.05,
         "stat_penalties": {"power": 3}, "damage": 5},
        {"name": "Shoulder Separation", "severity": INJURY_MODERATE, "weeks": (3, 8), "chronic_chance": 0.15,
         "stat_penalties": {"power": 8, "in_ring": 3}, "damage": 12},
        {"name": "Torn Rotator Cuff", "severity": INJURY_MAJOR, "weeks": (10, 24), "chronic_chance": 0.4,
         "stat_penalties": {"power": 12, "in_ring": 8, "athleticism": 5}, "damage": 28},
    ],
    "right_shoulder": [
        {"name": "Shoulder Strain", "severity": INJURY_MINOR, "weeks": (1, 2), "chronic_chance": 0.05,
         "stat_penalties": {"power": 3}, "damage": 5},
        {"name": "Shoulder Separation", "severity": INJURY_MODERATE, "weeks": (3, 8), "chronic_chance": 0.15,
         "stat_penalties": {"power": 8, "in_ring": 3}, "damage": 12},
        {"name": "Torn Rotator Cuff", "severity": INJURY_MAJOR, "weeks": (10, 24), "chronic_chance": 0.4,
         "stat_penalties": {"power": 12, "in_ring": 8, "athleticism": 5}, "damage": 28},
    ],
    "ribs": [
        {"name": "Bruised Ribs", "severity": INJURY_MINOR, "weeks": (1, 2), "chronic_chance": 0.02,
         "stat_penalties": {"durability": 3}, "damage": 4},
        {"name": "Cracked Ribs", "severity": INJURY_MODERATE, "weeks": (3, 6), "chronic_chance": 0.1,
         "stat_penalties": {"durability": 8, "power": 3}, "damage": 12},
        {"name": "Broken Ribs", "severity": INJURY_MAJOR, "weeks": (6, 12), "chronic_chance": 0.2,
         "stat_penalties": {"durability": 12, "power": 8, "athleticism": 5}, "damage": 20},
    ],
    "wrist": [
        {"name": "Sprained Wrist", "severity": INJURY_MINOR, "weeks": (1, 2), "chronic_chance": 0.02,
         "stat_penalties": {"in_ring": 2}, "damage": 3},
        {"name": "Fractured Wrist", "severity": INJURY_MODERATE, "weeks": (4, 8), "chronic_chance": 0.1,
         "stat_penalties": {"in_ring": 5, "power": 3}, "damage": 10},
    ],
}


def roll_for_injury(wrestler, match_type_id, approach="safe"):
    """Determine if an injury occurs during a match. Returns Injury or None."""
    from game.match.match_types import MATCH_TYPES

    match_type = MATCH_TYPES.get(match_type_id, {})
    injury_mult = match_type.get("injury_multiplier", 1.0)

    # Base injury chance
    base_chance = 0.08

    # Approach modifiers
    approach_mods = {
        "all_out": 1.8,
        "safe": 0.6,
        "stiff": 1.5,
        "cheat": 0.8,
        "put_over": 1.0,
    }
    base_chance *= approach_mods.get(approach, 1.0)

    # Match type multiplier
    base_chance *= injury_mult

    # Low durability increases risk
    durability = wrestler.get_effective_skill("durability")
    if durability < 30:
        base_chance *= 1.5
    elif durability > 70:
        base_chance *= 0.7

    # Existing body damage increases risk
    for part, damage in wrestler.body_damage.items():
        if damage > BODY_DAMAGE_CRITICAL:
            base_chance *= 1.3
            break

    # Health going into match
    if wrestler.health < 50:
        base_chance *= 1.5

    # Age factor
    if wrestler.age > 35:
        base_chance *= 1.0 + (wrestler.age - 35) * 0.05

    # Roll
    if random.random() > base_chance:
        return None

    # Determine body part (weighted by existing damage)
    body_part = pick_injured_body_part(wrestler)

    # Determine severity (weighted by match violence)
    severity_weights = _get_severity_weights(match_type_id, wrestler)
    injuries_for_part = INJURY_TABLE.get(body_part, INJURY_TABLE["ribs"])
    filtered = [i for i in injuries_for_part if i["severity"] in severity_weights]
    if not filtered:
        filtered = injuries_for_part[:1]

    weights = [severity_weights.get(i["severity"], 1) for i in filtered]
    injury_data = random.choices(filtered, weights=weights, k=1)[0]

    # Create injury
    weeks = random.randint(injury_data["weeks"][0], injury_data["weeks"][1])
    chronic = random.random() < injury_data["chronic_chance"]

    injury = Injury(
        body_part=body_part,
        severity=injury_data["severity"],
        description=injury_data["name"],
        weeks_remaining=weeks,
        chronic=chronic,
        stat_penalties=dict(injury_data["stat_penalties"]),
    )

    # Apply body damage
    wrestler.body_damage[body_part] = min(100, wrestler.body_damage[body_part] + injury_data["damage"])

    return injury


def _get_severity_weights(match_type_id, wrestler):
    """Get severity probability weights based on context."""
    from game.match.match_types import MATCH_TYPES
    mt = MATCH_TYPES.get(match_type_id, {})
    violence = mt.get("violence_requirement", 0)

    if violence >= 8:
        return {1: 2, 2: 3, 3: 3, 4: 1}
    elif violence >= 5:
        return {1: 3, 2: 3, 3: 2, 4: 0.3}
    elif violence >= 3:
        return {1: 4, 2: 3, 3: 1, 4: 0.1}
    else:
        return {1: 5, 2: 2, 3: 0.5, 4: 0.05}


def pick_injured_body_part(wrestler):
    """Pick which body part gets injured, weighted by existing damage."""
    parts = list(wrestler.body_damage.keys())
    weights = []
    for part in parts:
        damage = wrestler.body_damage[part]
        weight = 1.0 + (damage / 30.0)  # Higher damage = more likely to re-injure
        weights.append(weight)
    return random.choices(parts, weights=weights, k=1)[0]


def apply_injury(wrestler, injury):
    """Apply an injury to a wrestler."""
    wrestler.injuries.append(injury)
    wrestler.health = max(0, wrestler.health - injury.severity * 10)
    print_injury_report(injury)

    # Graphic description
    desc = describe_injury_graphic(injury)
    if desc:
        print(f"    {colored(desc, Colors.BLOOD)}")


def describe_injury_graphic(injury):
    """Return graphic text description of the injury. Extreme violence for in-ring."""
    descriptions = {
        "Mild Concussion": "Your vision blurs. The lights swim overhead as you try to remember where you are.",
        "Concussion": "Your eyes go glassy. You can't track your opponent. The ref holds up fingers and you guess wrong.",
        "Severe Concussion": "You collapse like a puppet with cut strings. Blood trickles from your ear. The medical team rushes in.",
        "Fractured Skull": "The sickening crack echoes through the arena. Your head splits open like a melon, blood sheeting down your face in a crimson mask. Bone fragments are visible through the gash.",
        "Stinger": "Lightning shoots down your arm. Your fingers go numb. You shake it off but the tingling doesn't stop.",
        "Neck Strain": "You feel something shift in your neck. Every movement sends electric pain down your spine.",
        "Herniated Disc (Cervical)": "Something pops in your neck with a wet crunch. Your arms go weak. You can't feel your fingers.",
        "Broken Neck": "The sound is like a branch snapping. You hit the mat and can't move. Can't feel your legs. The arena goes silent. Medical staff sprint to the ring.",
        "Back Spasm": "Your back locks up mid-move. You crumple to the mat, muscles seizing like a fist clenching your spine.",
        "Strained Lower Back": "Something tears in your lower back. Standing upright becomes agony.",
        "Herniated Disc (Lumbar)": "You feel the disc blow out. White-hot pain radiates from your spine to your toes. You can't stand. Can't breathe.",
        "Spinal Stenosis": "Your spine is failing. Every bump sends shockwaves through your body. Your legs give out. This could be it.",
        "Hyperextended Knee": "Your knee bends the wrong way with a sickening pop. The crowd gasps as you crumble.",
        "Torn Meniscus": "Your knee buckles sideways. You feel cartilage tear like wet paper. The joint swells immediately.",
        "Torn ACL": "POP. The sound is audible to the front row. Your knee explodes with pain. The joint goes completely unstable -- your leg bends where it shouldn't.",
        "Shattered Kneecap": "Your kneecap shatters on impact. You can see the fragments shifting under the skin. Blood pools in the joint. You're screaming before you know it.",
        "Shoulder Strain": "Your shoulder burns. You can still move it, but every lift sends fire through the joint.",
        "Shoulder Separation": "Your shoulder pops out with a grotesque bulge visible under the skin. Your arm hangs dead at your side.",
        "Torn Rotator Cuff": "The muscle rips away from the bone. You grab your shoulder and feel something grinding that shouldn't be grinding. Your arm is useless.",
        "Bruised Ribs": "Pain shoots through your side with every breath. You clutch your ribs and try to keep going.",
        "Cracked Ribs": "You feel ribs crack under the impact. Breathing becomes a knife in your side. You taste blood.",
        "Broken Ribs": "CRACK. Multiple ribs snap like dry twigs. One pushes against your lung -- you gasp but can't get air. Blood froths at your lips.",
        "Sprained Wrist": "Your wrist bends wrong on impact. It swells immediately, throbbing with your heartbeat.",
        "Fractured Wrist": "The bone snaps. You can see the unnatural angle through the swelling. Your hand is useless.",
    }
    return descriptions.get(injury.description, "")


def process_injury_recovery(wrestler):
    """Process weekly injury recovery."""
    for injury in wrestler.injuries:
        if injury.weeks_remaining > 0:
            # Steroid users recover faster
            if wrestler.steroid_use:
                if random.random() < 0.2:
                    injury.weeks_remaining = max(0, injury.weeks_remaining - 1)


def check_career_threatening_injuries(wrestler):
    """Check if accumulated injuries should force retirement."""
    # CTE check
    head_damage = wrestler.body_damage.get("head", 0)
    if head_damage >= 80:
        if random.random() < 0.3:
            return "cte"

    # Neck/spine check
    neck_damage = wrestler.body_damage.get("neck", 0)
    back_damage = wrestler.body_damage.get("back", 0)
    if neck_damage >= 70 or back_damage >= 70:
        if random.random() < 0.2:
            return "spine"

    return None
