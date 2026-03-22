"""Career business management - merch, brand deals, investments, appearances."""

import random
from game.display import (
    print_subheader, print_menu, colored, Colors, bold, dim, press_enter,
    print_stat_bar,
)


# -----------------------------------------------------------------------
# Merch tiers
# -----------------------------------------------------------------------

MERCH_TIERS = {
    0: {"name": "None", "desc": "No merchandise", "cost": 0, "base_weekly": 0},
    1: {"name": "Basic", "desc": "T-shirts at the gimmick table", "cost": 500, "base_weekly": 20},
    2: {"name": "Standard", "desc": "Shirts, hats, and wristbands", "cost": 2000, "base_weekly": 80},
    3: {"name": "Premium", "desc": "Full line: shirts, posters, replica belts", "cost": 8000, "base_weekly": 250},
    4: {"name": "Deluxe", "desc": "Online store, action figures, DVD", "cost": 25000, "base_weekly": 600},
    5: {"name": "Empire", "desc": "Global brand, licensing deals, everything", "cost": 75000, "base_weekly": 1500},
}

# -----------------------------------------------------------------------
# Brand deal templates
# -----------------------------------------------------------------------

BRAND_DEAL_POOL = [
    {"name": "Local Gym Sponsorship", "min_pop": 10, "weekly_pay": 50, "weeks": 12, "tier_req": 0},
    {"name": "Energy Drink Endorsement", "min_pop": 25, "weekly_pay": 150, "weeks": 24, "tier_req": 1},
    {"name": "Supplement Company Deal", "min_pop": 20, "weekly_pay": 100, "weeks": 16, "tier_req": 1},
    {"name": "Regional TV Commercial", "min_pop": 35, "weekly_pay": 250, "weeks": 8, "tier_req": 2},
    {"name": "Video Game Appearance", "min_pop": 40, "weekly_pay": 400, "weeks": 4, "tier_req": 2},
    {"name": "Clothing Brand Collab", "min_pop": 45, "weekly_pay": 300, "weeks": 20, "tier_req": 2},
    {"name": "Podcast Sponsorship", "min_pop": 30, "weekly_pay": 200, "weeks": 26, "tier_req": 1},
    {"name": "National TV Commercial", "min_pop": 60, "weekly_pay": 800, "weeks": 8, "tier_req": 3},
    {"name": "Movie Cameo", "min_pop": 70, "weekly_pay": 2000, "weeks": 4, "tier_req": 4},
    {"name": "Major Brand Ambassador", "min_pop": 80, "weekly_pay": 1500, "weeks": 52, "tier_req": 4},
]

# -----------------------------------------------------------------------
# Investment options
# -----------------------------------------------------------------------

INVESTMENT_POOL = [
    {
        "name": "Wrestling School",
        "cost": 15000,
        "weekly_income": 200,
        "min_pop": 30,
        "description": "Train the next generation. Steady income.",
    },
    {
        "name": "Gym Ownership",
        "cost": 25000,
        "weekly_income": 350,
        "min_pop": 20,
        "description": "Your own gym. Members pay monthly.",
    },
    {
        "name": "Bar / Restaurant",
        "cost": 40000,
        "weekly_income": 500,
        "min_pop": 35,
        "description": "A themed bar. Risky but lucrative.",
    },
    {
        "name": "Real Estate (Rental Property)",
        "cost": 60000,
        "weekly_income": 600,
        "min_pop": 0,
        "description": "Buy a rental property. Passive income.",
    },
    {
        "name": "Indie Promotion (Owner)",
        "cost": 50000,
        "weekly_income": 400,
        "min_pop": 40,
        "description": "Start your own small promotion.",
    },
    {
        "name": "Online Content / YouTube",
        "cost": 5000,
        "weekly_income": 100,
        "min_pop": 25,
        "description": "Start a YouTube channel. Build your brand online.",
    },
]


# -----------------------------------------------------------------------
# Weekly business processing
# -----------------------------------------------------------------------

def process_weekly_business(player):
    """Process weekly income from merch, brand deals, investments.

    Returns total business income for the week.
    """
    total = 0

    # Merch income
    merch_tier = MERCH_TIERS.get(player.merch_level, MERCH_TIERS[0])
    base_merch = merch_tier["base_weekly"]
    if base_merch > 0:
        # Scale by popularity and social media
        pop_mult = 0.5 + (player.popularity / 100.0)
        social_mult = 1.0 + min(1.0, getattr(player, 'social_media_followers', 0) / 100000.0)
        merch_income = int(base_merch * pop_mult * social_mult)
        merch_cut = max(1, player.merch_cut_pct) / 100.0
        merch_income = int(merch_income * merch_cut)
        player.money += merch_income
        player.total_earnings += merch_income
        player.merch_income_total += merch_income
        total += merch_income

    # Brand deal income
    active_deals = []
    for deal in player.brand_deals:
        if deal.get("weeks_remaining", 0) > 0:
            pay = deal.get("weekly_pay", 0)
            player.money += pay
            player.total_earnings += pay
            total += pay
            deal["weeks_remaining"] -= 1
            if deal["weeks_remaining"] > 0:
                active_deals.append(deal)
    player.brand_deals = active_deals

    # Investment income
    for inv in player.business_investments:
        income = inv.get("weekly_income", 0)
        # Random variance for businesses
        variance = random.uniform(0.7, 1.3)
        actual = int(income * variance)
        player.money += actual
        player.total_earnings += actual
        total += actual

    # Appearance fee income (if popular enough)
    appearance_fee = getattr(player, 'appearance_fee', 0)
    if appearance_fee > 0 and random.random() < 0.3:  # 30% chance of an appearance gig
        player.money += appearance_fee
        player.total_earnings += appearance_fee
        total += appearance_fee

    return total


# -----------------------------------------------------------------------
# Business management menu
# -----------------------------------------------------------------------

def present_business_menu(player):
    """Show the business management menu."""
    print_subheader("CAREER BUSINESS MANAGEMENT")

    # Current status
    merch_tier = MERCH_TIERS.get(player.merch_level, MERCH_TIERS[0])
    print(f"  {bold('Merch Tier:')} {merch_tier['name']} - {merch_tier['desc']}")
    print(f"  {bold('Merch Cut:')} {player.merch_cut_pct}% of sales")
    print(f"  {bold('Social Media:')} {getattr(player, 'social_media_followers', 0):,} followers")
    print(f"  {bold('Appearance Fee:')} ${getattr(player, 'appearance_fee', 0):,}")
    print(f"  {bold('Lifetime Merch Income:')} ${getattr(player, 'merch_income_total', 0):,}")
    if player.brand_deals:
        print(f"  {bold('Active Brand Deals:')} {len(player.brand_deals)}")
        for deal in player.brand_deals:
            print(f"    - {deal['name']}: ${deal['weekly_pay']}/wk ({deal['weeks_remaining']} wks left)")
    if player.business_investments:
        print(f"  {bold('Investments:')}")
        for inv in player.business_investments:
            print(f"    - {inv['name']}: ~${inv['weekly_income']}/wk")
    print(f"\n  {bold('Cash:')} {colored(f'${player.money:,}', Colors.MONEY)}")

    options = [
        ("Upgrade Merch", "Expand your merchandise line"),
        ("Negotiate Merch Cut", "Demand a bigger slice of merch revenue"),
        ("Brand Deals", "View and accept endorsement offers"),
        ("Invest in a Business", "Spend money to make money"),
        ("Set Appearance Fee", "How much you charge for appearances"),
        ("Back", "Return to the game"),
    ]

    choice = print_menu(options, "Business")

    if choice == 0:
        _upgrade_merch(player)
    elif choice == 1:
        _negotiate_merch_cut(player)
    elif choice == 2:
        _brand_deals_menu(player)
    elif choice == 3:
        _investment_menu(player)
    elif choice == 4:
        _set_appearance_fee(player)
    elif choice == 5:
        return


def _upgrade_merch(player):
    """Upgrade merch tier."""
    current = player.merch_level
    if current >= 5:
        print(f"\n  {dim('Your merch empire is already at maximum.')}")
        return

    next_tier = MERCH_TIERS[current + 1]
    cost = next_tier["cost"]
    print(f"\n  {bold('Upgrade to:')} {next_tier['name']} - {next_tier['desc']}")
    print(f"  {bold('Cost:')} ${cost:,}")
    print(f"  {bold('Base weekly income:')} ~${next_tier['base_weekly']}/week (scaled by popularity)")

    if player.money < cost:
        print(f"\n  {colored(f'Not enough cash. You need ${cost:,} but have ${player.money:,}.', Colors.RED)}")
        return

    options = [("Buy upgrade", f"Spend ${cost:,}"), ("Cancel", "Not right now")]
    if print_menu(options, "Upgrade?") == 0:
        player.money -= cost
        player.merch_level += 1
        # Start with a basic cut if first merch
        if player.merch_cut_pct == 0:
            player.merch_cut_pct = 10
        tier_name = next_tier["name"]
        print(f"\n  {colored(f'Merch upgraded to {tier_name}!', Colors.GREEN)}")


def _negotiate_merch_cut(player):
    """Try to negotiate a better merch cut percentage."""
    if player.merch_level == 0:
        print(f"\n  {dim('You have no merch to negotiate a cut for.')}")
        return

    current = player.merch_cut_pct
    print(f"\n  Current merch cut: {current}%")

    if current >= 80:
        print(f"  {dim('Your cut is already near the maximum.')}")
        return

    # Success based on popularity and charisma
    charisma = player.get_effective_skill("charisma")
    success_chance = 0.3 + (player.popularity / 200.0) + (charisma / 300.0)

    options = [
        ("Ask for 5% more", "Modest request, likely to succeed"),
        ("Demand 15% more", "Aggressive - needs leverage"),
        ("Cancel", "Keep current deal"),
    ]
    choice = print_menu(options, "Negotiation")

    if choice == 0:
        if random.random() < success_chance + 0.2:
            increase = 5
            player.merch_cut_pct = min(80, current + increase)
            print(f"\n  {colored(f'Deal! Your merch cut is now {player.merch_cut_pct}%.', Colors.GREEN)}")
        else:
            print(f"\n  {dim('They say no. You have not earned that yet.')}")
    elif choice == 1:
        if random.random() < success_chance - 0.1:
            increase = 15
            player.merch_cut_pct = min(80, current + increase)
            print(f"\n  {colored(f'They agree! Your merch cut is now {player.merch_cut_pct}%.', Colors.GREEN)}")
        else:
            msg = 'They shut you down hard. "Know your place."'
            print(f"\n  {colored(msg, Colors.RED)}")
            player.backstage_rep -= 5


def _brand_deals_menu(player):
    """Show available brand deals."""
    print_subheader("BRAND DEALS")

    # Generate available deals based on popularity
    available = [d for d in BRAND_DEAL_POOL if player.popularity >= d["min_pop"]]
    # Filter out deals player already has
    active_names = {d["name"] for d in player.brand_deals}
    available = [d for d in available if d["name"] not in active_names]

    if not available:
        print(f"  {dim('No brand deals available right now. Build your popularity.')}")
        return

    # Show 3 random offers
    offers = random.sample(available, min(3, len(available)))

    options = []
    for deal in offers:
        options.append((
            deal["name"],
            f"${deal['weekly_pay']}/wk for {deal['weeks']} weeks (${deal['weekly_pay'] * deal['weeks']:,} total)",
        ))
    options.append(("Decline all", "Not interested right now"))

    choice = print_menu(options, "Accept a deal?")
    if choice < len(offers):
        deal = offers[choice]
        player.brand_deals.append({
            "name": deal["name"],
            "weekly_pay": deal["weekly_pay"],
            "weeks_remaining": deal["weeks"],
        })
        deal_name = deal["name"]
        deal_pay = deal["weekly_pay"]
        deal_wks = deal["weeks"]
        print(f"\n  {colored(f'Signed with {deal_name}! ${deal_pay}/week for {deal_wks} weeks.', Colors.GREEN)}")
    else:
        print(f"\n  {dim('You pass on the deals for now.')}")


def _investment_menu(player):
    """Show investment opportunities."""
    print_subheader("INVESTMENTS")

    # Filter to investments player can afford and qualifies for
    owned_names = {inv["name"] for inv in player.business_investments}
    available = [inv for inv in INVESTMENT_POOL
                 if inv["name"] not in owned_names and player.popularity >= inv["min_pop"]]

    if not available:
        if len(owned_names) == len(INVESTMENT_POOL):
            print(f"  {dim('You own every available investment. True mogul status.')}")
        else:
            print(f"  {dim('No new investments available. Build your popularity and cash.')}")
        return

    options = []
    for inv in available:
        affordable = player.money >= inv["cost"]
        label = inv["name"]
        if not affordable:
            label += " (CAN'T AFFORD)"
        options.append((
            label,
            f"{inv['description']} | Cost: ${inv['cost']:,} | Income: ~${inv['weekly_income']}/wk",
        ))
    options.append(("Cancel", "Not right now"))

    choice = print_menu(options, "Invest?")
    if choice < len(available):
        inv = available[choice]
        if player.money < inv["cost"]:
            inv_cost = inv["cost"]
            print(f"\n  {colored(f'Not enough cash. Need ${inv_cost:,}.', Colors.RED)}")
            return
        player.money -= inv["cost"]
        player.business_investments.append({
            "name": inv["name"],
            "weekly_income": inv["weekly_income"],
        })
        inv_name = inv["name"]
        inv_income = inv["weekly_income"]
        print(f"\n  {colored(f'Invested in {inv_name}! Expected ~${inv_income}/week.', Colors.GREEN)}")


def _set_appearance_fee(player):
    """Set the player's appearance fee for public appearances."""
    current = getattr(player, 'appearance_fee', 0)
    print(f"\n  Current appearance fee: ${current:,}")
    print(f"  Your popularity: {player.popularity}")

    # Suggest a fee based on popularity
    suggested = max(0, player.popularity * 10 - 50)
    print(f"  Suggested rate: ${suggested:,}")

    options = [
        ("Free (build your brand)", "$0 - more appearance opportunities"),
        (f"Low (${max(50, suggested // 2):,})", "Affordable - more bookings"),
        (f"Market rate (${suggested:,})", "Fair price for your level"),
        (f"Premium (${suggested * 2:,})", "High price - fewer bookings"),
    ]
    if current > 0:
        options.append(("Keep current", f"${current:,}"))

    choice = print_menu(options, "Set your fee")
    fees = [0, max(50, suggested // 2), suggested, suggested * 2]
    if choice < 4:
        player.appearance_fee = fees[choice]
        print(f"\n  Appearance fee set to ${player.appearance_fee:,}.")
    # else keep current
