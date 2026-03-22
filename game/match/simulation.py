"""Interactive match simulation engine.

Runs a match as a sequence of phases with player choices at key moments.
Returns a result dict consumed by engine.apply_match_results.
"""

import random
from game.display import (
    clear_screen, print_subheader, print_menu, print_match_moment,
    print_dramatic, print_crowd_reaction, print_match_rating,
    print_injury_report, colored, Colors, bold, dim, press_enter,
    print_divider,
)
from game.match.ratings import (
    calculate_match_rating, get_rating_description, did_botch,
    get_popularity_change, get_xp_from_rating,
)
from game.match.moves import (
    FINISHERS_BY_STYLE, SIGNATURES_BY_STYLE, STANDARD_MOVES,
    WEAPON_MOVES, WEAPONS_BY_VIOLENCE, CROWD_SPOTS, COUNTERS,
    NEAR_FALLS, PACING,
)
from game.match.match_types import MATCH_TYPES


def run_match(player, opponent, match_type_id, booked_to_win, state):
    """Run a full interactive match.

    Parameters
    ----------
    player : Wrestler
    opponent : Wrestler
    match_type_id : str
    booked_to_win : bool
    state : GameState

    Returns
    -------
    dict  Match result for engine.apply_match_results
    """
    match_type = MATCH_TYPES.get(match_type_id, MATCH_TYPES["standard_singles"])

    print()
    print(f"  {bold(match_type['name'].upper())}")
    print(f"  {colored(player.ring_name, Colors.FACE if player.alignment > 0 else Colors.HEEL)}")
    print(f"    vs.")
    print(f"  {colored(opponent.ring_name, Colors.HEEL if player.alignment > 0 else Colors.FACE)}")
    print()

    # Track match state
    match_state = {
        "momentum": 0,  # positive = player advantage
        "near_falls": 0,
        "false_finishes": 0,
        "dramatic_moments": 0,
        "botches": 0,
        "injuries_during": 0,
        "choices_made": [],
        "crowd_heat": 0,
        "blood": False,
        "approach": None,
    }

    # Phase 1: Pre-match approach
    approach = choose_approach(player, match_type)
    match_state["approach"] = approach

    # Phase 2: Early match
    run_phase(player, opponent, match_type, match_state, "early", approach)

    # Phase 3: Mid match (1-2 key moments)
    run_phase(player, opponent, match_type, match_state, "mid", approach)
    if random.random() < 0.6:
        run_phase(player, opponent, match_type, match_state, "mid2", approach)

    # Phase 4: Finish sequence
    run_phase(player, opponent, match_type, match_state, "finish", approach)

    # Determine winner
    if booked_to_win:
        winner = "player"
    else:
        # Even if booked to lose, player choices can change outcome slightly
        override_chance = match_state["momentum"] * 0.03
        if random.random() < override_chance:
            winner = "player"
            match_state["dramatic_moments"] += 1
        else:
            winner = "opponent"

    # Run finish narration
    narrate_finish(player, opponent, winner, match_type, match_state, approach)

    # Calculate rating
    rating, breakdown = calculate_match_rating(
        player, opponent, match_type, approach,
        match_state["choices_made"],
        near_falls=match_state["near_falls"],
        false_finishes=match_state["false_finishes"],
        dramatic_moments=match_state["dramatic_moments"],
        injuries_during_match=match_state["injuries_during"],
        botches=match_state["botches"],
        blading_occurred=match_state["blood"],
    )

    # Display result
    print_divider()
    if winner == "player":
        print(f"\n  {colored('WINNER: ' + player.ring_name + '!', Colors.GOLD)}")
    else:
        print(f"\n  {colored('WINNER: ' + opponent.ring_name, Colors.RED)}")

    print_match_rating(rating)
    desc = get_rating_description(rating)
    print(f"  {dim(desc)}")

    # Post-match choice
    post_match_choice = post_match(player, opponent, winner, match_type, match_state)

    # Calculate stat changes
    pop_change = get_popularity_change(rating, player.popularity, winner == "player")
    alignment_change = 0
    rep_change = 0

    if approach == "cheat_to_win":
        alignment_change -= 10
    elif approach == "put_them_over":
        alignment_change += 5
        rep_change += 5

    if post_match_choice == "attack":
        alignment_change -= 15
        match_state["dramatic_moments"] += 1
    elif post_match_choice == "respect":
        alignment_change += 5
        rep_change += 3
    elif post_match_choice == "celebrate":
        pop_change += 1

    # Check for injury
    from game.systems.injury import roll_for_injury, apply_injury
    injury = roll_for_injury(player, match_type_id, approach)
    if injury:
        apply_injury(player, injury)
        match_state["injuries_during"] += 1

    # XP gains
    xp_gains = get_xp_from_rating(rating)
    for skill, xp in xp_gains.items():
        player.add_skill_xp(skill, xp)

    press_enter()

    return {
        "winner": winner,
        "rating": rating,
        "match_type": match_type_id,
        "popularity_change": pop_change,
        "alignment_change": alignment_change,
        "rep_change": rep_change,
        "had_promo": False,
        "breakdown": breakdown,
    }


def choose_approach(player, match_type):
    """Let the player choose their match approach."""
    print_subheader("MATCH APPROACH")
    print("  How do you want to work this match?")

    options = [
        ("Go All Out", "Leave it all in the ring. High risk, high reward."),
        ("Play It Safe", "Protect yourself. Solid fundamentals, fewer big spots."),
        ("Work Stiff", "Hit hard. Make it look real. Your opponent will feel it."),
        ("Cheat To Win", "Use every dirty trick in the book. Win at all costs."),
        ("Put Them Over", "Make your opponent look like a million bucks."),
    ]

    # Filter based on match type
    if match_type.get("violence_requirement", 0) >= 7:
        # Violent matches don't really have a 'safe' option
        pass  # keep all options

    choice = print_menu(options, "Approach")
    approaches = ["go_all_out", "play_it_safe", "work_stiff", "cheat_to_win", "put_them_over"]
    approach = approaches[choice]

    flavor = {
        "go_all_out": "You're going to give them everything you've got tonight.",
        "play_it_safe": "Smart. Live to fight another day.",
        "work_stiff": "They're going to feel every shot. This is going to hurt.",
        "cheat_to_win": "Whatever it takes. The ref can't catch everything.",
        "put_them_over": "You're going to make them look like a star tonight.",
    }
    print(f"\n  {dim(flavor[approach])}")
    print()

    return approach


def run_phase(player, opponent, match_type, match_state, phase, approach):
    """Run a single match phase with a player choice."""
    # Narrate the phase opening
    if phase == "early":
        pacing_pool = PACING.get("feeling_out", ["The match begins."])
        print(f"\n  {random.choice(pacing_pool)}")
    elif phase == "mid":
        pacing_pool = PACING.get("building", ["The action intensifies."])
        print(f"\n  {random.choice(pacing_pool)}")
    elif phase == "mid2":
        pacing_pool = PACING.get("heat_segment", ["The punishment continues."])
        print(f"\n  {random.choice(pacing_pool)}")
    elif phase == "finish":
        pacing_pool = PACING.get("finishing_stretch", ["This is it!"])
        print(f"\n  {random.choice(pacing_pool)}")

    # Generate choices based on phase and approach
    choices = generate_phase_choices(player, opponent, match_type, match_state, phase, approach)

    if not choices:
        return

    options = [(c["name"], c["description"]) for c in choices]
    choice_idx = print_menu(options, "What do you do?")
    chosen = choices[choice_idx]

    # Resolve the choice
    resolve_choice(player, opponent, match_type, match_state, chosen, phase)


def generate_phase_choices(player, opponent, match_type, match_state, phase, approach):
    """Generate contextual choices for a match phase."""
    choices = []
    style = player.style_id or "hybrid"

    if phase == "early":
        choices.append({
            "name": "Wrestling clinic",
            "description": "Lock up and work holds. Show your technical ability.",
            "skill_check": "in_ring",
            "quality_bonus": 0.5,
            "risk": 0.1,
            "momentum_bonus": 1,
        })
        choices.append({
            "name": "Aggressive start",
            "description": "Attack before the bell. Set the tone early.",
            "skill_check": "violence",
            "quality_bonus": 0.4,
            "risk": 0.15,
            "momentum_bonus": 2,
            "alignment_shift": -3,
        })
        choices.append({
            "name": "Feel them out",
            "description": "Take your time. Read your opponent.",
            "skill_check": "psychology",
            "quality_bonus": 0.6,
            "risk": 0.05,
            "momentum_bonus": 0,
        })

    elif phase in ("mid", "mid2"):
        # Signature move
        sigs = SIGNATURES_BY_STYLE.get(style, SIGNATURES_BY_STYLE.get("hybrid", []))
        if sigs:
            sig = random.choice(sigs)
            choices.append({
                "name": f"Hit the {sig[0]}",
                "description": f"Go for your signature move.",
                "skill_check": "in_ring",
                "quality_bonus": 0.6,
                "risk": sig[4],
                "momentum_bonus": 2,
            })

        choices.append({
            "name": "Work a body part",
            "description": "Target a specific area to set up your finisher.",
            "skill_check": "psychology",
            "quality_bonus": 0.7,
            "risk": 0.05,
            "momentum_bonus": 1,
        })

        # Weapon spot if allowed
        if match_type.get("allow_weapons") or match_type.get("no_dq"):
            violence_req = match_type.get("violence_requirement", 0)
            available_weapons = []
            for threshold in sorted(WEAPONS_BY_VIOLENCE.keys()):
                if threshold <= violence_req:
                    available_weapons = WEAPONS_BY_VIOLENCE[threshold]
            if available_weapons:
                weapon = random.choice(available_weapons)
                weapon_moves = WEAPON_MOVES.get(weapon, [])
                if weapon_moves:
                    wm = random.choice(weapon_moves)
                    choices.append({
                        "name": f"Grab the {weapon.replace('_', ' ')}",
                        "description": f"Use a {weapon.replace('_', ' ')} - {wm[0]}.",
                        "skill_check": "violence",
                        "quality_bonus": 0.5,
                        "risk": wm[4],
                        "momentum_bonus": 3,
                        "alignment_shift": -5,
                        "is_weapon": True,
                    })

        # Dive to the outside
        choices.append({
            "name": "High-risk dive",
            "description": "Launch yourself to the outside. The crowd will go wild.",
            "skill_check": "athleticism",
            "quality_bonus": 0.7,
            "risk": 0.25,
            "momentum_bonus": 3,
            "is_high_risk": True,
        })

        # Taunt
        choices.append({
            "name": "Taunt the crowd",
            "description": "Work the audience. Build the atmosphere.",
            "skill_check": "charisma",
            "quality_bonus": 0.4,
            "risk": 0.0,
            "momentum_bonus": 1,
        })

    elif phase == "finish":
        # Finisher attempt
        finishers = FINISHERS_BY_STYLE.get(style, FINISHERS_BY_STYLE.get("hybrid", []))
        if finishers:
            fin = random.choice(finishers)
            choices.append({
                "name": f"Go for the {player.finisher_name or fin[0]}",
                "description": "Hit your finisher! End this!",
                "skill_check": "in_ring",
                "quality_bonus": 0.8,
                "risk": fin[4],
                "momentum_bonus": 4,
                "is_finisher": True,
            })

        choices.append({
            "name": "Dramatic near-fall sequence",
            "description": "Trade big moves. Kickouts. Build the drama.",
            "skill_check": "psychology",
            "quality_bonus": 0.9,
            "risk": 0.15,
            "momentum_bonus": 2,
            "is_drama": True,
        })

        choices.append({
            "name": "Desperate last stand",
            "description": "Dig deep. Fighting spirit. Leave it all out there.",
            "skill_check": "durability",
            "quality_bonus": 0.6,
            "risk": 0.2,
            "momentum_bonus": 3,
        })

        if match_type.get("allow_blade"):
            choices.append({
                "name": "Blade (cut yourself)",
                "description": "Crimson mask. Blood sells. The old school way.",
                "skill_check": "violence",
                "quality_bonus": 0.5,
                "risk": 0.1,
                "momentum_bonus": 2,
                "is_blade": True,
                "alignment_shift": -3,
            })

    return choices


def resolve_choice(player, opponent, match_type, match_state, choice, phase):
    """Resolve a player's in-match choice."""
    skill_name = choice.get("skill_check", "in_ring")
    skill_value = player.get_effective_skill(skill_name)

    # Skill check with randomness
    roll = random.randint(1, 100)
    success = roll <= (skill_value + 20)  # Generous threshold

    # Check for botch
    is_high_risk = choice.get("is_high_risk", False)
    is_fatigued = phase == "finish"
    botched = did_botch(player, is_high_risk=is_high_risk, is_fatigued=is_fatigued)

    if botched:
        success = False
        match_state["botches"] += 1

    # Record choice
    match_state["choices_made"].append({
        "quality_bonus": choice.get("quality_bonus", 0.5),
        "risk_taken": choice.get("risk", 0.0),
        "success": success and not botched,
    })

    # Narrate outcome
    if success and not botched:
        narrate_success(player, opponent, choice, phase)
        match_state["momentum"] += choice.get("momentum_bonus", 1)

        if choice.get("is_drama"):
            match_state["near_falls"] += random.randint(1, 3)
            match_state["dramatic_moments"] += 1
            # Show near fall text
            print(f"    {colored(random.choice(NEAR_FALLS), Colors.GOLD)}")

        if choice.get("is_finisher"):
            match_state["false_finishes"] += 1
            match_state["dramatic_moments"] += 1

        if choice.get("is_blade"):
            match_state["blood"] = True
            print(f"    {colored('Blood streams down your face. The crowd erupts.', Colors.BLOOD)}")

        if choice.get("is_weapon"):
            match_state["dramatic_moments"] += 1
    else:
        narrate_failure(player, opponent, choice, phase, botched)
        match_state["momentum"] -= 1

        if botched:
            print(f"    {colored('BOTCH! The crowd groans.', Colors.RED)}")

    # Alignment shift
    if choice.get("alignment_shift"):
        match_state.setdefault("total_alignment_shift", 0)
        match_state["total_alignment_shift"] = match_state.get("total_alignment_shift", 0) + choice["alignment_shift"]


def narrate_success(player, opponent, choice, phase):
    """Print success narration for a choice."""
    name = choice["name"]
    print(f"\n  {colored('>>>', Colors.GREEN)} {bold(name)}")

    flavor_texts = {
        "Wrestling clinic": f"  {player.ring_name} takes control with crisp chain wrestling. {opponent.ring_name} can't find an answer.",
        "Aggressive start": f"  {player.ring_name} attacks before the bell! {opponent.ring_name} is caught off guard!",
        "Feel them out": f"  {player.ring_name} reads {opponent.ring_name} perfectly, anticipating every move.",
        "Work a body part": f"  {player.ring_name} zeroes in, targeting the weakened body part relentlessly.",
        "High-risk dive": f"  {player.ring_name} LAUNCHES to the outside! A spectacular dive connects!",
        "Taunt the crowd": f"  {player.ring_name} plays to the crowd. The arena is electric!",
        "Dramatic near-fall sequence": f"  WHAT A SEQUENCE! Back and forth! Neither wrestler will stay down!",
        "Desperate last stand": f"  {player.ring_name} digs deep! Where is this energy coming from?!",
    }

    text = flavor_texts.get(name, f"  {player.ring_name} connects! {choice.get('description', '')}")
    print(text)

    # Crowd reaction
    if choice.get("momentum_bonus", 0) >= 3:
        if player.alignment > 0:
            print_crowd_reaction("pop", 2)
        else:
            print_crowd_reaction("heat", 2)


def narrate_failure(player, opponent, choice, phase, botched):
    """Print failure narration."""
    name = choice["name"]
    print(f"\n  {colored('<<<', Colors.RED)} {bold(name)}")

    if botched:
        botch_texts = [
            f"  {player.ring_name} goes for it but slips! An ugly botch!",
            f"  Miscommunication! {player.ring_name} and {opponent.ring_name} collide awkwardly.",
            f"  {player.ring_name} mistimes the move completely. The crowd goes quiet.",
        ]
        print(random.choice(botch_texts))
    else:
        counter_text = random.choice(COUNTERS)
        print(f"  {opponent.ring_name} {counter_text}!")
        if choice.get("momentum_bonus", 0) >= 3:
            print_crowd_reaction("gasp", 1)


def narrate_finish(player, opponent, winner, match_type, match_state, approach):
    """Narrate the match finish."""
    print_divider()

    if winner == "player":
        if approach == "cheat_to_win":
            finishes = [
                f"  {player.ring_name} hooks the tights! The ref doesn't see it! ONE! TWO! THREE!",
                f"  {player.ring_name} grabs a handful of trunks! That's a stolen victory!",
                f"  Low blow while the ref is distracted! {player.ring_name} covers! ONE! TWO! THREE!",
                f"  Feet on the ropes for leverage! The ref counts! ONE! TWO! THREE!",
            ]
            print_match_moment(random.choice(finishes), delay=0.02)
        else:
            finishes = [
                f"  {player.ring_name} hits the {player.finisher_name or 'finisher'}! Covers! ONE! TWO! THREE!",
                f"  THERE IT IS! The {player.finisher_name or 'finisher'}! It's over! ONE! TWO! THREE!",
                f"  {player.ring_name} with the cover! ONE! TWO! THREE! It's over!",
            ]
            print_match_moment(random.choice(finishes), delay=0.02)

        if player.alignment > 0:
            print_crowd_reaction("pop", 3)
        else:
            print_crowd_reaction("heat", 3)
    else:
        losses = [
            f"  {opponent.ring_name} catches {player.ring_name} with a devastating finisher! ONE! TWO! THREE!",
            f"  {player.ring_name} walks into a counter! {opponent.ring_name} covers! ONE! TWO! THREE!",
            f"  After a grueling battle, {opponent.ring_name} hits the finishing blow! ONE! TWO! THREE!",
        ]
        print_match_moment(random.choice(losses), delay=0.02)

        if opponent.alignment > 0:
            print_crowd_reaction("pop", 2)
        else:
            print_crowd_reaction("heat", 2)


def post_match(player, opponent, winner, match_type, match_state):
    """Post-match player choice."""
    print()
    print("  The bell has rung. What do you do?")

    options = [
        ("Leave the ring", "Just walk away. The match is done."),
        ("Celebrate / Sell the loss", "Play to the crowd."),
    ]

    if winner == "player":
        options.append(("Show respect to opponent", "Shake hands. Good match."))
        options.append(("Attack your opponent", "The match is over, but you're not done."))
    else:
        options.append(("Show respect to opponent", "Acknowledge a hard-fought loss."))
        options.append(("Attack the winner", "You lost, but you won't accept it."))

    choice = print_menu(options, "Post-match")

    if choice == 0:
        print(f"\n  {dim('You roll out of the ring and head to the back.')}")
        return "leave"
    elif choice == 1:
        if winner == "player":
            print(f"\n  {player.ring_name} celebrates in the ring!")
            print_crowd_reaction("pop" if player.alignment > 0 else "heat", 2)
        else:
            print(f"\n  {player.ring_name} sells the defeat, lying in the ring.")
        return "celebrate"
    elif choice == 2:
        print(f"\n  You extend your hand to {opponent.ring_name}.")
        if random.random() < 0.8:
            print(f"  {opponent.ring_name} shakes your hand. A show of respect.")
            print_crowd_reaction("pop", 1)
        else:
            print(f"  {opponent.ring_name} slaps your hand away! No respect given!")
            print_crowd_reaction("heat", 1)
        return "respect"
    elif choice == 3:
        print(f"\n  {colored('You blindside ' + opponent.ring_name + ' from behind!', Colors.BLOOD)}")
        attacks = [
            f"  A vicious chair shot to the skull!",
            f"  You stomp {opponent.ring_name} into the mat!",
            f"  You lock in a submission and won't let go! The refs are trying to pull you off!",
        ]
        print(random.choice(attacks))
        print_crowd_reaction("heat", 3)
        return "attack"

    return "leave"


def get_available_match_types(violence_tolerance, player_violence):
    """Return match type IDs available given promotion violence tolerance."""
    available = ["standard_singles"]  # Always available

    for mt_id, mt in MATCH_TYPES.items():
        if mt_id == "standard_singles":
            continue
        # Skip multi-person matches (need more logic)
        if mt.get("min_participants", 2) > 2:
            continue
        if mt.get("violence_requirement", 0) <= violence_tolerance:
            available.append(mt_id)

    return available
