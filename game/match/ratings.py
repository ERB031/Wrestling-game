"""Match rating calculation system.

Takes match quality factors and outputs a star rating (0.0 - 5.0+).
Considers: wrestler skills, match type bonus, crowd heat, match approach,
in-ring choices made, injuries during match, and botch chance.
"""

import random
from data.constants import (
    MATCH_RATING_MIN, MATCH_RATING_MAX, MATCH_RATING_MELTZER_BONUS,
)


# Weights for each factor in the final rating
RATING_WEIGHTS = {
    "wrestler_skill": 0.30,      # Combined in-ring ability of both wrestlers
    "psychology": 0.15,          # Match storytelling
    "crowd_heat": 0.15,          # How hot the crowd was
    "match_type_bonus": 0.08,    # Some match types have higher ceilings
    "approach_bonus": 0.10,      # Did the player pick the right approach?
    "choice_quality": 0.12,      # Quality of in-ring decisions
    "drama": 0.10,               # Near-falls, false finishes, dramatic moments
}

# Approach synergy with match types - (approach, narration_flavor) -> bonus
APPROACH_SYNERGY = {
    ("go_all_out", "highspot"): 0.4,
    ("go_all_out", "carnage"): 0.3,
    ("go_all_out", "brutal"): 0.2,
    ("go_all_out", "epic"): 0.3,
    ("play_it_safe", "technical"): 0.3,
    ("play_it_safe", "teamwork"): 0.2,
    ("play_it_safe", "epic"): 0.1,
    ("work_stiff", "brutal"): 0.4,
    ("work_stiff", "endurance"): 0.3,
    ("work_stiff", "gore"): 0.3,
    ("work_stiff", "ultraviolence"): 0.4,
    ("work_stiff", "torture"): 0.3,
    ("cheat_to_win", "brawl"): 0.2,
    ("cheat_to_win", "chaotic"): 0.2,
    ("cheat_to_win", "destruction"): 0.1,
    ("put_them_over", "technical"): 0.3,
    ("put_them_over", "epic"): 0.4,
    ("put_them_over", "spectacle"): 0.3,
    ("put_them_over", "highspot"): 0.2,
}


# Botch chance modifiers by situation
BOTCH_FACTORS = {
    "low_skill": 0.15,           # Base chance when skill < 30
    "mid_skill": 0.05,           # Base chance when skill 30-60
    "high_skill": 0.01,          # Base chance when skill > 60
    "injured_modifier": 0.10,    # Added if wrestler is injured
    "fatigue_modifier": 0.08,    # Added in late match
    "high_risk_modifier": 0.12,  # Added for aerial/dangerous moves
    "substance_modifier": 0.06,  # Added if substance abuse is high
}


def calculate_botch_chance(wrestler, is_high_risk=False, is_fatigued=False):
    """Calculate the chance of a botch for a given wrestler in context."""
    skill = wrestler.get_effective_skill("in_ring")

    if skill > 60:
        chance = BOTCH_FACTORS["high_skill"]
    elif skill > 30:
        chance = BOTCH_FACTORS["mid_skill"]
    else:
        chance = BOTCH_FACTORS["low_skill"]

    # Injury modifier
    if wrestler.is_injured():
        chance += BOTCH_FACTORS["injured_modifier"]

    # Fatigue
    if is_fatigued:
        chance += BOTCH_FACTORS["fatigue_modifier"]

    # High-risk moves
    if is_high_risk:
        chance += BOTCH_FACTORS["high_risk_modifier"]

    # Substance abuse
    total_substance = wrestler.alcohol_level + wrestler.painkiller_level + wrestler.drug_level
    if total_substance > 100:
        chance += BOTCH_FACTORS["substance_modifier"]

    return min(chance, 0.50)  # Cap at 50%


def did_botch(wrestler, is_high_risk=False, is_fatigued=False):
    """Roll for a botch. Returns True if botched."""
    chance = calculate_botch_chance(wrestler, is_high_risk, is_fatigued)
    return random.random() < chance


def calculate_wrestler_skill_score(wrestler1, wrestler2):
    """Calculate combined skill contribution to match quality (0.0 - 1.0)."""
    skills_to_check = ["in_ring", "psychology", "athleticism", "charisma"]

    score1 = sum(wrestler1.get_effective_skill(s) for s in skills_to_check) / (len(skills_to_check) * 100)
    score2 = sum(wrestler2.get_effective_skill(s) for s in skills_to_check) / (len(skills_to_check) * 100)

    # The weaker wrestler drags the match down more than the stronger one lifts it
    combined = (score1 * 0.4 + score2 * 0.4 + min(score1, score2) * 0.2)

    return min(1.0, combined)


def calculate_crowd_heat(wrestler1, wrestler2, match_type_data, approach):
    """Calculate crowd engagement score (0.0 - 1.0)."""
    # Base heat from popularity
    pop_score = (wrestler1.popularity + wrestler2.popularity) / 200.0

    # Alignment contrast bonus - face vs heel is best
    alignment_diff = abs(wrestler1.alignment - wrestler2.alignment)
    contrast_bonus = min(alignment_diff / 200.0, 0.20)

    # Match type excitement
    type_excitement = match_type_data.get("rating_bonus", 0.0) * 0.5

    # Approach affects crowd
    approach_heat = {
        "go_all_out": 0.10,
        "play_it_safe": -0.05,
        "work_stiff": 0.05,
        "cheat_to_win": 0.08,
        "put_them_over": 0.12,
    }.get(approach, 0.0)

    heat = pop_score + contrast_bonus + type_excitement + approach_heat

    # Random crowd variance - some nights the crowd is just hot or dead
    crowd_variance = random.uniform(-0.10, 0.15)
    heat += crowd_variance

    return max(0.0, min(1.0, heat))


def calculate_approach_score(approach, match_type_data, wrestler):
    """Score how well the player's approach fits the match (0.0 - 1.0)."""
    flavor = match_type_data.get("narration_flavor", "technical")
    synergy_key = (approach, flavor)
    synergy = APPROACH_SYNERGY.get(synergy_key, 0.0)

    # Skill check - does the wrestler have the skills for their approach?
    skill_check = 0.0
    if approach == "go_all_out":
        skill_check = wrestler.get_effective_skill("athleticism") / 100.0
    elif approach == "play_it_safe":
        skill_check = wrestler.get_effective_skill("psychology") / 100.0
    elif approach == "work_stiff":
        skill_check = wrestler.get_effective_skill("violence") / 100.0
    elif approach == "cheat_to_win":
        skill_check = wrestler.get_effective_skill("psychology") / 100.0
    elif approach == "put_them_over":
        skill_check = wrestler.get_effective_skill("psychology") / 100.0

    return min(1.0, synergy + skill_check * 0.6)


def calculate_choice_quality(choices_made):
    """Score the in-ring decisions the player made (0.0 - 1.0).

    choices_made: list of dicts with keys 'quality_bonus', 'risk_taken', 'success'
    """
    if not choices_made:
        return 0.5  # Default middle score

    total_quality = 0.0
    for choice in choices_made:
        base = choice.get("quality_bonus", 0.0)
        if choice.get("success", True):
            total_quality += base
        else:
            # Botched choice still adds something, but less
            total_quality += base * 0.3

    avg_quality = total_quality / len(choices_made)
    return max(0.0, min(1.0, avg_quality))


def calculate_drama_score(near_falls, false_finishes, dramatic_moments):
    """Score the drama level of the match (0.0 - 1.0)."""
    # Near falls add drama but diminish with too many
    near_fall_score = min(near_falls * 0.12, 0.50)

    # False finishes are high drama
    false_finish_score = min(false_finishes * 0.18, 0.40)

    # Other dramatic moments (comebacks, ref bumps, etc.)
    drama_moment_score = min(dramatic_moments * 0.08, 0.30)

    return min(1.0, near_fall_score + false_finish_score + drama_moment_score)


def calculate_match_rating(
    wrestler1,
    wrestler2,
    match_type_data,
    approach,
    choices_made,
    near_falls=0,
    false_finishes=0,
    dramatic_moments=0,
    injuries_during_match=0,
    botches=0,
    blading_occurred=False,
):
    """Calculate the final star rating for a match.

    Returns a dict with the rating and breakdown of contributing factors.
    """
    # Calculate each component
    skill_score = calculate_wrestler_skill_score(wrestler1, wrestler2)
    psychology_score = (
        wrestler1.get_effective_skill("psychology")
        + wrestler2.get_effective_skill("psychology")
    ) / 200.0
    crowd_heat = calculate_crowd_heat(wrestler1, wrestler2, match_type_data, approach)
    match_type_bonus = match_type_data.get("rating_bonus", 0.0)
    approach_score = calculate_approach_score(approach, match_type_data, wrestler1)
    choice_score = calculate_choice_quality(choices_made)
    drama_score = calculate_drama_score(near_falls, false_finishes, dramatic_moments)

    # Weighted combination
    raw_rating = (
        skill_score * RATING_WEIGHTS["wrestler_skill"]
        + psychology_score * RATING_WEIGHTS["psychology"]
        + crowd_heat * RATING_WEIGHTS["crowd_heat"]
        + match_type_bonus * RATING_WEIGHTS["match_type_bonus"]
        + approach_score * RATING_WEIGHTS["approach_bonus"]
        + choice_score * RATING_WEIGHTS["choice_quality"]
        + drama_score * RATING_WEIGHTS["drama"]
    )

    # Scale to 0-5 range
    star_rating = raw_rating * 5.0

    # Botch penalties
    botch_penalty = botches * 0.25
    star_rating -= botch_penalty

    # Injury during match can add drama OR subtract quality
    if injuries_during_match > 0:
        # Serious injuries hurt the rating slightly but add spectacle
        star_rating -= injuries_during_match * 0.1
        star_rating += min(injuries_during_match * 0.05, 0.15)  # Slight drama bonus

    # Blading in appropriate match types adds to the spectacle
    if blading_occurred:
        if match_type_data.get("allow_blade", False):
            star_rating += 0.10  # Blood in a blood match adds drama
        else:
            star_rating -= 0.05  # Blood in a standard match is a negative

    # Match type rating bonus is additive on top
    star_rating += match_type_bonus

    # Random variance for the "intangibles"
    star_rating += random.uniform(-0.15, 0.20)

    # Clamp to valid range, but allow exceeding 5.0 for legendary matches
    max_possible = MATCH_RATING_MAX + MATCH_RATING_MELTZER_BONUS
    star_rating = max(MATCH_RATING_MIN, min(max_possible, star_rating))

    # Round to nearest quarter star
    star_rating = round(star_rating * 4) / 4

    breakdown = {
        "skill_contribution": skill_score,
        "psychology_contribution": psychology_score,
        "crowd_heat": crowd_heat,
        "match_type_bonus": match_type_bonus,
        "approach_score": approach_score,
        "choice_quality": choice_score,
        "drama_score": drama_score,
        "botch_penalty": botch_penalty,
        "final_rating": star_rating,
    }

    return star_rating, breakdown


def get_rating_description(star_rating):
    """Return a text description for a star rating."""
    if star_rating >= 5.0:
        return "MATCH OF THE YEAR CANDIDATE. This will be talked about for decades."
    elif star_rating >= 4.5:
        return "An instant classic. The crowd will never forget this one."
    elif star_rating >= 4.0:
        return "An outstanding match. Everything clicked tonight."
    elif star_rating >= 3.5:
        return "A great match. The crowd went home happy."
    elif star_rating >= 3.0:
        return "A solid, good match. Nothing to complain about."
    elif star_rating >= 2.5:
        return "An average match. Did the job, nothing more."
    elif star_rating >= 2.0:
        return "Below average. The crowd started checking their phones."
    elif star_rating >= 1.5:
        return "A bad match. Awkward spots and dead crowd."
    elif star_rating >= 1.0:
        return "Terrible. Botch-filled and embarrassing."
    elif star_rating >= 0.5:
        return "A disaster. This will live in infamy."
    else:
        return "Negative stars territory. What did we just witness?"


def get_xp_from_rating(star_rating):
    """Calculate XP gains based on match quality."""
    base_xp = 5
    rating_bonus = int(star_rating * 8)
    return {
        "in_ring": base_xp + rating_bonus,
        "psychology": base_xp + int(star_rating * 5),
        "durability": base_xp + 2,
        "athleticism": base_xp + int(star_rating * 3),
    }


def get_popularity_change(star_rating, wrestler_popularity, is_winner):
    """Calculate popularity change from match result."""
    if star_rating >= 4.5:
        base_change = random.randint(3, 6)
    elif star_rating >= 3.5:
        base_change = random.randint(2, 4)
    elif star_rating >= 2.5:
        base_change = random.randint(0, 2)
    elif star_rating >= 1.5:
        base_change = random.randint(-1, 1)
    else:
        base_change = random.randint(-3, -1)

    # Winners get a boost
    if is_winner:
        base_change += random.randint(1, 2)
    else:
        # Losing a great match can still help
        if star_rating >= 3.5:
            base_change += 1

    # Diminishing returns at high popularity
    if wrestler_popularity > 80:
        base_change = max(base_change - 1, 0)

    # Easier to gain when low
    if wrestler_popularity < 20:
        base_change += 1

    return base_change
