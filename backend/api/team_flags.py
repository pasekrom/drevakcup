"""
IIHF team name (Czech/long) to official 3-letter shortcut mapping.
Used to resolve bundled flag filenames: {shortcut}.png in api/static/team_flags/
"""
# Czech long name (or common name) -> IIHF code (lowercase for filename)
TEAM_NAME_TO_SHORTCUT = {
    # Common Czech names
    'Česko': 'cze',
    'Česká republika': 'cze',
    'Kanada': 'can',
    'Canada': 'can',
    'Švédsko': 'swe',
    'Sweden': 'swe',
    'Finsko': 'fin',
    'Finland': 'fin',
    'Rusko': 'rus',
    'Russia': 'rus',
    'USA': 'usa',
    'Spojené státy': 'usa',
    'Slovensko': 'svk',
    'Slovakia': 'svk',
    'Německo': 'ger',
    'Germany': 'ger',
    'Švýcarsko': 'sui',
    'Switzerland': 'sui',
    'Rakousko': 'aut',
    'Austria': 'aut',
    'Norsko': 'nor',
    'Norway': 'nor',
    'Dánsko': 'den',
    'Denmark': 'den',
    'Lotyšsko': 'lat',
    'Latvia': 'lat',
    'Bělorusko': 'blr',
    'Belarus': 'blr',
    'Francie': 'fra',
    'France': 'fra',
    'Itálie': 'ita',
    'Italy': 'ita',
    'Kazachstán': 'kaz',
    'Kazakhstan': 'kaz',
    'Polsko': 'pol',
    'Poland': 'pol',
    'Ukrajina': 'ukr',
    'Ukraine': 'ukr',
    'Velká Británie': 'gbr',
    'Great Britain': 'gbr',
    'Slovinsko': 'svn',
    'Slovenia': 'svn',
    'Maďarsko': 'hun',
    'Hungary': 'hun',
    'Japonsko': 'jpn',
    'Japan': 'jpn',
    'Jižní Korea': 'kor',
    'Korea': 'kor',
    'South Korea': 'kor',
    'Čína': 'chn',
    'China': 'chn',
}

# Normalize for lookup: strip whitespace, optional case-insensitive
def get_team_flag_shortcut(team_name):
    """Return 3-letter shortcut for flag filename, or None if not in mapping."""
    if not team_name or not isinstance(team_name, str):
        return None
    key = team_name.strip()
    if key in TEAM_NAME_TO_SHORTCUT:
        return TEAM_NAME_TO_SHORTCUT[key]
    # Case-insensitive fallback
    for name, code in TEAM_NAME_TO_SHORTCUT.items():
        if name.lower() == key.lower():
            return code
    return None
