"""Multi-week storyline arc system."""

import random
from game.display import (
    print_subheader, print_menu, colored, Colors, bold, dim, press_enter,
    print_dramatic, print_crowd_reaction,
)


def advance_storyline(state):
    """Advance the current storyline by one beat."""
    sl = state.active_storyline
    if not sl:
        return

    current_beat = sl.get("current_beat", 0)
    beats = sl.get("beats", [])

    if current_beat >= len(beats):
        # Storyline is over
        conclude_storyline(state)
        return

    beat = beats[current_beat]
    print_subheader(f"STORYLINE: {sl['name']}")
    print(f"  {bold(beat['title'])}")
    print(f"  {beat['description']}")

    if beat.get("choices"):
        options = [(c["text"], c.get("hint", "")) for c in beat["choices"]]
        choice_idx = print_menu(options, "What do you do?")
        chosen = beat["choices"][choice_idx]

        # Apply effects
        if chosen.get("alignment_change"):
            state.player.alignment += chosen["alignment_change"]
        if chosen.get("popularity_change"):
            state.player.popularity = max(0, min(100, state.player.popularity + chosen["popularity_change"]))
        if chosen.get("rep_change"):
            state.player.backstage_rep += chosen["rep_change"]
        if chosen.get("heat_boost"):
            sl["heat"] = sl.get("heat", 0) + chosen["heat_boost"]

        print(f"\n  {chosen.get('result_text', 'The angle plays out.')}")

        if chosen.get("crowd_reaction"):
            reaction, intensity = chosen["crowd_reaction"]
            print_crowd_reaction(reaction, intensity)

    sl["current_beat"] = current_beat + 1
    sl["weeks_elapsed"] = sl.get("weeks_elapsed", 0) + 1


def conclude_storyline(state):
    """Wrap up a storyline."""
    sl = state.active_storyline
    if not sl:
        return

    heat = sl.get("heat", 0)
    print_subheader("STORYLINE CONCLUDED")
    print(f"  {bold(sl['name'])} has come to an end.")
    print(f"  Total heat generated: {heat}")

    # Popularity boost based on heat
    pop_bonus = min(15, heat // 3)
    state.player.popularity = min(100, state.player.popularity + pop_bonus)
    print(f"  Popularity +{pop_bonus}")

    state.storyline_history.append({
        "name": sl["name"],
        "heat": heat,
        "weeks": sl.get("weeks_elapsed", 0),
    })
    state.active_storyline = {}
    state.log_career_event(f"Completed storyline: {sl['name']}")


def generate_storyline(state, opponent):
    """Generate a new storyline with the given opponent."""
    player = state.player
    templates = _get_storyline_templates(player, opponent)

    if not templates:
        return None

    template = random.choice(templates)
    storyline = {
        "name": template["name"].format(
            player=player.ring_name,
            opponent=opponent.ring_name,
        ),
        "type": template["type"],
        "opponent_id": opponent.npc_id,
        "beats": _generate_beats(template, player, opponent),
        "current_beat": 0,
        "weeks_elapsed": 0,
        "heat": 0,
        "blow_off_week": state.total_weeks + len(template.get("beat_templates", [])) * 4,
    }

    return storyline


def _get_storyline_templates(player, opponent):
    """Get available storyline templates based on context."""
    templates = [
        {
            "name": "{player} vs. {opponent}: The Rivalry",
            "type": "feud",
            "beat_templates": ["confrontation", "escalation", "personal", "blowoff_build"],
        },
        {
            "name": "The Rise of {player}",
            "type": "title_chase",
            "beat_templates": ["challenge", "proving_ground", "setback", "final_chance"],
        },
        {
            "name": "{player}: Betrayal",
            "type": "betrayal",
            "beat_templates": ["tension", "incident", "confrontation", "split"],
        },
    ]
    return templates


def _generate_beats(template, player, opponent):
    """Generate story beats from a template."""
    beat_generators = {
        "confrontation": {
            "title": "Face to Face",
            "description": f"{player.ring_name} and {opponent.ring_name} come face to face in the ring.",
            "choices": [
                {
                    "text": "Cut a fiery promo",
                    "hint": "Get the crowd invested",
                    "alignment_change": 0,
                    "popularity_change": 3,
                    "heat_boost": 5,
                    "result_text": "The crowd is buzzing. This feud is real.",
                    "crowd_reaction": ("pop", 2),
                },
                {
                    "text": "Attack them",
                    "hint": "Let your fists do the talking",
                    "alignment_change": -10,
                    "popularity_change": 2,
                    "heat_boost": 8,
                    "result_text": "You blindside them! The crowd erupts!",
                    "crowd_reaction": ("heat", 2),
                },
                {
                    "text": "Stay silent and stare",
                    "hint": "Let the tension build",
                    "alignment_change": 0,
                    "popularity_change": 1,
                    "heat_boost": 3,
                    "result_text": "The staredown says everything. No words needed.",
                },
            ],
        },
        "escalation": {
            "title": "Things Get Personal",
            "description": f"{opponent.ring_name} has crossed a line. This just got personal.",
            "choices": [
                {
                    "text": "Respond in kind",
                    "hint": "Match their intensity",
                    "alignment_change": -5,
                    "heat_boost": 7,
                    "result_text": "You give as good as you get. The feud intensifies.",
                    "crowd_reaction": ("heat", 2),
                },
                {
                    "text": "Take the high road",
                    "hint": "Don't sink to their level",
                    "alignment_change": 5,
                    "popularity_change": 3,
                    "heat_boost": 4,
                    "result_text": "You show restraint. The crowd respects it.",
                    "crowd_reaction": ("pop", 2),
                },
            ],
        },
        "personal": {
            "title": "The Breaking Point",
            "description": "Something snaps. This has gone beyond wrestling.",
            "choices": [
                {
                    "text": "Go nuclear",
                    "hint": "Destroy everything",
                    "alignment_change": -15,
                    "popularity_change": 5,
                    "heat_boost": 12,
                    "result_text": "You've gone too far. Or maybe not far enough.",
                    "crowd_reaction": ("heat", 3),
                },
                {
                    "text": "Channel the emotion into your promo",
                    "hint": "Use the anger to tell a story",
                    "alignment_change": 0,
                    "popularity_change": 5,
                    "heat_boost": 10,
                    "result_text": "That was one of the best promos of your career.",
                    "crowd_reaction": ("pop", 3),
                },
            ],
        },
        "blowoff_build": {
            "title": "Final Countdown",
            "description": "Next week: the blowoff match. Everything on the line.",
            "choices": [
                {
                    "text": "Promise to end them",
                    "hint": "Maximum intensity",
                    "heat_boost": 8,
                    "result_text": "The crowd is ready for the blowoff.",
                    "crowd_reaction": ("pop", 2),
                },
                {
                    "text": "Mind games",
                    "hint": "Get inside their head",
                    "heat_boost": 6,
                    "popularity_change": 2,
                    "result_text": "You've gotten under their skin. The advantage is yours.",
                },
            ],
        },
        "challenge": {
            "title": "The Challenge",
            "description": f"You look at the championship. You want it. {opponent.ring_name} has it.",
            "choices": [
                {
                    "text": "Formally challenge for the title",
                    "hint": "Make it official",
                    "popularity_change": 3,
                    "heat_boost": 5,
                    "result_text": "The challenge is made. The champion stares you down.",
                    "crowd_reaction": ("pop", 2),
                },
                {
                    "text": "Earn your shot",
                    "hint": "Prove you deserve it first",
                    "rep_change": 5,
                    "heat_boost": 3,
                    "result_text": "You'll earn your way. The hard way.",
                },
            ],
        },
        "proving_ground": {
            "title": "Proving Ground",
            "description": "You must beat a top contender to earn your title shot.",
            "choices": [
                {
                    "text": "Bring your A-game",
                    "heat_boost": 5,
                    "popularity_change": 2,
                    "result_text": "You prove yourself. The title shot is next.",
                    "crowd_reaction": ("pop", 2),
                },
                {
                    "text": "Take a shortcut",
                    "alignment_change": -10,
                    "heat_boost": 4,
                    "result_text": "You cheated your way through. But a win is a win.",
                    "crowd_reaction": ("heat", 2),
                },
            ],
        },
        "setback": {
            "title": "Setback",
            "description": "Things don't go your way. The champion makes you look foolish.",
            "choices": [
                {
                    "text": "Refuse to give up",
                    "heat_boost": 6,
                    "popularity_change": 3,
                    "alignment_change": 5,
                    "result_text": "You get knocked down. You get back up. The crowd loves it.",
                    "crowd_reaction": ("pop", 2),
                },
                {
                    "text": "Snap",
                    "alignment_change": -10,
                    "heat_boost": 8,
                    "result_text": "You lose control. Something dark has awoken.",
                    "crowd_reaction": ("gasp", 2),
                },
            ],
        },
        "final_chance": {
            "title": "One Last Shot",
            "description": "This is it. Your final chance at the championship.",
            "choices": [
                {
                    "text": "Stay focused",
                    "heat_boost": 7,
                    "popularity_change": 2,
                    "result_text": "Eyes on the prize. Everything you've worked for comes down to this.",
                    "crowd_reaction": ("chant", 2),
                },
                {
                    "text": "Put everything on the line",
                    "heat_boost": 10,
                    "popularity_change": 4,
                    "result_text": "Win or lose, you'll leave everything in that ring.",
                    "crowd_reaction": ("pop", 3),
                },
            ],
        },
        "tension": {
            "title": "Cracks Appear",
            "description": f"Something feels off with {opponent.ring_name}. They're distant.",
            "choices": [
                {
                    "text": "Confront them",
                    "heat_boost": 4,
                    "result_text": "'Everything's fine,' they say. But it's not.",
                },
                {
                    "text": "Let it slide",
                    "heat_boost": 2,
                    "result_text": "You ignore the warning signs.",
                },
            ],
        },
        "incident": {
            "title": "The Incident",
            "description": f"{opponent.ring_name} 'accidentally' costs you a match.",
            "choices": [
                {
                    "text": "Give them the benefit of the doubt",
                    "alignment_change": 5,
                    "heat_boost": 5,
                    "result_text": "You forgive. But you won't forget.",
                    "crowd_reaction": ("pop", 1),
                },
                {
                    "text": "Strike first",
                    "alignment_change": -15,
                    "heat_boost": 10,
                    "popularity_change": 5,
                    "result_text": "You strike before they can betray you!",
                    "crowd_reaction": ("gasp", 3),
                },
            ],
        },
        "split": {
            "title": "The Split",
            "description": "It's over. The partnership is dead.",
            "choices": [
                {
                    "text": "Burn it all down",
                    "alignment_change": -10,
                    "heat_boost": 12,
                    "popularity_change": 5,
                    "result_text": "The betrayal is complete. The crowd is in shock.",
                    "crowd_reaction": ("gasp", 3),
                },
                {
                    "text": "Walk away with dignity",
                    "alignment_change": 5,
                    "heat_boost": 6,
                    "popularity_change": 3,
                    "result_text": "You walk away. No looking back.",
                    "crowd_reaction": ("pop", 2),
                },
            ],
        },
    }

    beats = []
    for beat_name in template.get("beat_templates", []):
        beat = beat_generators.get(beat_name)
        if beat:
            beats.append(dict(beat))  # Copy to avoid mutation

    return beats
