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
    'Kanda': 'can',  # častý překlep
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

# IIHF / ISO 3 písmena (název týmu v DB jen jako kód)
IIHF_CODE_TO_FILE = {
    'CZE': 'cze',
    'SVK': 'svk',
    'SUI': 'sui',
    'FIN': 'fin',
    'USA': 'usa',
    'SWE': 'swe',
    'LAT': 'lat',
    'CAN': 'can',
    'GER': 'ger',
    'AUT': 'aut',
    'NOR': 'nor',
    'DEN': 'den',
    'FRA': 'fra',
    'ITA': 'ita',
    'KAZ': 'kaz',
    'POL': 'pol',
    'UKR': 'ukr',
    'GBR': 'gbr',
    'SVN': 'svn',
    'HUN': 'hun',
    'JPN': 'jpn',
    'KOR': 'kor',
    'CHN': 'chn',
    'RUS': 'rus',
    'BLR': 'blr',
}

# Zobrazení v UI, když je v DB jen třípísmenný kód (FIN, CZE, …)
IIHF_CODE_TO_DISPLAY_CZ = {
    'CZE': 'Česko',
    'SVK': 'Slovensko',
    'SUI': 'Švýcarsko',
    'FIN': 'Finsko',
    'USA': 'USA',
    'SWE': 'Švédsko',
    'LAT': 'Lotyšsko',
    'CAN': 'Kanada',
    'GER': 'Německo',
    'AUT': 'Rakousko',
    'NOR': 'Norsko',
    'DEN': 'Dánsko',
    'FRA': 'Francie',
    'ITA': 'Itálie',
    'KAZ': 'Kazachstán',
    'POL': 'Polsko',
    'UKR': 'Ukrajina',
    'GBR': 'Velká Británie',
    'SVN': 'Slovinsko',
    'HUN': 'Maďarsko',
    'JPN': 'Japonsko',
    'KOR': 'Jižní Korea',
    'CHN': 'Čína',
    'RUS': 'Rusko',
    'BLR': 'Bělorusko',
}


def get_team_display_label(team_name: str) -> str:
    """Český dlouhý název pro známý třípísmenný kód; jinak vrátí původní řetězec z DB."""
    if not team_name or not isinstance(team_name, str):
        return team_name or ''
    s = team_name.strip()
    if not s:
        return ''
    if len(s) == 3 and s.isalpha():
        return IIHF_CODE_TO_DISPLAY_CZ.get(s.upper(), s)
    return s


# Normalize for lookup: strip whitespace, optional case-insensitive
def get_team_flag_shortcut(team_name):
    """Return 3-letter shortcut for flag filename, or None if not in mapping."""
    if not team_name or not isinstance(team_name, str):
        return None
    key = team_name.strip()
    if key in TEAM_NAME_TO_SHORTCUT:
        return TEAM_NAME_TO_SHORTCUT[key]
    # Přesně třípísmenný kód (LAT, CZE, …)
    if len(key) == 3 and key.isalpha():
        k3 = key.upper()
        if k3 in IIHF_CODE_TO_FILE:
            return IIHF_CODE_TO_FILE[k3]
    # Case-insensitive fallback na dlouhé názvy
    for name, code in TEAM_NAME_TO_SHORTCUT.items():
        if name.lower() == key.lower():
            return code
    return None
