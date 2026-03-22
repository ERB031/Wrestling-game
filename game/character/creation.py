"""Character creation wizard."""

import random
from game.display import (
    clear_screen, print_header, print_subheader, print_menu, print_stats,
    print_stat_bar, get_input, bold, colored, Colors, press_enter, dim,
    print_divider,
)
from game.character.wrestler import Wrestler
from game.character.backstory import (
    BACKSTORIES, WRESTLING_STYLES, get_starting_skills,
)
from data.constants import SKILL_DISPLAY_NAMES


def create_character():
    """Run the full character creation flow. Returns a Wrestler."""
    clear_screen()
    print_header("CREATE YOUR WRESTLER")
    print()
    print("  Every legend starts somewhere.")
    print("  Time to build yours.")
    press_enter()

    # Step 1: Real name
    clear_screen()
    print_header("STEP 1: WHO ARE YOU?")
    print()
    real_name = ""
    while not real_name:
        real_name = get_input("Enter your real name: ")
    print()
    print(f"  {bold(real_name)}. Let's see where you come from.")
    press_enter()

    # Step 2: Backstory
    clear_screen()
    print_header("STEP 2: YOUR BACKSTORY")
    print()
    print("  Everyone in this business has a story.")
    print("  What's yours?")
    print()

    backstory_options = []
    backstory_ids = list(BACKSTORIES.keys())
    for bs_id in backstory_ids:
        bs = BACKSTORIES[bs_id]
        backstory_options.append((bs["name"], bs["description"][:100] + "..."))

    backstory_idx = print_menu(backstory_options, "Choose your backstory")
    backstory_id = backstory_ids[backstory_idx]
    backstory = BACKSTORIES[backstory_id]

    # Show full backstory
    clear_screen()
    print_subheader(backstory["name"])
    print()
    print(f"  {backstory['description']}")
    print()
    print(f"  Starting Age: {bold(str(backstory['starting_age']))}")
    print(f"  Starting Money: {colored(f'${backstory[\"starting_money\"]:,}', Colors.MONEY)}")
    print()
    print("  Skill Modifiers:")
    for skill, bonus in backstory["skill_bonuses"].items():
        display = SKILL_DISPLAY_NAMES.get(skill, skill)
        color = Colors.GREEN if bonus > 0 else Colors.RED
        sign = "+" if bonus > 0 else ""
        print(f"    {display}: {colored(f'{sign}{bonus}', color)}")
    print()
    print(f"  Starting Promotions: {', '.join(backstory['starting_promotions'])}")
    press_enter()

    # Step 3: Wrestling style
    clear_screen()
    print_header("STEP 3: YOUR STYLE")
    print()
    print("  How do you fight?")
    print()

    style_options = []
    style_ids = list(WRESTLING_STYLES.keys())
    for st_id in style_ids:
        st = WRESTLING_STYLES[st_id]
        style_options.append((st["name"], st["description"]))

    style_idx = print_menu(style_options, "Choose your wrestling style")
    style_id = style_ids[style_idx]
    style = WRESTLING_STYLES[style_id]

    # Show style details
    clear_screen()
    print_subheader(style["name"])
    print()
    print(f"  {style['description']}")
    print()
    print("  Skill Modifiers:")
    for skill, bonus in style["skill_bonuses"].items():
        display = SKILL_DISPLAY_NAMES.get(skill, skill)
        color = Colors.GREEN if bonus > 0 else Colors.RED
        sign = "+" if bonus > 0 else ""
        print(f"    {display}: {colored(f'{sign}{bonus}', color)}")
    press_enter()

    # Step 4: Ring name and finisher
    clear_screen()
    print_header("STEP 4: YOUR CHARACTER")
    print()

    ring_name = ""
    while not ring_name:
        ring_name = get_input("Enter your ring name: ")

    print()
    finisher = ""
    while not finisher:
        finisher = get_input("Name your finishing move: ")

    print()
    print("  Pick your entrance style:")
    entrance_options = [
        ("Intense & Brooding", "Dark lighting, slow walk, intimidating presence"),
        ("High Energy", "Pyro, running to the ring, crowd interaction"),
        ("Cocky Swagger", "Strut to the ring, posing, talking trash"),
        ("No-Nonsense", "Walk straight to the ring, all business"),
        ("Mysterious", "Smoke, dim lights, cryptic imagery"),
        ("Over-the-Top", "Elaborate costume, dramatic poses, spectacle"),
    ]
    entrance_idx = print_menu(entrance_options, "Choose entrance style")
    entrance_style = entrance_options[entrance_idx][0]

    # Step 5: Starting alignment
    clear_screen()
    print_header("STEP 5: FACE OR HEEL?")
    print()
    print("  In this business, you're either the hero or the villain.")
    print("  At least, that's how it starts.")
    print()

    alignment_options = [
        ("Babyface", "The hero. The crowd cheers for you. You fight fair. Mostly."),
        ("Heel", "The villain. They boo you. They pay to see you get your ass kicked. You love it."),
        ("Tweener", "Neither. Both. You do what you want. Some love you, some hate you."),
    ]
    alignment_idx = print_menu(alignment_options, "Choose your starting alignment")
    starting_alignment = [30, -30, 0][alignment_idx]

    # Build the wrestler
    skills = get_starting_skills(backstory_id, style_id)

    wrestler = Wrestler(
        real_name=real_name,
        ring_name=ring_name,
        age=backstory["starting_age"],
        backstory_id=backstory_id,
        style_id=style_id,
        skills=skills,
        health=100,
        alignment=starting_alignment,
        booked_alignment=starting_alignment,
        popularity=5,
        backstage_rep=0,
        money=backstory["starting_money"],
        finisher_name=finisher,
        entrance_style=entrance_style,
        is_player=True,
        current_promotion=backstory["starting_promotions"][0],
        career_promotions=[backstory["starting_promotions"][0]],
    )

    # Backstory-specific setup
    if backstory_id == "bodybuilder":
        wrestler.steroid_use = True
        wrestler.steroid_cumulative = 52  # Been on for a year
        wrestler.look = min(100, wrestler.skills["look"])

    if backstory_id == "football":
        wrestler.body_damage["left_knee"] = 20  # Old injury
        wrestler.body_damage["right_knee"] = 10

    if backstory_id == "backyard":
        wrestler.body_damage["head"] = 10
        wrestler.body_damage["back"] = 10
        wrestler.body_damage["ribs"] = 5

    # Summary
    clear_screen()
    print_header("YOUR WRESTLER")
    print()
    print(f'  Real Name: {bold(wrestler.real_name)}')
    print(f'  Ring Name: {bold(wrestler.ring_name)}')
    print(f'  Age: {wrestler.age}')
    print(f'  Background: {backstory["name"]}')
    print(f'  Style: {style["name"]}')
    print(f'  Finisher: {bold(wrestler.finisher_name)}')
    print(f'  Entrance: {wrestler.entrance_style}')
    print()
    print_stats(wrestler)
    print()
    print(f"  Starting Promotion: {colored(wrestler.current_promotion.upper(), Colors.CYAN)}")
    press_enter()

    clear_screen()
    print()
    print(colored("  The road starts here.", Colors.GOLD))
    print()
    if backstory_id == "backyard":
        print("  A plywood ring in someone's backyard. Twenty drunk people")
        print("  standing around. A boombox playing entrance music.")
        print("  It's not much. But it's a start.")
    elif backstory_id == "dojo":
        print("  The dojo is quiet. Your sensei nods as you leave.")
        print('  "Remember what I taught you," he says. That\'s all.')
        print("  You bow. Time to show the world.")
    elif backstory_id == "amateur":
        print("  You walk into the wrestling school. The ring looks different")
        print("  than what you're used to. Ropes instead of a mat edge.")
        print("  The coach sizes you up. 'Can you take a bump?'")
        print("  Time to find out.")
    elif backstory_id == "football":
        print("  The NFL dream is dead. But this? This could be something.")
        print("  The promoter looks at your build and grins.")
        print("  'Kid, you're money. We just gotta teach you how to work.'")
    elif backstory_id == "second_gen":
        print(f"  Everyone in the locker room knows your last name.")
        print(f'  "You look just like your old man," they say.')
        print(f"  You don't know if that's a compliment or a warning.")
    elif backstory_id == "street_fighter":
        print("  The promoter finds you after the bar clears out.")
        print("  'You got a hell of a right hand, kid.'")
        print("  You've got scars older than some of these wrestlers.")
        print("  This is just another kind of fight.")
    elif backstory_id == "theater_kid":
        print("  The wrestling school is... humbling. You can cut a promo")
        print("  better than anyone here. But when they throw you in the ring?")
        print("  Your body hits the mat and you see God.")
        print("  'Again,' the coach says. It's going to be a long road.")
    elif backstory_id == "bodybuilder":
        print("  The Performance Center. State-of-the-art everything.")
        print("  You look like a million bucks. You move like a newborn deer.")
        print("  The trainers whisper. 'Great look. Can he work?'")
        print("  Only one way to find out.")
    press_enter()

    return wrestler
