"""Main game loop and turn management."""

import random
from game.state import GameState
from game.display import (
    clear_screen, print_header, print_subheader, print_menu, print_stats,
    print_week_header, print_divider, print_game_over, press_enter,
    colored, Colors, bold, dim, get_input, confirm, print_dramatic,
)
from game.character.creation import create_character
from game.save import save_game, autosave, present_save_menu, present_load_menu


def new_game():
    """Start a new game."""
    state = GameState()
    state.player = create_character()
    initialize_world(state)
    return state


def initialize_world(state):
    """Set up the game world - rosters, titles, calendar."""
    from game.world.npcs import generate_roster
    from game.world.promotions import PROMOTIONS
    from game.world.titles import TitleManager
    from game.world.calendar import Calendar

    # Generate rosters for all promotions
    for promo_id, promo in PROMOTIONS.items():
        if promo_id == "retirement":
            continue
        roster = generate_roster(promo)
        state.promotion_rosters[promo_id] = roster
        for npc in roster:
            state.register_npc(npc)

    # Initialize titles
    state.title_manager = TitleManager()
    state.title_manager.initialize_titles(PROMOTIONS, state.promotion_rosters)

    # Setup calendar
    state.calendar = Calendar()
    state.calendar.schedule_month([state.player.current_promotion])

    # Set initial contract
    promo_id = state.player.current_promotion
    promo = PROMOTIONS.get(promo_id)
    state.contract = {
        "promotion_id": promo_id,
        "weeks_remaining": 52,
        "pay_per_show": promo.pay_min if promo else 0,
        "exclusive": promo.tier >= 3 if promo else False,
    }

    promo_name = promo.name if promo else promo_id
    state.log_career_event(f"Signed first contract with {promo_name}")


def game_loop(state):
    """Main game loop - runs weekly turns until game over."""
    while not state.game_over:
        run_week(state)

    # Game over
    clear_screen()
    summary = state.get_career_summary()
    print_game_over(state.player, summary)
    press_enter()


def run_week(state):
    """Process a single game week."""
    from game.events.manager import process_weekly_events
    from game.systems.lifestyle import tick_addictions, check_lifestyle_events
    from game.systems.injury import process_injury_recovery

    player = state.player

    # Display weekly header
    clear_screen()
    from game.world.promotions import PROMOTIONS
    promo = PROMOTIONS.get(player.current_promotion)
    promo_name = promo.name if promo else player.current_promotion
    print_week_header(state.current_week, state.current_year, promo_name, player)

    # Check for injuries preventing action
    if player.is_injured():
        severe = [i for i in player.injuries if i.weeks_remaining > 0 and i.severity >= 3]
        moderate = [i for i in player.injuries if i.weeks_remaining > 0 and i.severity == 2]
        concussions = [i for i in player.injuries if i.weeks_remaining > 0 and "concussion" in i.description.lower()]
        if severe:
            # Check if it's ONLY a concussion at severity 3 - allow risky choice
            severe_concussions = [i for i in severe if "concussion" in i.description.lower()]
            non_conc_severe = [i for i in severe if "concussion" not in i.description.lower()]
            if severe_concussions and not non_conc_severe:
                _present_concussion_choice(state, severe_concussions)
            else:
                print(f"\n  {colored('You are currently injured and cannot wrestle.', Colors.INJURY)}")
                for inj in severe:
                    print(f"    - {inj.description}: {inj.weeks_remaining} weeks remaining")
        elif concussions:
            # Moderate concussions get a special prompt with CTE warning
            _present_concussion_choice(state, concussions)
        elif moderate:
            print(f"\n  {colored('You are hurt. These injuries are nagging:', Colors.WARNING)}")
            for inj in moderate:
                print(f"    - {inj.description}: {inj.weeks_remaining} weeks remaining")
            print()
            work_injured = confirm("Do you want to work through the pain?")
            if work_injured:
                print(f"  {dim('You pop some painkillers and tape up. The show must go on.')}")
                player.painkiller_level = min(100, player.painkiller_level + 5)
                player.backstage_rep += 3
                state._working_injured = True
            else:
                print(f"  {dim('Smart. You sit this one out and let your body heal.')}")
                player.health = min(100, player.health + 10)
                state._working_injured = False

    # Process storyline beats
    if state.active_storyline:
        from game.events.storylines import advance_storyline
        advance_storyline(state)
    elif state.total_weeks >= 8 and random.random() < 0.15:
        # No active storyline - chance to organically start a feud
        _try_generate_feud(state)

    # Random events
    process_weekly_events(state)

    # Check for lifestyle events
    check_lifestyle_events(state)

    # Show phase - match if booked
    ppv = _is_ppv_week(state)
    can_work = player.can_wrestle() or getattr(state, '_working_injured', False)
    if can_work:
        show_phase(state, is_ppv=ppv)
        # Working injured increases re-injury risk after the match
        if getattr(state, '_working_injured', False):
            from game.systems.injury import roll_for_injury, apply_injury
            if random.random() < 0.25:
                injury = roll_for_injury(player, "standard_singles", "go_all_out")
                if injury:
                    print(f"\n  {colored('Working through the pain made things worse!', Colors.INJURY)}")
                    apply_injury(player, injury)
            # Extra concussion risk when competing concussed
            if getattr(state, '_competing_concussed', False):
                if random.random() < 0.35:
                    from game.character.wrestler import Injury
                    sev = random.choices([2, 3, 4], weights=[3, 2, 1])[0]
                    names = {2: "Concussion (Second Impact)", 3: "Severe Concussion", 4: "Traumatic Brain Injury"}
                    weeks = {2: (3, 8), 3: (8, 16), 4: (16, 40)}
                    w = weeks[sev]
                    conc = Injury(
                        body_part="head", severity=sev,
                        description=names[sev],
                        weeks_remaining=random.randint(w[0], w[1]),
                        chronic=sev >= 3,
                        stat_penalties={"in_ring": sev * 3, "psychology": sev * 3, "charisma": sev * 2},
                    )
                    apply_injury(player, conc)
                    player.concussion_count += 1
                    player.cte_severity = min(100, player.cte_severity + sev * 8)
                    player.body_damage["head"] = min(100, player.body_damage["head"] + sev * 6)
                    print(f"\n  {colored('Competing with a concussion was a terrible idea. Another head injury.', Colors.RED)}")
                    if sev == 4:
                        print(f"  {colored('This could be career-ending.', Colors.RED)}")
                state._competing_concussed = False
            state._working_injured = False
    else:
        print(f"\n  {dim('No match this week - recovering from injury.')}")

    # Off-day phase
    off_day_phase(state)

    # Weekly maintenance
    player.heal_week()
    tick_addictions(player)
    process_injury_recovery(player)

    # Weekly business income
    from game.systems.business import process_weekly_business
    biz_income = process_weekly_business(player)
    if biz_income >= 200:
        print(f"\n  {colored(f'Business income this week: +${biz_income:,}', Colors.MONEY)}")

    # Decrement event cooldowns
    for event_id in list(state.event_cooldowns.keys()):
        state.event_cooldowns[event_id] -= 1
        if state.event_cooldowns[event_id] <= 0:
            del state.event_cooldowns[event_id]

    # Contract countdown
    if state.contract:
        state.contract["weeks_remaining"] -= 1
        if state.contract["weeks_remaining"] <= 0:
            _handle_contract_expiry(state)

    # Simulate NPC title defenses in the background
    if state.title_manager and state.current_week % 4 == 0:
        _simulate_npc_title_defenses(state)

    # Monthly checks (every 4 weeks)
    if state.current_week % 4 == 0:
        monthly_phase(state)

    # Yearly checks
    if state.current_week == 52:
        yearly_phase(state)

    # Advance calendar
    _advance_week(state)

    # Autosave at PPVs
    if ppv:
        autosave(state)

    # Check game over conditions
    check_game_over(state)

    # Weekly menu
    if not state.game_over:
        weekly_menu(state)


def show_phase(state, is_ppv=False):
    """Handle the show/match portion of the week."""
    from game.match.simulation import run_match
    from game.world.promotions import PROMOTIONS

    player = state.player
    roster = state.get_current_roster()

    if not roster:
        print(f"\n  {dim('No opponents available this week.')}")
        return

    # Determine opponent
    opponent = pick_opponent(state, roster, is_ppv)
    if not opponent:
        return

    promo = PROMOTIONS.get(player.current_promotion)
    promo_id = player.current_promotion

    # Check if this is a title match
    title_match_info = _check_title_match(state, opponent, is_ppv)

    # Determine match type
    from game.match.simulation import get_available_match_types
    violence_tolerance = promo.violence_tolerance if promo else 5
    available_types = get_available_match_types(
        violence_tolerance,
        player.get_effective_skill("violence"),
    )

    if is_ppv:
        print(f"\n  {colored('★ PAY-PER-VIEW EVENT ★', Colors.GOLD)}")
        # PPVs can have special match types
        if state.active_storyline and state.active_storyline.get("blow_off_week") == state.total_weeks:
            match_type_id = state.active_storyline.get("blow_off_match_type", "standard_singles")
        else:
            match_type_id = choose_match_type(available_types)
    else:
        # Regular show - usually standard unless storyline dictates
        if random.random() < 0.3:
            match_type_id = choose_match_type(available_types)
        else:
            match_type_id = "standard_singles"

    # Display title match banner
    if title_match_info:
        title_name = title_match_info["title_name"]
        print(f"\n  {colored(f'🏆 TITLE MATCH: {title_name} 🏆', Colors.GOLD)}")
        if title_match_info["player_is_champion"]:
            print(f"  {bold('Champion:')} {player.ring_name} vs. Challenger: {opponent.ring_name}")
        else:
            print(f"  Champion: {opponent.ring_name} vs. {bold('Challenger:')} {player.ring_name}")

    # Determine if player is booked to win
    booked_to_win = determine_booking(state, opponent)

    # Run the match
    header = 'PPV MAIN EVENT' if is_ppv else 'MATCH'
    if title_match_info:
        header += f" - {title_match_info['title_name']}"
    print_subheader(f"{header}: {player.ring_name} vs. {opponent.ring_name}")
    result = run_match(player, opponent, match_type_id, booked_to_win, state)

    # Apply results
    apply_match_results(state, result, opponent, is_ppv)

    # Resolve title match outcome
    if title_match_info and result:
        _resolve_title_result(state, result, opponent, title_match_info)


def pick_opponent(state, roster, is_ppv):
    """Pick an opponent from the roster."""
    # If in a storyline, face the feud partner
    if state.active_storyline and state.active_storyline.get("opponent_id"):
        opp = state.get_npc(state.active_storyline["opponent_id"])
        if opp:
            return opp

    # Filter to available opponents
    available = [w for w in roster if isinstance(w, object) and hasattr(w, 'can_wrestle') and w.can_wrestle()]
    if not available:
        return None

    if is_ppv:
        # PPV opponents tend to be higher ranked
        available.sort(key=lambda w: w.get_overall_rating(), reverse=True)
        return available[0] if available else None

    # Regular show - weighted random
    return random.choice(available)


def choose_match_type(available_types):
    """Let the player choose a match type (or pick automatically)."""
    from game.display import print_menu
    from game.match.match_types import MATCH_TYPES

    if len(available_types) <= 1:
        return available_types[0] if available_types else "standard_singles"

    # Show top 5 options
    options_to_show = available_types[:6]
    options = []
    for mt_id in options_to_show:
        mt = MATCH_TYPES.get(mt_id, {})
        options.append((mt.get("name", mt_id), mt.get("description", "")))

    choice = print_menu(options, "Match type")
    return options_to_show[choice]


def determine_booking(state, opponent):
    """Determine if the player is booked to win."""
    player = state.player
    momentum = player.momentum

    # Base win chance from momentum
    base_chance = 0.5 + (momentum * 0.05)

    # Popularity comparison
    if player.popularity > opponent.popularity + 20:
        base_chance += 0.15
    elif opponent.popularity > player.popularity + 20:
        base_chance -= 0.15

    # Backstage rep helps
    if player.backstage_rep > 30:
        base_chance += 0.1
    elif player.backstage_rep < -30:
        base_chance -= 0.1

    # Title holders usually retain
    if player.titles_held:
        base_chance += 0.2

    return random.random() < min(0.85, max(0.15, base_chance))


def apply_match_results(state, result, opponent, is_ppv):
    """Apply match results to game state."""
    player = state.player

    if result is None:
        return

    # Record
    if result.get("winner") == "player":
        player.wins += 1
        if isinstance(opponent, object) and hasattr(opponent, 'losses'):
            opponent.losses += 1
    elif result.get("winner") == "opponent":
        player.losses += 1
        if isinstance(opponent, object) and hasattr(opponent, 'wins'):
            opponent.wins += 1
    else:
        player.draws += 1

    player.total_matches += 1

    # Match rating
    rating = result.get("rating", 2.0)
    if rating > player.best_match_rating:
        player.best_match_rating = rating

    # Popularity
    pop_change = result.get("popularity_change", 0)
    if is_ppv:
        pop_change = int(pop_change * 1.5)
    player.popularity = max(0, min(100, player.popularity + pop_change))
    if player.popularity > player.peak_popularity:
        player.peak_popularity = player.popularity

    # Alignment
    alignment_change = result.get("alignment_change", 0)
    player.alignment = max(-100, min(100, player.alignment + alignment_change))

    # Money
    pay = state.contract.get("pay_per_show", 0)
    if is_ppv:
        pay = int(pay * 2)
    player.money += pay
    player.total_earnings += pay

    # Momentum
    if result.get("winner") == "player":
        player.momentum = min(10, player.momentum + 1)
    else:
        player.momentum = max(-10, player.momentum - 1)

    # Backstage rep
    rep_change = result.get("rep_change", 0)
    player.backstage_rep = max(-100, min(100, player.backstage_rep + rep_change))

    # Record match
    state.match_history.append({
        "week": state.total_weeks,
        "opponent": opponent.ring_name if hasattr(opponent, 'ring_name') else str(opponent),
        "match_type": result.get("match_type", "unknown"),
        "rating": rating,
        "winner": result.get("winner", "unknown"),
        "ppv": is_ppv,
    })

    # Fan interest bonuses from high-interest matches
    fan_interest = result.get("fan_interest_total", 0)
    if fan_interest >= 25:
        # Viral match - big career boost
        fan_pop_bonus = min(8, fan_interest // 5)
        player.popularity = max(0, min(100, player.popularity + fan_pop_bonus))
        player.momentum = min(10, player.momentum + 1)
        player.social_media_followers = getattr(player, 'social_media_followers', 0) + fan_interest * 100
        # Extra XP from crowd-pleasing performance
        for skill in ("charisma", "mic_work"):
            player.add_skill_xp(skill, fan_interest // 3)
        print(f"\n  {colored(f'The crowd loved it! +{fan_pop_bonus} popularity. Social media is buzzing!', Colors.GOLD)}")
    elif fan_interest >= 15:
        fan_pop_bonus = min(4, fan_interest // 5)
        player.popularity = max(0, min(100, player.popularity + fan_pop_bonus))
        player.social_media_followers = getattr(player, 'social_media_followers', 0) + fan_interest * 50
        player.add_skill_xp("charisma", fan_interest // 5)

    # Merch sales bump from good matches
    merch_level = getattr(player, 'merch_level', 0)
    if merch_level > 0 and fan_interest >= 10:
        merch_cut = getattr(player, 'merch_cut_pct', 10)
        base_merch = fan_interest * merch_level * 5
        if is_ppv:
            base_merch *= 3
        merch_earnings = int(base_merch * merch_cut / 100)
        player.money += merch_earnings
        player.total_earnings += merch_earnings
        player.merch_income_total = getattr(player, 'merch_income_total', 0) + merch_earnings
        if merch_earnings >= 100:
            print(f"  {colored(f'Merch sales: +${merch_earnings:,}', Colors.MONEY)}")

    # Log notable matches
    if rating >= 4.0:
        state.log_career_event(
            f"{'PPV ' if is_ppv else ''}{rating:.1f}-star classic vs. "
            f"{opponent.ring_name if hasattr(opponent, 'ring_name') else opponent}"
        )


def off_day_phase(state):
    """Handle off-day activities."""
    from game.character.skills import present_training_options
    from game.systems.lifestyle import present_lifestyle_choices

    print_subheader("OFF DAY")

    options = [
        ("Train", "Hit the gym and work on your skills"),
        ("Rest", "Recover health and let your body heal"),
        ("Go Out", "Hit the town - bars, clubs, social scene"),
        ("Study Tape", "Watch matches and study the craft"),
        ("Manage Business", "Merch, brand deals, investments"),
    ]

    # Add relationship option if in one
    if state.player.relationship_status != "single":
        options.append(("Spend Time with Partner", "Maintain your relationship"))

    choice = print_menu(options, "How do you spend your off day?")

    player = state.player

    if choice == 0:  # Train
        present_training_options(player)
    elif choice == 1:  # Rest
        recovery = random.randint(10, 20)
        player.health = min(100, player.health + recovery)
        player.burnout = max(0, player.burnout - 5)
        print(f"\n  You rest up. Health +{recovery}. Burnout reduced.")
    elif choice == 2:  # Go out
        present_lifestyle_choices(player, "night_out")
    elif choice == 3:  # Study tape
        from game.character.skills import train_skill
        xp = random.randint(5, 12)
        skill = random.choice(["psychology", "in_ring"])
        leveled = player.add_skill_xp(skill, xp)
        from data.constants import SKILL_DISPLAY_NAMES
        print(f"\n  You study wrestling tapes for hours.")
        print(f"  {SKILL_DISPLAY_NAMES[skill]} +{xp} XP" + (" - LEVEL UP!" if leveled else ""))
    elif choice == 4:  # Business
        from game.systems.business import present_business_menu
        present_business_menu(player)
    elif choice == 5:  # Relationship
        player.relationship_health = min(100, player.relationship_health + 10)
        player.burnout = max(0, player.burnout - 3)
        print(f"\n  You spend quality time with {player.relationship_partner or 'your partner'}.")
        print(f"  Relationship health improved. Burnout reduced.")

    press_enter()


def monthly_phase(state):
    """Monthly career checks."""
    from game.systems.reputation import calculate_push_level

    player = state.player

    # Update push level
    player.momentum = calculate_push_level(player)

    # Financial check
    player.money -= 200 * 4  # Monthly expenses
    if player.money < 0:
        _msg = "You're broke. Living paycheck to paycheck."
        print(f"\n  {colored(_msg, Colors.WARNING)}")
        player.burnout += 5

    # Title defense tracking
    if player.titles_held:
        player.weeks_as_champion += 4


def yearly_phase(state):
    """Yearly career milestones."""
    from game.character.skills import check_skill_milestones
    from game.systems.aging import process_aging, check_retirement_prompt

    player = state.player
    player.age += 1

    print_subheader(f"YEAR {state.current_year} IN REVIEW")
    print(f"  Age: {player.age}")
    print(f"  Record this year: Check your stats")
    print(f"  Current Popularity: {player.popularity}")
    print(f"  Money: ${player.money:,}")

    # Age effects
    process_aging(player)

    # Skill milestones
    check_skill_milestones(player)

    # Retirement check
    if player.age >= 35:
        check_retirement_prompt(state)

    press_enter()


def weekly_menu(state):
    """Show end-of-week menu options."""
    print_divider()
    options = [
        "Continue to next week",
        "View stats",
        "View career history",
        "Manage business",
        "Save game",
        "Retire",
    ]

    choice = print_menu(options, "What would you like to do?")

    if choice == 0:
        return
    elif choice == 1:
        clear_screen()
        print_stats(state.player)
        press_enter()
        weekly_menu(state)
    elif choice == 2:
        clear_screen()
        print_subheader("CAREER LOG")
        if state.career_log:
            for entry in state.career_log[-20:]:
                print(f"  Year {entry['year']}, Week {entry['week']}: {entry['text']}")
        else:
            print("  No notable events yet.")
        press_enter()
        weekly_menu(state)
    elif choice == 3:
        clear_screen()
        from game.systems.business import present_business_menu
        present_business_menu(state.player)
        press_enter()
        weekly_menu(state)
    elif choice == 4:
        present_save_menu(state)
        weekly_menu(state)
    elif choice == 5:
        if confirm("Are you sure you want to retire?"):
            state.game_over = True
            state.game_over_reason = "retirement"
            state.log_career_event(f"Retired from professional wrestling at age {state.player.age}")


def _present_concussion_choice(state, concussion_injuries):
    """Present the choice to wrestle through a concussion with CTE risks."""
    player = state.player
    worst = max(concussion_injuries, key=lambda i: i.severity)

    print(f"\n  {colored('CONCUSSION PROTOCOL', Colors.INJURY)}")
    for inj in concussion_injuries:
        print(f"    - {inj.description}: {inj.weeks_remaining} weeks remaining")

    # Show CTE warning based on history
    if player.concussion_count >= 5:
        print(f"\n  {colored(f'WARNING: This is concussion #{player.concussion_count + 1} of your career.', Colors.RED)}")
        print(f"  {colored(f'CTE Severity: {player.cte_severity}/100', Colors.RED)}")
    elif player.concussion_count >= 2:
        print(f"\n  {colored(f'Caution: You have had {player.concussion_count} concussions in your career.', Colors.WARNING)}")

    if player.weeks_since_concussion < 8:
        print(f"  {colored('Your last concussion was only {0} weeks ago. Second-impact risk is HIGH.'.format(player.weeks_since_concussion), Colors.RED)}")

    options = [
        ("Sit out and recover", f"Rest {worst.weeks_remaining} weeks. Protect your brain."),
        ("Compete anyway", "Risk CTE damage. Increased injury chance. The show must go on."),
    ]
    if worst.severity >= 3:
        options[1] = ("Compete anyway (DANGEROUS)", "Severe risk of permanent brain damage. Doctors advise against it.")

    choice = print_menu(options, "What do you do?")

    if choice == 0:
        print(f"\n  {dim('You follow concussion protocol. Your brain will thank you later.')}")
        player.health = min(100, player.health + 10)
        state._working_injured = False
    else:
        # Competing with a concussion
        cte_gain = worst.severity * 5
        if player.weeks_since_concussion < 8:
            cte_gain *= 2  # Second-impact syndrome
            print(f"\n  {colored('SECOND IMPACT RISK: Competing so soon after a concussion is extremely dangerous.', Colors.RED)}")
        else:
            print(f"\n  {colored('You ignore medical advice and suit up. The crowd will never know.', Colors.WARNING)}")

        player.cte_severity = min(100, player.cte_severity + cte_gain)
        player.painkiller_level = min(100, player.painkiller_level + 10)
        player.backstage_rep += 5  # Respect for toughness
        state._working_injured = True
        state._competing_concussed = True

        # CTE symptoms at high levels
        if player.cte_severity >= 60:
            symptoms = random.choice([
                "Your hands are trembling. You can't make it stop.",
                "The headaches are constant now. Light hurts.",
                "You forgot where you parked. Again.",
                "Your mood swings are getting worse. Everyone notices.",
            ])
            print(f"  {dim(symptoms)}")


def _try_generate_feud(state):
    """Try to organically generate a feud with a roster member."""
    from game.events.storylines import generate_storyline

    roster = state.get_current_roster()
    if not roster:
        return

    # Prefer opponents the player has a relationship with (positive or negative)
    candidates = []
    for npc in roster:
        if not npc.can_wrestle():
            continue
        rel = state.player.relationships.get(npc.npc_id, 0)
        # Strong relationship (positive or negative) = more likely feud
        weight = 1.0 + abs(rel) / 20.0
        # Champions make good feud targets
        if state.title_manager and state.title_manager.is_champion(npc.npc_id, state.player.current_promotion):
            weight *= 2.0
        # Similar skill level = more compelling
        rating_diff = abs(state.player.get_overall_rating() - npc.get_overall_rating())
        if rating_diff < 15:
            weight *= 1.5
        candidates.append((npc, weight))

    if not candidates:
        return

    weights = [w for _, w in candidates]
    opponent = random.choices([c for c, _ in candidates], weights=weights, k=1)[0]

    storyline = generate_storyline(state, opponent)
    if storyline:
        state.active_storyline = storyline
        print_subheader("A NEW RIVALRY BEGINS")
        print(f"  {colored(storyline['name'], Colors.GOLD)}")
        print(f"  A feud is brewing between you and {opponent.ring_name}...")
        state.log_career_event(f"Started feud with {opponent.ring_name}")


def _check_title_match(state, opponent, is_ppv):
    """Check if this match should be a title match.

    Returns dict with title info or None.
    """
    if not state.title_manager:
        return None

    promo_id = state.player.current_promotion
    player = state.player
    champions = state.title_manager.get_all_champions(promo_id)

    for title_name, reign in champions.items():
        if reign is None:
            continue

        opp_id = opponent.npc_id if opponent.npc_id else "player"

        # Opponent is the champion and player is challenger
        if reign.holder_id == opp_id:
            # Title matches happen at PPVs, or if in a title chase storyline
            is_title_chase = (state.active_storyline and
                              state.active_storyline.get("type") == "title_chase" and
                              state.active_storyline.get("opponent_id") == opp_id)
            if is_ppv or is_title_chase:
                return {
                    "title_name": title_name,
                    "player_is_champion": False,
                    "champion_id": opp_id,
                    "challenger_id": "player",
                }

        # Player is the champion defending
        if reign.holder_id == "player":
            # Champions defend at PPVs, or 30% chance on regular shows
            if is_ppv or random.random() < 0.3:
                return {
                    "title_name": title_name,
                    "player_is_champion": True,
                    "champion_id": "player",
                    "challenger_id": opp_id,
                }

    return None


def _resolve_title_result(state, result, opponent, title_info):
    """Resolve a title match outcome through the TitleManager."""
    player = state.player
    promo_id = player.current_promotion
    title_name = title_info["title_name"]
    winner = result.get("winner")

    if title_info["player_is_champion"]:
        champion = player
        challenger = opponent
        match_result = "champion_wins" if winner == "player" else "challenger_wins"
    else:
        champion = opponent
        challenger = player
        match_result = "champion_wins" if winner == "opponent" else "challenger_wins"

    current_week = state.calendar.get_current_week_number() if state.calendar else state.total_weeks
    outcome = state.title_manager.resolve_title_match(
        promo_id, title_name, champion, challenger, match_result, current_week,
    )

    if outcome.get("title_change"):
        new_champ = outcome["new_champion"]
        former = outcome["former_champion"]
        print(f"\n  {colored(f'★ NEW CHAMPION! {new_champ} wins the {title_name}! ★', Colors.GOLD)}")
        state.log_career_event(f"Won the {title_name} by defeating {former}")

        # Update player tracking
        if winner == "player":
            if title_name not in player.titles_held:
                player.titles_held.append(title_name)
            if title_name not in player.career_titles:
                player.career_titles.append(title_name)
            player.popularity = min(100, player.popularity + 10)
        else:
            if title_name in player.titles_held:
                player.titles_held.remove(title_name)
                state.log_career_event(f"Lost the {title_name} to {opponent.ring_name}")
    else:
        if title_info["player_is_champion"] and winner == "player":
            defenses = outcome.get("defenses", 0)
            print(f"\n  {colored(f'Champion retains! Defense #{defenses}', Colors.GREEN)}")
        elif not title_info["player_is_champion"] and winner == "opponent":
            print(f"\n  {colored(f'{opponent.ring_name} retains the {title_name}.', Colors.RED)}")


def _simulate_npc_title_defenses(state):
    """Simulate NPC title defenses in other promotions."""
    from game.world.promotions import PROMOTIONS
    current_week = state.calendar.get_current_week_number() if state.calendar else state.total_weeks

    for promo_id, roster in state.promotion_rosters.items():
        if promo_id == state.player.current_promotion:
            continue  # Player's promotion titles handled in show_phase
        champions = state.title_manager.get_all_champions(promo_id)
        for title_name, reign in champions.items():
            if reign is None:
                continue
            if random.random() < 0.15:  # 15% chance per month
                result = state.title_manager.simulate_npc_title_defense(
                    promo_id, title_name, roster, current_week,
                )
                if result and result.get("title_change"):
                    # Silently record - player won't see this unless they check
                    pass


def _is_ppv_week(state):
    """Check if current week is a PPV week."""
    if hasattr(state, 'calendar') and state.calendar:
        return state.calendar.is_ppv_week(state.player.current_promotion)
    # Fallback: every 4th week
    return state.current_week % 4 == 0


def _advance_week(state):
    """Advance the game calendar by one week."""
    state.total_weeks += 1
    state.current_week += 1

    if state.current_week > 52:
        state.current_week = 1
        state.current_year += 1

    # Advance calendar object if present
    if hasattr(state, 'calendar') and state.calendar:
        result = state.calendar.advance_week()
        if result.get("rolled_month"):
            state.calendar.schedule_month([state.player.current_promotion])


def _handle_contract_expiry(state):
    """Handle contract expiration."""
    from game.world.promotions import PROMOTIONS, get_available_promotions
    from game.world.contracts import generate_offer

    player = state.player
    promo = PROMOTIONS.get(player.current_promotion)
    promo_name = promo.name if promo else player.current_promotion

    print_subheader("CONTRACT EXPIRED")
    print(f"  Your contract with {promo_name} has expired.")

    # Current promotion may offer renewal
    options = []
    if promo:
        new_offer = generate_offer(promo, player)
        options.append((
            f"Re-sign with {promo_name}",
            f"${new_offer.pay_per_show}/show, {new_offer.weeks_duration} weeks",
        ))

    # Other promotions may be interested
    available = get_available_promotions(player)
    available = [p for p in available if p.id != player.current_promotion][:3]
    for ap in available:
        offer = generate_offer(ap, player)
        options.append((
            f"Sign with {ap.name}",
            f"${offer.pay_per_show}/show, {offer.weeks_duration} weeks (Tier {ap.tier})",
        ))

    options.append(("Go freelance", "No contract. Work when you want."))

    choice = print_menu(options, "What do you do?")

    if choice == 0 and promo:
        # Re-sign
        new_offer = generate_offer(promo, player)
        state.contract = {
            "promotion_id": promo.id,
            "weeks_remaining": new_offer.weeks_duration,
            "pay_per_show": new_offer.pay_per_show,
            "exclusive": new_offer.exclusive,
        }
        player.money += new_offer.signing_bonus
        print(f"\n  Re-signed with {promo_name}!")
        if new_offer.signing_bonus:
            print(f"  Signing bonus: ${new_offer.signing_bonus:,}")
        state.log_career_event(f"Re-signed with {promo_name}")
    elif choice <= len(available) and choice > 0:
        # Sign with new promotion
        new_promo = available[choice - 1]
        offer = generate_offer(new_promo, player)
        player.current_promotion = new_promo.id
        if new_promo.id not in player.career_promotions:
            player.career_promotions.append(new_promo.id)
        state.contract = {
            "promotion_id": new_promo.id,
            "weeks_remaining": offer.weeks_duration,
            "pay_per_show": offer.pay_per_show,
            "exclusive": offer.exclusive,
        }
        player.money += offer.signing_bonus
        print(f"\n  Signed with {new_promo.name}!")
        if offer.signing_bonus:
            print(f"  Signing bonus: ${offer.signing_bonus:,}")
        state.log_career_event(f"Signed with {new_promo.name}")
    else:
        # Freelance
        state.contract = {
            "promotion_id": player.current_promotion,
            "weeks_remaining": 12,
            "pay_per_show": 50,
            "exclusive": False,
        }
        print(f"\n  You go freelance. Working indie dates.")

    press_enter()


def check_game_over(state):
    """Check for game-over conditions."""
    player = state.player

    if player.is_dead:
        state.game_over = True
        state.game_over_reason = "death"
        return

    if player.is_retired:
        state.game_over = True
        state.game_over_reason = "retirement"
        return

    if player.age >= 55:
        _msg = "Your body can't take it anymore. It's time to hang up the boots."
        print(f"\n  {colored(_msg, Colors.WARNING)}")
        state.game_over = True
        state.game_over_reason = "age"
        state.log_career_event("Forced to retire due to age")
