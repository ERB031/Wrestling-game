"""Wrestler class - the central data model for player and NPCs."""

import random
from dataclasses import dataclass, field
from data.constants import SKILLS, SKILL_DEFAULT, SKILL_MIN, SKILL_MAX


@dataclass
class Injury:
    body_part: str
    severity: int  # 1-4
    description: str
    weeks_remaining: int
    chronic: bool = False
    stat_penalties: dict = field(default_factory=dict)

    def to_dict(self):
        return {
            "body_part": self.body_part,
            "severity": self.severity,
            "description": self.description,
            "weeks_remaining": self.weeks_remaining,
            "chronic": self.chronic,
            "stat_penalties": self.stat_penalties,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


@dataclass
class Wrestler:
    real_name: str = ""
    ring_name: str = ""
    age: int = 22
    backstory_id: str = ""
    style_id: str = ""

    # Skills (1-100)
    skills: dict = field(default_factory=lambda: {s: SKILL_DEFAULT for s in SKILLS})
    skill_xp: dict = field(default_factory=lambda: {s: 0 for s in SKILLS})

    # Derived / status
    health: int = 100
    alignment: int = 0  # -100 to +100
    booked_alignment: int = 0  # What the promotion wants
    popularity: int = 5
    backstage_rep: int = 0
    momentum: int = 0  # -10 to +10, current push level
    money: int = 500

    # Combat record
    wins: int = 0
    losses: int = 0
    draws: int = 0

    # Body damage (0-100 per part, accumulated over career)
    body_damage: dict = field(default_factory=lambda: {
        "head": 0, "neck": 0, "back": 0,
        "left_knee": 0, "right_knee": 0,
        "left_shoulder": 0, "right_shoulder": 0,
        "ribs": 0, "wrist": 0,
    })

    # Active injuries
    injuries: list = field(default_factory=list)

    # Lifestyle / addiction (0-100)
    alcohol_level: int = 0
    painkiller_level: int = 0
    drug_level: int = 0
    steroid_use: bool = False
    steroid_cumulative: int = 0  # Lifetime weeks on steroids
    relationship_status: str = "single"  # single, dating, relationship, married
    relationship_partner: str = ""
    relationship_health: int = 0
    burnout: int = 0

    # Career
    current_promotion: str = ""
    contract_weeks_remaining: int = 0
    titles_held: list = field(default_factory=list)
    career_titles: list = field(default_factory=list)  # Historical
    career_promotions: list = field(default_factory=list)
    finisher_name: str = ""
    signature_moves: list = field(default_factory=list)
    entrance_style: str = ""

    # Relationships with NPCs: {npc_id: score}
    relationships: dict = field(default_factory=dict)

    # Flags
    is_player: bool = False
    is_retired: bool = False
    is_dead: bool = False
    personality: str = ""  # For NPCs: politician, workrate_junkie, partier, mentor, bully, etc.

    # Career stats
    total_matches: int = 0
    best_match_rating: float = 0.0
    total_earnings: int = 0
    peak_popularity: int = 0
    weeks_as_champion: int = 0

    # CTE / concussion tracking
    concussion_count: int = 0       # Lifetime concussions
    cte_severity: int = 0           # 0-100, accumulated brain damage
    weeks_since_concussion: int = 99  # Weeks since last concussion (high = safe)

    # Business / merch
    merch_level: int = 0            # 0-5: none, basic, standard, premium, deluxe, empire
    merch_cut_pct: int = 0          # % of merch revenue player keeps (0-100)
    social_media_followers: int = 0 # Influences merch sales and appearance fees
    appearance_fee: int = 0         # Per-appearance income outside matches
    brand_deals: list = field(default_factory=list)  # Active endorsement deals
    merch_income_total: int = 0     # Lifetime merch earnings
    business_investments: list = field(default_factory=list)  # Investments like gym, school, etc.

    # NPC id
    npc_id: str = ""

    def get_effective_skill(self, skill_name):
        """Get skill value after injury penalties and substance effects."""
        base = self.skills.get(skill_name, 0)

        # Injury penalties
        for injury in self.injuries:
            penalty = injury.stat_penalties.get(skill_name, 0)
            base -= penalty

        # Steroid boost
        if self.steroid_use:
            from data.constants import STEROID_LIGHT_BOOST
            base += STEROID_LIGHT_BOOST.get(skill_name, 0)

        # Alcohol penalty (if high)
        if self.alcohol_level > 50:
            if skill_name in ("in_ring", "athleticism", "psychology"):
                base -= (self.alcohol_level - 50) // 10

        # Painkiller effects
        if self.painkiller_level > 60:
            if skill_name in ("in_ring", "psychology", "charisma"):
                base -= (self.painkiller_level - 60) // 15

        # Drug effects
        if self.drug_level > 50:
            if skill_name in ("in_ring", "athleticism", "psychology"):
                base -= (self.drug_level - 50) // 10

        # Burnout penalty
        if self.burnout > 70:
            base -= (self.burnout - 70) // 10

        # CTE degradation (permanent)
        if self.cte_severity > 30:
            if skill_name in ("in_ring", "psychology", "charisma", "mic_work"):
                base -= (self.cte_severity - 30) // 10

        return max(SKILL_MIN, min(SKILL_MAX, base))

    def get_overall_rating(self):
        """Calculate overall wrestler rating."""
        weights = {
            "in_ring": 1.5,
            "psychology": 1.2,
            "charisma": 1.0,
            "mic_work": 1.0,
            "athleticism": 0.8,
            "power": 0.7,
            "durability": 0.8,
            "look": 0.8,
            "violence": 0.5,
        }
        total = sum(self.get_effective_skill(s) * w for s, w in weights.items())
        max_total = sum(100 * w for w in weights.values())
        return int((total / max_total) * 100)

    def add_skill_xp(self, skill_name, amount):
        """Add XP to a skill, potentially leveling up."""
        from data.constants import XP_BASE, XP_GROWTH_FACTOR
        current = self.skills.get(skill_name, SKILL_DEFAULT)
        if current >= SKILL_MAX:
            return False

        self.skill_xp[skill_name] = self.skill_xp.get(skill_name, 0) + amount
        xp_needed = int(XP_BASE * (XP_GROWTH_FACTOR ** current))

        leveled = False
        while self.skill_xp[skill_name] >= xp_needed and self.skills[skill_name] < SKILL_MAX:
            self.skill_xp[skill_name] -= xp_needed
            self.skills[skill_name] += 1
            leveled = True
            xp_needed = int(XP_BASE * (XP_GROWTH_FACTOR ** self.skills[skill_name]))

        return leveled

    def is_injured(self):
        """Check if wrestler has any active non-chronic injuries."""
        return any(not i.chronic or i.weeks_remaining > 0 for i in self.injuries)

    def can_wrestle(self):
        """Check if wrestler is healthy enough to compete."""
        severe = [i for i in self.injuries if i.severity >= 3 and i.weeks_remaining > 0]
        return len(severe) == 0 and self.health > 10 and not self.is_dead and not self.is_retired

    def heal_week(self):
        """Process one week of healing."""
        # Natural health recovery
        if self.health < 100:
            recovery = random.randint(5, 15)
            if self.steroid_use:
                recovery = int(recovery * 1.3)
            self.health = min(100, self.health + recovery)

        # Injury recovery
        still_injured = []
        for injury in self.injuries:
            if injury.weeks_remaining > 0:
                injury.weeks_remaining -= 1
            if injury.weeks_remaining > 0 or injury.chronic:
                still_injured.append(injury)
        self.injuries = still_injured

        # Body damage slow decay
        for part in self.body_damage:
            if self.body_damage[part] > 0:
                self.body_damage[part] = max(0, self.body_damage[part] - random.uniform(0.1, 0.5))

        # Track weeks since last concussion
        self.weeks_since_concussion = min(999, self.weeks_since_concussion + 1)

    def to_dict(self):
        """Serialize to dict for saving."""
        data = {}
        for key, value in self.__dict__.items():
            if key == "injuries":
                data[key] = [i.to_dict() for i in value]
            else:
                data[key] = value
        return data

    @classmethod
    def from_dict(cls, data):
        """Deserialize from dict."""
        injuries_data = data.pop("injuries", [])
        wrestler = cls(**data)
        wrestler.injuries = [Injury.from_dict(i) for i in injuries_data]
        return wrestler

    def __str__(self):
        return f'{self.ring_name} (OVR: {self.get_overall_rating()})'
