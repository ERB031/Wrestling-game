"""Skill progression system."""

import random
from data.constants import (
    SKILLS, SKILL_DISPLAY_NAMES, SKILL_MAX, TRAINING_XP_BASE,
    TRAINING_XP_VARIANCE, PEAK_AGE_END, DECLINE_RATE,
)
from game.display import (
    print_menu, print_subheader, colored, Colors, bold, dim,
    print_stat_bar,
)


def present_training_options(wrestler):
    """Show training menu and apply training."""
    print_subheader("TRAINING")
    print("  Pick a skill to focus on this week:")
    print()

    options = []
    for skill_id in SKILLS:
        name = SKILL_DISPLAY_NAMES[skill_id]
        current = wrestler.skills[skill_id]
        options.append((name, f"Current: {current}"))

    choice = print_menu(options, "Train")
    skill_id = SKILLS[choice]

    xp = TRAINING_XP_BASE + random.randint(-TRAINING_XP_VARIANCE, TRAINING_XP_VARIANCE)

    # Style bonus
    from game.character.backstory import WRESTLING_STYLES
    style = WRESTLING_STYLES.get(wrestler.style_id, {})
    if skill_id in style.get("skill_bonuses", {}):
        xp = int(xp * 1.2)
        print(f"  Your {style['name']} style gives you a training bonus!")

    # Age penalty for physical skills
    if wrestler.age > PEAK_AGE_END and skill_id in ("athleticism", "power", "durability"):
        xp = int(xp * 0.7)
        _msg = "Your body doesn't respond like it used to..."
        print(f"  {dim(_msg)}")

    leveled = wrestler.add_skill_xp(skill_id, xp)
    name = SKILL_DISPLAY_NAMES[skill_id]
    current = wrestler.skills[skill_id]

    print(f"\n  Training {name}... +{xp} XP")
    if leveled:
        print(f"  {colored(f'{name} increased to {current}!', Colors.GREEN)}")

    # Small health cost from training
    wrestler.health = max(50, wrestler.health - random.randint(2, 5))


def train_skill(wrestler, skill_id):
    """Directly train a specific skill (used by events)."""
    xp = TRAINING_XP_BASE + random.randint(0, TRAINING_XP_VARIANCE)
    return wrestler.add_skill_xp(skill_id, xp)


def gain_match_xp(wrestler, match_result):
    """Gain XP from a match based on what happened."""
    base_xp = 8
    rating = match_result.get("rating", 2.0)

    # Better matches = more XP
    xp_mult = 1.0 + (rating - 2.0) * 0.3

    # Always gain some in_ring
    wrestler.add_skill_xp("in_ring", int(base_xp * xp_mult))
    wrestler.add_skill_xp("psychology", int(base_xp * 0.5 * xp_mult))

    # Style-specific gains
    match_type = match_result.get("match_type", "standard_singles")
    if match_type in ("hardcore", "barbed_wire", "deathmatch", "tlc", "tables"):
        wrestler.add_skill_xp("violence", int(base_xp * 0.8 * xp_mult))
        wrestler.add_skill_xp("durability", int(base_xp * 0.5 * xp_mult))
    elif match_type in ("ladder", "triple_threat", "fatal_four_way"):
        wrestler.add_skill_xp("athleticism", int(base_xp * 0.6 * xp_mult))
    elif match_type in ("iron_man", "last_man_standing", "i_quit"):
        wrestler.add_skill_xp("durability", int(base_xp * 0.8 * xp_mult))
        wrestler.add_skill_xp("psychology", int(base_xp * 0.5 * xp_mult))

    # Promo during match
    if match_result.get("had_promo"):
        wrestler.add_skill_xp("mic_work", int(base_xp * 0.6 * xp_mult))
        wrestler.add_skill_xp("charisma", int(base_xp * 0.4 * xp_mult))


def check_skill_milestones(wrestler):
    """Check if any skills hit notable thresholds."""
    milestones = {50: "competent", 70: "skilled", 85: "elite", 95: "legendary"}
    for skill_id in SKILLS:
        value = wrestler.skills[skill_id]
        name = SKILL_DISPLAY_NAMES[skill_id]
        for threshold, label in milestones.items():
            if value == threshold:
                print(f"  {colored(f'★ {name} has reached {label} level ({threshold})!', Colors.GOLD)}")


def apply_age_decline(wrestler):
    """Reduce physical skills based on age past peak."""
    if wrestler.age <= PEAK_AGE_END:
        return

    years_past = wrestler.age - PEAK_AGE_END
    physical_skills = ["athleticism", "power", "durability"]

    for skill in physical_skills:
        decline = int(DECLINE_RATE * years_past * random.uniform(0.5, 1.5))
        if decline > 0 and wrestler.skills[skill] > 20:
            wrestler.skills[skill] = max(20, wrestler.skills[skill] - decline)

    # Charisma and look decline slower
    if years_past > 5:
        for skill in ["look", "charisma"]:
            decline = int(DECLINE_RATE * 0.3 * years_past * random.uniform(0.3, 1.0))
            if decline > 0 and wrestler.skills[skill] > 25:
                wrestler.skills[skill] = max(25, wrestler.skills[skill] - decline)

    if years_past >= 3:
        print(f"  {dim('Father Time is undefeated. Physical skills are declining.')}")
