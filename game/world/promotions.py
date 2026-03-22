"""All wrestling promotions in the game world."""

from dataclasses import dataclass, field


@dataclass
class Title:
    name: str
    prestige: int  # 1-100
    is_tag: bool = False
    is_womens: bool = False

    def to_dict(self):
        return {
            "name": self.name,
            "prestige": self.prestige,
            "is_tag": self.is_tag,
            "is_womens": self.is_womens,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


@dataclass
class Promotion:
    id: str
    name: str
    short_name: str
    tier: int  # 1-4
    style_preferences: list = field(default_factory=list)
    skill_minimums: dict = field(default_factory=dict)
    drug_testing: bool = False
    violence_tolerance: int = 5  # 0-10
    titles: list = field(default_factory=list)
    roster_size: int = 12
    tv_deal: bool = False
    pay_min: int = 0
    pay_max: int = 0
    reputation_weight: float = 0.3  # How much backstage politics matters (0.0-1.0)
    description: str = ""

    def to_dict(self):
        data = {}
        for key, value in self.__dict__.items():
            if key == "titles":
                data[key] = [t.to_dict() for t in value]
            else:
                data[key] = value
        return data

    @classmethod
    def from_dict(cls, data):
        titles_data = data.pop("titles", [])
        promo = cls(**data)
        promo.titles = [Title.from_dict(t) for t in titles_data]
        return promo


# ---------------------------------------------------------------------------
# Promotion definitions
# ---------------------------------------------------------------------------

PROMOTIONS = {
    "backyard": Promotion(
        id="backyard",
        name="Backyard Wrestling Alliance",
        short_name="BWA",
        tier=1,
        style_preferences=["hardcore", "deathmatch", "brawling"],
        skill_minimums={},
        drug_testing=False,
        violence_tolerance=10,
        titles=[
            Title("BWA Backyard Champion", prestige=5),
        ],
        roster_size=8,
        tv_deal=False,
        pay_min=0,
        pay_max=0,
        reputation_weight=0.0,
        description="No ring. No rules. No pay. Just a trampoline and some fluorescent light tubes in somebody's backyard.",
    ),

    "czw": Promotion(
        id="czw",
        name="Combat Zone Wrestling",
        short_name="CZW",
        tier=2,
        style_preferences=["deathmatch", "hardcore", "high_flying"],
        skill_minimums={"in_ring": 15, "violence": 25},
        drug_testing=False,
        violence_tolerance=10,
        titles=[
            Title("CZW World Heavyweight Championship", prestige=30),
            Title("CZW Wired Championship", prestige=20),
            Title("CZW Tag Team Championship", prestige=15, is_tag=True),
        ],
        roster_size=14,
        tv_deal=False,
        pay_min=25,
        pay_max=100,
        reputation_weight=0.15,
        description="The tournament of death awaits. Barbed wire, glass, and thumbtacks are your friends here.",
    ),

    "roh": Promotion(
        id="roh",
        name="Ring of Honor",
        short_name="ROH",
        tier=2,
        style_preferences=["technical", "strong_style", "high_flying"],
        skill_minimums={"in_ring": 30, "psychology": 20},
        drug_testing=False,
        violence_tolerance=4,
        titles=[
            Title("ROH World Championship", prestige=50),
            Title("ROH Television Championship", prestige=35),
            Title("ROH World Tag Team Championship", prestige=35, is_tag=True),
            Title("ROH Pure Championship", prestige=40),
        ],
        roster_size=16,
        tv_deal=True,
        pay_min=75,
        pay_max=300,
        reputation_weight=0.2,
        description="The workrate mecca. If you can go in the ring, you can make your name here. Honor means something.",
    ),

    "pwg": Promotion(
        id="pwg",
        name="Pro Wrestling Guerrilla",
        short_name="PWG",
        tier=2,
        style_preferences=["high_flying", "technical", "comedy"],
        skill_minimums={"in_ring": 30, "athleticism": 25},
        drug_testing=False,
        violence_tolerance=5,
        titles=[
            Title("PWG World Championship", prestige=45),
            Title("PWG World Tag Team Championship", prestige=35, is_tag=True),
        ],
        roster_size=12,
        tv_deal=False,
        pay_min=50,
        pay_max=250,
        reputation_weight=0.1,
        description="The buzz factory. A small gym in Reseda that churns out future stars. BOLA is the proving ground.",
    ),

    "njpw": Promotion(
        id="njpw",
        name="New Japan Pro Wrestling",
        short_name="NJPW",
        tier=3,
        style_preferences=["strong_style", "technical", "puroresu"],
        skill_minimums={"in_ring": 45, "psychology": 35, "athleticism": 30},
        drug_testing=False,
        violence_tolerance=6,
        titles=[
            Title("IWGP World Heavyweight Championship", prestige=90),
            Title("IWGP Intercontinental Championship", prestige=70),
            Title("IWGP United States Championship", prestige=55),
            Title("IWGP Junior Heavyweight Championship", prestige=65),
            Title("IWGP Tag Team Championship", prestige=55, is_tag=True),
            Title("IWGP Junior Heavyweight Tag Team Championship", prestige=40, is_tag=True),
            Title("NEVER Openweight Championship", prestige=50),
        ],
        roster_size=20,
        tv_deal=True,
        pay_min=300,
        pay_max=2000,
        reputation_weight=0.25,
        description="The King of Sports. Strong Style is a way of life. G1 Climax separates the men from the boys.",
    ),

    "ajpw": Promotion(
        id="ajpw",
        name="All Japan Pro Wrestling",
        short_name="AJPW",
        tier=3,
        style_preferences=["puroresu", "technical", "strong_style"],
        skill_minimums={"in_ring": 40, "psychology": 30, "durability": 30},
        drug_testing=False,
        violence_tolerance=5,
        titles=[
            Title("Triple Crown Heavyweight Championship", prestige=80),
            Title("World Junior Heavyweight Championship", prestige=50),
            Title("World Tag Team Championship", prestige=55, is_tag=True),
        ],
        roster_size=16,
        tv_deal=True,
        pay_min=250,
        pay_max=1500,
        reputation_weight=0.3,
        description="Kings Road style. Stiff chops and fighting spirit. The legacy of Giant Baba lives on.",
    ),

    "ecw": Promotion(
        id="ecw",
        name="Extreme Championship Wrestling",
        short_name="ECW",
        tier=3,
        style_preferences=["hardcore", "deathmatch", "high_flying", "technical"],
        skill_minimums={"in_ring": 25, "violence": 30, "charisma": 20},
        drug_testing=False,
        violence_tolerance=9,
        titles=[
            Title("ECW World Heavyweight Championship", prestige=65),
            Title("ECW Television Championship", prestige=45),
            Title("ECW Tag Team Championship", prestige=40, is_tag=True),
        ],
        roster_size=18,
        tv_deal=True,
        pay_min=100,
        pay_max=800,
        reputation_weight=0.2,
        description="The house that extreme built. Innovation, violence, and a rabid fanbase. EC-DUB. EC-DUB.",
    ),

    "tna": Promotion(
        id="tna",
        name="TNA/Impact Wrestling",
        short_name="TNA",
        tier=3,
        style_preferences=["technical", "high_flying", "entertainment"],
        skill_minimums={"in_ring": 30, "charisma": 25, "look": 20},
        drug_testing=True,  # Sometimes
        violence_tolerance=5,
        titles=[
            Title("TNA World Heavyweight Championship", prestige=60),
            Title("TNA X Division Championship", prestige=50),
            Title("TNA World Tag Team Championship", prestige=40, is_tag=True),
            Title("TNA Knockouts Championship", prestige=45, is_womens=True),
        ],
        roster_size=18,
        tv_deal=True,
        pay_min=200,
        pay_max=1200,
        reputation_weight=0.6,
        description="The alternative. Creative freedom mixed with backstage politics. The X Division is where stars are born.",
    ),

    "nxt": Promotion(
        id="nxt",
        name="NXT",
        short_name="NXT",
        tier=3,
        style_preferences=["technical", "entertainment", "high_flying"],
        skill_minimums={"in_ring": 30, "look": 25, "athleticism": 25},
        drug_testing=True,
        violence_tolerance=4,
        titles=[
            Title("NXT Championship", prestige=65),
            Title("NXT North American Championship", prestige=45),
            Title("NXT Tag Team Championship", prestige=40, is_tag=True),
            Title("NXT Women's Championship", prestige=55, is_womens=True),
        ],
        roster_size=20,
        tv_deal=True,
        pay_min=500,
        pay_max=1500,
        reputation_weight=0.35,
        description="WWE's developmental brand, but a powerhouse in its own right. Prove yourself here and the main roster calls.",
    ),

    "aew": Promotion(
        id="aew",
        name="All Elite Wrestling",
        short_name="AEW",
        tier=4,
        style_preferences=["technical", "high_flying", "strong_style", "entertainment"],
        skill_minimums={"in_ring": 50, "charisma": 35, "psychology": 35},
        drug_testing=False,
        violence_tolerance=5,
        titles=[
            Title("AEW World Championship", prestige=85),
            Title("AEW International Championship", prestige=60),
            Title("AEW TNT Championship", prestige=55),
            Title("AEW World Tag Team Championship", prestige=55, is_tag=True),
            Title("AEW World Trios Championship", prestige=40, is_tag=True),
            Title("AEW Women's World Championship", prestige=55, is_womens=True),
            Title("AEW Continental Championship", prestige=50),
        ],
        roster_size=20,
        tv_deal=True,
        pay_min=1000,
        pay_max=10000,
        reputation_weight=0.3,
        description="Creative freedom, elite competition. Built by the Elite, for the fans. Wednesday nights belong to AEW.",
    ),

    "wwe": Promotion(
        id="wwe",
        name="WWE",
        short_name="WWE",
        tier=4,
        style_preferences=["entertainment", "power", "look"],
        skill_minimums={"charisma": 40, "look": 40, "mic_work": 35, "in_ring": 35},
        drug_testing=True,
        violence_tolerance=3,
        titles=[
            Title("WWE Universal Championship", prestige=95),
            Title("WWE Championship", prestige=95),
            Title("WWE Intercontinental Championship", prestige=70),
            Title("WWE United States Championship", prestige=65),
            Title("WWE Raw Tag Team Championship", prestige=50, is_tag=True),
            Title("WWE SmackDown Tag Team Championship", prestige=50, is_tag=True),
            Title("WWE Raw Women's Championship", prestige=65, is_womens=True),
            Title("WWE SmackDown Women's Championship", prestige=65, is_womens=True),
        ],
        roster_size=20,
        tv_deal=True,
        pay_min=2000,
        pay_max=25000,
        reputation_weight=0.7,
        description="The biggest stage in professional wrestling. Millions watching. Huge money. But Vince's way or the highway.",
    ),

    "retirement": Promotion(
        id="retirement",
        name="Legends Circuit",
        short_name="Legends",
        tier=1,
        style_preferences=["entertainment", "comedy"],
        skill_minimums={"popularity": 30},
        drug_testing=False,
        violence_tolerance=2,
        titles=[
            Title("Legends Championship", prestige=10),
        ],
        roster_size=10,
        tv_deal=False,
        pay_min=100,
        pay_max=500,
        reputation_weight=0.1,
        description="Where old warriors go to cash in on nostalgia. Autograph signings, legends matches, and one more run.",
    ),
}


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------

def get_promotion(promotion_id):
    """Return a Promotion by its id, or None if not found."""
    return PROMOTIONS.get(promotion_id)


def get_all_promotions():
    """Return every promotion as a dict keyed by id."""
    return PROMOTIONS


def get_promotions_by_tier(tier):
    """Return a list of promotions matching the given tier."""
    return [p for p in PROMOTIONS.values() if p.tier == tier]


def get_available_promotions(wrestler):
    """Return promotions that might be interested in the wrestler.

    A promotion is available if the wrestler meets at least *some* of
    its skill minimums or if the promotion has no minimums at all.
    Tier-4 promotions require meeting most minimums.
    """
    available = []
    for promo in PROMOTIONS.values():
        if promo.id == "retirement":
            # Legends circuit only for older / popular wrestlers
            if wrestler.age >= 38 or wrestler.popularity >= 30:
                available.append(promo)
            continue

        if not promo.skill_minimums:
            available.append(promo)
            continue

        # Count how many minimums the wrestler meets
        met = 0
        total = len(promo.skill_minimums)
        for skill, minimum in promo.skill_minimums.items():
            if skill == "popularity":
                value = wrestler.popularity
            else:
                value = wrestler.get_effective_skill(skill)
            if value >= minimum:
                met += 1

        # Tier 4 requires meeting all minimums
        if promo.tier == 4:
            if met >= total:
                available.append(promo)
        # Tier 3 requires meeting most minimums
        elif promo.tier == 3:
            if total == 0 or met >= (total * 0.7):
                available.append(promo)
        # Tier 1–2 require meeting at least half
        else:
            if total == 0 or met >= (total * 0.5):
                available.append(promo)

    return available


def check_promotion_interest(wrestler, promotion_id):
    """Return an interest score (0-100) for how much a promotion wants the wrestler.

    Factors: skill match, popularity, backstage reputation, and whether
    the wrestler fits the promotion's style preferences.
    """
    promo = get_promotion(promotion_id)
    if promo is None:
        return 0

    score = 0.0

    # --- Skill match (up to 40 points) ---
    if promo.skill_minimums:
        skill_scores = []
        for skill, minimum in promo.skill_minimums.items():
            if skill == "popularity":
                value = wrestler.popularity
            else:
                value = wrestler.get_effective_skill(skill)
            # How far above the minimum are they?
            ratio = value / max(minimum, 1)
            skill_scores.append(min(ratio, 2.0))  # Cap at 2x the minimum
        avg = sum(skill_scores) / len(skill_scores)
        score += avg * 20  # 0–40
    else:
        score += 20  # No minimums: baseline interest

    # --- Popularity (up to 30 points) ---
    score += (wrestler.popularity / 100) * 30

    # --- Backstage reputation (up to 15 points, weighted by promotion) ---
    rep_normalized = (wrestler.backstage_rep + 100) / 200  # 0.0–1.0
    score += rep_normalized * 15 * promo.reputation_weight

    # --- Style fit (up to 15 points) ---
    if promo.style_preferences and wrestler.style_id:
        if wrestler.style_id in promo.style_preferences:
            score += 15
        else:
            score += 5  # Partial credit

    # --- Drug testing penalty ---
    if promo.drug_testing and wrestler.steroid_use:
        score -= 20

    # --- Overall rating bonus ---
    overall = wrestler.get_overall_rating()
    if overall >= 80:
        score += 10
    elif overall >= 60:
        score += 5

    return max(0, min(100, int(score)))
