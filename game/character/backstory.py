"""Backstory and wrestling style definitions."""


BACKSTORIES = {
    "backyard": {
        "name": "Backyard Legend",
        "description": (
            "You grew up in a small town with nothing to do but fight. You and your buddies "
            "built a ring out of plywood and mattresses in someone's backyard. You've been "
            "thrown through tables, hit with chairs, and wrapped in barbed wire -- all before "
            "you turned 18. You're tough as nails but rough around the edges."
        ),
        "starting_age": 18,
        "skill_bonuses": {"violence": 20, "durability": 15, "in_ring": -5},
        "starting_promotions": ["backyard", "czw"],
        "starting_money": 200,
        "traits": ["scarred", "underground_rep"],
    },
    "amateur": {
        "name": "Amateur Wrestling Champion",
        "description": (
            "Four years of college wrestling. State champion twice. You could have gone to "
            "the Olympics, but the money wasn't there. Pro wrestling pays better -- if you "
            "can make it. You've got the fundamentals down cold, but you've never cut a "
            "promo or worked a crowd in your life."
        ),
        "starting_age": 22,
        "skill_bonuses": {"in_ring": 25, "psychology": 10, "athleticism": 10, "mic_work": -10},
        "starting_promotions": ["roh", "nxt", "pwg"],
        "starting_money": 800,
        "traits": ["clean_cut", "respected_amateur"],
    },
    "football": {
        "name": "Football Washout",
        "description": (
            "You were a beast on the field. D1 prospect, NFL scouts watching. Then you blew "
            "out your knee junior year. Surgery got you back to 90%, but 90% doesn't cut it "
            "in the NFL. A promoter at a local show saw your build and said, 'You ever think "
            "about wrestling?' You hadn't. But here you are."
        ),
        "starting_age": 24,
        "skill_bonuses": {"power": 20, "athleticism": 15, "look": 10, "in_ring": -15, "psychology": -10},
        "starting_promotions": ["nxt", "tna"],
        "starting_money": 1500,
        "traits": ["big_body", "sports_background", "bad_knee"],
    },
    "second_gen": {
        "name": "Second Generation",
        "description": (
            "Your father was a legend. Your mother hates that you're following in his "
            "footsteps -- she saw what this business did to him. The pills, the pain, the "
            "time away from home. But wrestling is in your blood. Everyone knows your name "
            "before you've even had a match. The expectations are crushing."
        ),
        "starting_age": 20,
        "skill_bonuses": {"psychology": 15, "charisma": 10, "in_ring": 10},
        "starting_promotions": ["roh", "pwg", "nxt"],
        "starting_money": 2000,
        "traits": ["famous_parent", "high_expectations"],
    },
    "street_fighter": {
        "name": "Street Fighter",
        "description": (
            "You grew up fighting. Not for fun -- for survival. Group homes, foster care, "
            "the streets. You've broken bones -- yours and other people's. A local promoter "
            "saw you in a bar fight and said you had 'it.' You don't know what 'it' is, "
            "but you know how to hurt people. Maybe you can get paid for it legally now."
        ),
        "starting_age": 19,
        "skill_bonuses": {"violence": 25, "power": 10, "durability": 10, "charisma": -5, "look": -10},
        "starting_promotions": ["backyard", "czw", "ecw"],
        "starting_money": 100,
        "traits": ["criminal_record", "street_tough", "intimidating"],
    },
    "theater_kid": {
        "name": "Theater Kid",
        "description": (
            "You were the lead in every school play. You can make a room full of strangers "
            "laugh, cry, or boo you out of the building. You watched wrestling and thought, "
            "'I can do THAT.' The talking, the characters, the drama. You signed up for "
            "wrestling school the day after you graduated. You can talk circles around "
            "anyone. You just can't wrestle worth a damn. Yet."
        ),
        "starting_age": 21,
        "skill_bonuses": {"mic_work": 25, "charisma": 20, "psychology": 5, "in_ring": -15, "power": -10, "durability": -5},
        "starting_promotions": ["pwg", "roh"],
        "starting_money": 600,
        "traits": ["natural_talker", "entertainer"],
    },
    "dojo": {
        "name": "Japanese Dojo Graduate",
        "description": (
            "Two years of hell. Up at 5 AM. Train until you puke. Clean the dojo. "
            "Train more. Sleep on the floor. The Japanese dojo system broke you down "
            "and rebuilt you into a wrestling machine. You can work stiff, sell like "
            "death, and your fundamentals are flawless. But you're quiet, disciplined, "
            "and you've never had to talk on a microphone in English."
        ),
        "starting_age": 23,
        "skill_bonuses": {"in_ring": 20, "durability": 15, "psychology": 15, "mic_work": -15, "charisma": -5},
        "starting_promotions": ["njpw", "ajpw"],
        "starting_money": 500,
        "traits": ["disciplined", "stiff_worker", "japanese_trained"],
    },
    "bodybuilder": {
        "name": "Bodybuilder",
        "description": (
            "You've got the look. 240 pounds of chiseled muscle. Veins popping. Jaw like "
            "a superhero. You've been on the gas since you were 19 -- everyone in the gym "
            "is. WWE scouts spotted you at a bodybuilding show and asked if you'd ever "
            "considered wrestling. The answer is you'll consider anything that gets you "
            "on TV. You just need to learn how to, you know, actually wrestle."
        ),
        "starting_age": 26,
        "skill_bonuses": {"look": 30, "power": 15, "in_ring": -20, "psychology": -15, "mic_work": -5},
        "starting_promotions": ["nxt"],
        "starting_money": 3000,
        "traits": ["the_look", "steroid_history", "green"],
    },
}


WRESTLING_STYLES = {
    "technical": {
        "name": "Technical",
        "description": "Chain wrestling, submissions, mat work. You tell stories through holds and counters.",
        "skill_bonuses": {"in_ring": 10, "psychology": 8},
        "match_bonuses": {"long_match_bonus": 0.3},
        "promotion_affinity": {"roh": 1.3, "njpw": 1.2, "nxt": 1.1},
    },
    "high_flyer": {
        "name": "High-Flyer",
        "description": "Moonsaults, dives, and death-defying spots. The crowd loves you, but your body pays the price.",
        "skill_bonuses": {"athleticism": 12, "charisma": 5},
        "match_bonuses": {"spot_bonus": 0.3, "injury_risk_mult": 1.3},
        "promotion_affinity": {"pwg": 1.3, "aew": 1.2, "njpw": 1.1},
    },
    "powerhouse": {
        "name": "Powerhouse",
        "description": "Slams, suplexes, and raw strength. You don't need 20 minutes to make an impact.",
        "skill_bonuses": {"power": 12, "look": 5},
        "match_bonuses": {"short_match_bonus": 0.3},
        "promotion_affinity": {"wwe": 1.3, "nxt": 1.2},
    },
    "brawler": {
        "name": "Brawler",
        "description": "Fists, chairs, and blood. You don't wrestle -- you fight. The dirtier, the better.",
        "skill_bonuses": {"violence": 12, "durability": 8},
        "match_bonuses": {"hardcore_bonus": 0.5},
        "promotion_affinity": {"czw": 1.5, "ecw": 1.4, "backyard": 1.3},
    },
    "showman": {
        "name": "Showman",
        "description": "The entrance, the promos, the character work. Your matches are just part of the show.",
        "skill_bonuses": {"charisma": 12, "mic_work": 8},
        "match_bonuses": {"promo_bonus": 0.3},
        "promotion_affinity": {"wwe": 1.4, "tna": 1.2, "aew": 1.1},
    },
    "strong_style": {
        "name": "Strong Style",
        "description": "Stiff strikes, brutal kicks, fighting spirit. It hurts. That's the point.",
        "skill_bonuses": {"in_ring": 8, "violence": 8, "durability": 5},
        "match_bonuses": {"stiff_bonus": 0.3},
        "promotion_affinity": {"njpw": 1.5, "ajpw": 1.4, "roh": 1.2},
    },
    "hybrid": {
        "name": "All-Rounder",
        "description": "A little bit of everything. Jack of all trades, master of none -- but often better than a master of one.",
        "skill_bonuses": {"in_ring": 5, "charisma": 4, "athleticism": 4, "psychology": 4},
        "match_bonuses": {"versatility_bonus": 0.2},
        "promotion_affinity": {"aew": 1.2, "nxt": 1.1, "roh": 1.1, "pwg": 1.1},
    },
}


def get_backstory(backstory_id):
    """Get a backstory definition."""
    return BACKSTORIES.get(backstory_id)


def get_style(style_id):
    """Get a wrestling style definition."""
    return WRESTLING_STYLES.get(style_id)


def get_starting_skills(backstory_id, style_id):
    """Calculate starting skills from backstory + style combo."""
    from data.constants import SKILL_DEFAULT, SKILLS, SKILL_MIN, SKILL_MAX

    skills = {s: SKILL_DEFAULT for s in SKILLS}

    backstory = BACKSTORIES.get(backstory_id, {})
    for skill, bonus in backstory.get("skill_bonuses", {}).items():
        skills[skill] = max(SKILL_MIN, min(SKILL_MAX, skills[skill] + bonus))

    style = WRESTLING_STYLES.get(style_id, {})
    for skill, bonus in style.get("skill_bonuses", {}).items():
        skills[skill] = max(SKILL_MIN, min(SKILL_MAX, skills[skill] + bonus))

    return skills
