"""Large pools of wrestling names for NPC generation."""

FIRST_NAMES = [
    # Classic American
    "Jake", "Tyler", "Marcus", "Brock", "Colt", "Ricky", "Shane", "Dean",
    "Seth", "Roman", "Finn", "Hector", "Damian", "Bobby", "Tommy", "Eddie",
    "Roderick", "Austin", "Kevin", "Mike", "Chris", "Matt", "Jeff", "Adam",
    "Jay", "Cody", "Dustin", "Lance", "Zack", "Dolph", "Elias", "Drew",
    "Shawn", "Hunter", "Randy", "Dave", "Steve", "Scott", "Rick", "Terry",
    "Bret", "Owen", "Ken", "Dan", "Taz", "Raven", "Rhino", "Sabu",
    # Stage / gimmick
    "Sting", "Vader", "Kane", "Luke", "Butch", "Haku", "Meng", "Konnan",
    # Lucha
    "Rey", "Juventud", "Psicosis", "Ultimo", "Lince", "Angel", "Santos",
    "Cruz", "Diego", "Victor", "Hugo", "Ivan", "Boris", "Nikolai",
    # Japanese
    "Akira", "Kenta", "Hiroshi", "Tetsuya", "Kazuchika", "Shingo",
    "Tomohiro", "Katsuyori", "Toru", "Minoru", "Jushin", "Tiger",
    # Modern / extra depth
    "Derek", "Brandon", "Caleb", "Donovan", "Eric", "Frank", "Grant",
    "Isaiah", "Jared", "Kyle", "Liam", "Nolan", "Patrick", "Quinn",
    "Rocco", "Sal", "Trevor", "Wade", "Xavier", "Zane",
    # Additional pool
    "Dominic", "Grayson", "Malakai", "Buddy", "Brodie", "Miro", "Andrade",
    "Claudio", "Cesaro", "Swerve", "Darby", "Jungle", "Luchasaurus", "Hook",
    "Wardlow", "Powerhouse", "Bron", "Carmelo", "Trick", "Wes",
    "Apollo", "Cedric", "Ricochet", "Mustafa", "Montez", "Angelo",
    "Braun", "Otis", "Chad", "Damon", "Erick", "Lars", "Riddick",
    "Sammy", "Trent", "Chuck", "Kip", "Nick", "Lee", "Dante",
    "Darius", "Tony", "Max", "Ace", "Blake", "Murphy", "Rowan",
]

LAST_NAMES = [
    # Tough / edgy
    "Steel", "Storm", "Stone", "Strong", "Steele", "Black", "Cross",
    "Drake", "Hart", "Hawk", "Wolf", "Fox", "Blaze", "Savage", "Bravo",
    "Knight", "King", "Cash", "Cage", "Cain", "Graves", "Rhodes",
    # Real-sounding
    "Lawler", "Michaels", "Johnson", "Williams", "Martinez", "Anderson",
    "Lee", "Walker", "Hall", "Young", "Allen", "Wright", "Lopez",
    "Carter", "Mitchell", "Rivera", "Morgan", "Reed", "Cooper",
    "Bailey", "Griffin", "Ward", "Torres", "Bennett", "Gray", "Price",
    # Over the top
    "Omega", "Alpha", "Fury", "Venom", "Havoc", "Mayhem", "Danger",
    "Razor", "Diesel", "Gunner", "Axe", "Hammer", "Bolt", "Crash",
    "Doom", "Thorn", "Frost", "Blitz", "Rush", "Riot", "Rogue",
    # Mythic / animal
    "Phoenix", "Dragon", "Viper", "Cobra", "Scorpion", "Panther",
    "Reaper", "Shadow", "Onyx", "Crimson", "Ivory", "Titan", "Atlas",
    "Orion", "Zenith", "Apex", "Rampage", "Thunder", "Voltage", "Magnum",
    # Lucha / international
    "Maximo", "Guerrero", "Lucha", "Dynamite", "Atomic", "Nitro", "Blaster",
    # Additional pool
    "Briggs", "Butcher", "Blade", "Starks", "Hobbs", "Strickland", "Takeshita",
    "Ospreay", "Kingston", "Moxley", "Danielson", "Okada", "Naito",
    "Suzuki", "Tanahashi", "Ibushi", "Goto", "Ishii", "Sabre",
    "Valentine", "Wyatt", "Rollins", "Ambrose", "Reigns", "Lesnar",
    "Orton", "Styles", "Nakamura", "Balor", "Owens", "Zayn",
    "Gresham", "Lethal", "Briscoe", "Castle", "Dalton", "Nemeth",
    "Cardona", "Jarrett", "Nash", "Waltman", "Helmsley", "Calaway",
]

NICKNAMES = [
    "The Natural", "The Prodigy", "The Machine", "The Ace", "The Beast",
    "The Chosen One", "The Phenom", "The Franchise", "The Icon", "The Legend",
    "The Destroyer", "The Hitman", "The Showstopper", "The Game",
    "The Viper", "The Architect", "The Lunatic", "The Big Dog",
    "The Monster", "The Demon", "The American Dream", "The American Nightmare",
    "The Technical Wizard", "The High Flyer", "The Hardcore King",
    "The Innovator of Violence", "The Cerebral Assassin", "The Rated-R Superstar",
    "The Phenomenal One", "The Kingslayer", "The Cleaner",
    "The Rainmaker", "The Ace of the Universe", "The Stone Pitbull",
    "Mr. Wrestling", "Mr. Perfect", "Dr. Death", "The Professor",
    "The Warrior", "The Enforcer", "The Giant Killer", "The Whole Damn Show",
    "The Human Suplex Machine", "The Rabid Wolverine", "The Crippler",
    "King of Strong Style", "The Best Bout Machine", "The Last Outlaw",
    "The Notorious", "The Untouchable",
    # Additional nicknames
    "The Tribal Chief", "The Visionary", "The Prize Fighter", "The Man",
    "The Boss", "The EST", "The Bruiserweight", "The Bastard",
    "The Dog of War", "The Cold-Hearted", "The Aerial Assassin",
    "The Spanish God", "The Redeemer", "The Blade Runner",
    "The Pain Maker", "The Switchblade", "The Undisputed",
    "The Alpha", "The Omega", "The Ace Crusher",
    "The Ring General", "The Head of the Table", "The Tribal Warrior",
    "The Submission Specialist", "The King of Flight", "The Innovator",
    "The Blackheart", "The Messiah", "The Savior", "The Purveyor of Violence",
]

# Ring name patterns: {first} {last}, {nickname} {last}, {first} "{nickname}" {last}, single name
RING_NAME_PATTERNS = [
    "{first} {last}",
    "{first} {last}",
    "{first} {last}",
    '{first} "{nickname}" {last}',
    "{nickname} {last}",
    "{last}",
    "The {last}",
    "{first} {last} Jr.",
]

# Tag team name parts for potential tag team generation
TAG_TEAM_PREFIXES = [
    "The", "Team", "Los", "New", "American", "World's Greatest",
]

TAG_TEAM_NAMES = [
    "Brothers of Destruction", "Midnight Express", "Road Warriors",
    "Dudley Boyz", "Hardy Boyz", "Edge and Christian", "Too Cool",
    "New Age Outlaws", "APA", "The Shield", "Evolution",
    "The Mega Powers", "The Rockers", "Demolition", "The Eliminators",
    "The Briscoes", "Young Bucks", "Motor City Machine Guns",
    "Beer Money", "Americas Most Wanted", "The Revival",
    "FTR", "The Acclaimed", "The Lucha Brothers", "Proud and Powerful",
    "The Usos", "New Day", "The Hurt Business", "Retribution",
    "Imperium", "Pretty Deadly", "Gallus", "Creed Brothers",
]

# Finisher name components for random generation
FINISHER_VERBS = [
    "Death", "Burning", "Spinning", "Flying", "Devastating", "Super",
    "Mega", "Ultra", "Atomic", "Electric", "Thunder", "Lightning",
    "Crushing", "Bone-Breaking", "Skull-Crushing", "Earth-Shattering",
    "Final", "Ultimate", "Extreme", "Savage", "Brutal",
    "Vicious", "Wicked", "Hellacious", "Merciless", "Relentless",
    "Rising", "Falling", "Twisting", "Inverted", "Modified",
]

FINISHER_NOUNS = [
    "Driver", "Bomb", "Buster", "Slam", "DDT", "Cutter", "Lock",
    "Clutch", "Piledriver", "Suplex", "Powerbomb", "Splash",
    "Elbow", "Lariat", "Kick", "Knee", "Moonsault", "Destroyer",
    "Stunner", "Drop", "Breaker", "Plunge", "Impact", "Hammer",
    "Crush", "Press", "Crossface", "Armbar", "Choke", "Submission",
    "Tombstone", "Rainmaker", "Rainbreaker", "Backbreaker", "Neckbreaker",
    "Brainbuster", "Tiger Driver", "Burning Hammer", "Vertebreaker",
    "Canadian Destroyer", "One Winged Angel", "Paradigm Shift",
]
