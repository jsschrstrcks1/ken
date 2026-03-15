#!/usr/bin/env python3
"""Build tz-cities file from whatsinport port-country mapping."""

import re

# Country to IANA timezone mapping
# For countries spanning multiple timezones, we pick the most common cruise port timezone
COUNTRY_TZ = {
    # Americas
    "United States": "America/New_York",  # default, overridden per port
    "Canada": "America/Toronto",  # default, overridden per port
    "Mexico": "America/Mexico_City",  # default, overridden per port
    "Bahamas": "America/Nassau",
    "Jamaica": "America/Jamaica",
    "Cuba": "America/Havana",
    "Dominican Republic": "America/Santo_Domingo",
    "Puerto Rico": "America/Puerto_Rico",
    "US Virgin Islands": "America/Virgin",
    "British Virgin Islands": "America/Tortola",
    "Antigua and Barbuda": "America/Antigua",
    "Saint Kitts and Nevis": "America/St_Kitts",
    "Saint Lucia": "America/St_Lucia",
    "Barbados": "America/Barbados",
    "Grenada": "America/Grenada",
    "Saint Vincent and the Grenadines": "America/St_Vincent",
    "Trinidad and Tobago": "America/Port_of_Spain",
    "Dominica": "America/Dominica",
    "Martinique": "America/Martinique",
    "Guadeloupe": "America/Guadeloupe",
    "Aruba": "America/Aruba",
    "Curacao": "America/Curacao",
    "Bonaire": "America/Kralendijk",
    "Sint Maarten": "America/Lower_Princes",
    "Saint Martin": "America/Marigot",
    "Cayman Islands": "America/Cayman",
    "Turks and Caicos Islands": "America/Grand_Turk",
    "Bermuda": "Atlantic/Bermuda",
    "Haiti": "America/Port-au-Prince",
    "Belize": "America/Belize",
    "Guatemala": "America/Guatemala",
    "Honduras": "America/Tegucigalpa",
    "El Salvador": "America/El_Salvador",
    "Nicaragua": "America/Managua",
    "Costa Rica": "America/Costa_Rica",
    "Panama": "America/Panama",
    "Colombia": "America/Bogota",
    "Venezuela": "America/Caracas",
    "Ecuador": "America/Guayaquil",
    "Peru": "America/Lima",
    "Chile": "America/Santiago",
    "Argentina": "America/Argentina/Buenos_Aires",
    "Uruguay": "America/Montevideo",
    "Brazil": "America/Sao_Paulo",
    "Suriname": "America/Paramaribo",
    "French Guiana": "America/Cayenne",
    "Falkland Islands": "Atlantic/Stanley",
    "Saint Pierre and Miquelon": "America/Miquelon",
    "Montserrat": "America/Montserrat",
    "Anguilla": "America/Anguilla",
    "Saint Barthelemy": "America/St_Barthelemy",
    "Saba": "America/Lower_Princes",
    "Barbuda": "America/Antigua",

    # Europe
    "United Kingdom": "Europe/London",
    "Ireland": "Europe/Dublin",
    "France": "Europe/Paris",
    "Spain": "Europe/Madrid",
    "Portugal": "Europe/Lisbon",
    "Italy": "Europe/Rome",
    "Greece": "Europe/Athens",
    "Turkey": "Europe/Istanbul",
    "Croatia": "Europe/Zagreb",
    "Montenegro": "Europe/Podgorica",
    "Albania": "Europe/Tirane",
    "Slovenia": "Europe/Ljubljana",
    "Malta": "Europe/Malta",
    "Cyprus": "Asia/Nicosia",
    "Monaco": "Europe/Monaco",
    "Gibraltar": "Europe/Gibraltar",
    "Netherlands": "Europe/Amsterdam",
    "Belgium": "Europe/Brussels",
    "Germany": "Europe/Berlin",
    "Denmark": "Europe/Copenhagen",
    "Sweden": "Europe/Stockholm",
    "Norway": "Europe/Oslo",
    "Finland": "Europe/Helsinki",
    "Estonia": "Europe/Tallinn",
    "Latvia": "Europe/Riga",
    "Lithuania": "Europe/Vilnius",
    "Poland": "Europe/Warsaw",
    "Romania": "Europe/Bucharest",
    "Bulgaria": "Europe/Sofia",
    "Serbia": "Europe/Belgrade",
    "Hungary": "Europe/Budapest",
    "Slovakia": "Europe/Bratislava",
    "Czech Republic": "Europe/Prague",
    "Austria": "Europe/Vienna",
    "Switzerland": "Europe/Zurich",
    "Russia": "Europe/Moscow",
    "Ukraine": "Europe/Kiev",
    "Georgia": "Asia/Tbilisi",
    "Iceland": "Atlantic/Reykjavik",
    "Faroe Islands": "Atlantic/Faroe",
    "Svalbard": "Arctic/Longyearbyen",
    "Greenland": "America/Godthab",
    "Isle of Man": "Europe/Isle_of_Man",
    "Guernsey": "Europe/Guernsey",
    "Jersey": "Europe/Jersey",
    "Moldova": "Europe/Chisinau",

    # Middle East
    "Israel": "Asia/Jerusalem",
    "Jordan": "Asia/Amman",
    "Lebanon": "Asia/Beirut",
    "Saudi Arabia": "Asia/Riyadh",
    "United Arab Emirates": "Asia/Dubai",
    "Oman": "Asia/Muscat",
    "Qatar": "Asia/Qatar",
    "Bahrain": "Asia/Bahrain",
    "Kuwait": "Asia/Kuwait",
    "Iran": "Asia/Tehran",
    "Iraq": "Asia/Baghdad",
    "Syria": "Asia/Damascus",
    "Egypt": "Africa/Cairo",
    "Yemen": "Asia/Aden",

    # Africa
    "Morocco": "Africa/Casablanca",
    "Tunisia": "Africa/Tunis",
    "Algeria": "Africa/Algiers",
    "Libya": "Africa/Tripoli",
    "Senegal": "Africa/Dakar",
    "Gambia": "Africa/Banjul",
    "Guinea-Bissau": "Africa/Bissau",
    "Guinea": "Africa/Conakry",
    "Ivory Coast": "Africa/Abidjan",
    "Ghana": "Africa/Accra",
    "Togo": "Africa/Lome",
    "Benin": "Africa/Porto-Novo",
    "Nigeria": "Africa/Lagos",
    "Cameroon": "Africa/Douala",
    "Gabon": "Africa/Libreville",
    "Republic of the Congo": "Africa/Brazzaville",
    "Angola": "Africa/Luanda",
    "Namibia": "Africa/Windhoek",
    "South Africa": "Africa/Johannesburg",
    "Mozambique": "Africa/Maputo",
    "Tanzania": "Africa/Dar_es_Salaam",
    "Kenya": "Africa/Nairobi",
    "Madagascar": "Indian/Antananarivo",
    "Mauritius": "Indian/Mauritius",
    "Reunion": "Indian/Reunion",
    "Seychelles": "Indian/Mahe",
    "Comoros": "Indian/Comoro",
    "Mayotte": "Indian/Mayotte",
    "Zanzibar": "Africa/Dar_es_Salaam",
    "Cape Verde": "Atlantic/Cape_Verde",
    "Sao Tome and Principe": "Africa/Sao_Tome",
    "Mauritania": "Africa/Nouakchott",
    "Saint Helena": "Atlantic/St_Helena",

    # Asia
    "India": "Asia/Kolkata",
    "Sri Lanka": "Asia/Colombo",
    "Maldives": "Indian/Maldives",
    "Thailand": "Asia/Bangkok",
    "Vietnam": "Asia/Ho_Chi_Minh",
    "Cambodia": "Asia/Phnom_Penh",
    "Myanmar": "Asia/Yangon",
    "Malaysia": "Asia/Kuala_Lumpur",
    "Singapore": "Asia/Singapore",
    "Indonesia": "Asia/Jakarta",
    "Philippines": "Asia/Manila",
    "Brunei": "Asia/Brunei",
    "Taiwan": "Asia/Taipei",
    "South Korea": "Asia/Seoul",
    "Japan": "Asia/Tokyo",
    "China": "Asia/Shanghai",
    "Hong Kong": "Asia/Hong_Kong",
    "Pakistan": "Asia/Karachi",
    "East Timor": "Asia/Dili",

    # Oceania
    "Australia": "Australia/Sydney",  # default, overridden per port
    "New Zealand": "Pacific/Auckland",
    "Fiji": "Pacific/Fiji",
    "Papua New Guinea": "Pacific/Port_Moresby",
    "Solomon Islands": "Pacific/Guadalcanal",
    "Vanuatu": "Pacific/Efate",
    "New Caledonia": "Pacific/Noumea",
    "Tonga": "Pacific/Tongatapu",
    "Samoa": "Pacific/Apia",
    "American Samoa": "Pacific/Pago_Pago",
    "Cook Islands": "Pacific/Rarotonga",
    "French Polynesia": "Pacific/Tahiti",
    "Guam": "Pacific/Guam",
    "Palau": "Pacific/Palau",
    "Micronesia": "Pacific/Chuuk",
    "Marshall Islands": "Pacific/Majuro",
    "Kiribati": "Pacific/Tarawa",
    "Tuvalu": "Pacific/Funafuti",
    "Niue": "Pacific/Niue",
    "Norfolk Island": "Pacific/Norfolk",
    "Pitcairn Islands": "Pacific/Pitcairn",
    "Saipan": "Pacific/Guam",
    "Northern Mariana Islands": "Pacific/Guam",
    "Chatham Islands": "Pacific/Chatham",

    # Atlantic
    "Azores": "Atlantic/Azores",
    "Canary Islands": "Atlantic/Canary",
    "Madeira": "Atlantic/Madeira",

    # Antarctica
    "Antarctica": "Antarctica/Palmer",
    "South Georgia": "Atlantic/South_Georgia",
}

# Specific port timezone overrides (for countries with multiple timezones)
PORT_TZ_OVERRIDES = {
    # US West Coast
    "Los-Angeles": "America/Los_Angeles",
    "San-Francisco": "America/Los_Angeles",
    "San-Diego": "America/Los_Angeles",
    "Monterey-California": "America/Los_Angeles",
    "Santa-Barbara-CA": "America/Los_Angeles",
    "Santa-Catalina-Island": "America/Los_Angeles",
    "Seattle": "America/Los_Angeles",
    "Astoria-Oregon": "America/Los_Angeles",
    "Portland-us": "America/Los_Angeles",
    "Vancouver-us": "America/Los_Angeles",
    "Clarkston-us": "America/Los_Angeles",
    "Burbank-us": "America/Los_Angeles",
    "Richland-us": "America/Los_Angeles",
    "Stevenson-us": "America/Los_Angeles",
    "Camas-Washougal-us": "America/Los_Angeles",
    "Kalama-us": "America/Los_Angeles",
    "The_Dallas-us": "America/Los_Angeles",
    "Rainier-us": "America/Los_Angeles",
    # US Alaska
    "Anchorage-Whittier-AK": "America/Anchorage",
    "Haines-AK": "America/Anchorage",
    "Juneau-AK": "America/Anchorage",
    "Ketchikan-AK": "America/Anchorage",
    "Sitka-AK": "America/Anchorage",
    "Skagway-AK": "America/Anchorage",
    "Seward-AK": "America/Anchorage",
    "Kodiak-AK": "America/Anchorage",
    "Icy-Strait-Point-AK": "America/Anchorage",
    "Homer": "America/Anchorage",
    "Wrangell": "America/Anchorage",
    "Tracy-Arm-Fjord-AK": "America/Anchorage",
    "Valdez-AK": "America/Anchorage",
    "Nome-AK": "America/Nome",
    "Dutch-Harbor-Unalaska-Island": "America/Adak",
    "Barrow-AK": "America/Anchorage",
    "Point-Hope-AK": "America/Anchorage",
    "Klawock": "America/Anchorage",
    # US Hawaii
    "Honolulu-Oahu-Hawaii": "Pacific/Honolulu",
    "Hilo-Hawaii": "Pacific/Honolulu",
    "Kahului-Maui-Hawaii": "Pacific/Honolulu",
    "Kona-Hawaii": "Pacific/Honolulu",
    "Lahaina-Maui-Hawaii": "Pacific/Honolulu",
    "Nawiliwili-Kauai-Hawaii": "Pacific/Honolulu",
    # US Gulf Coast
    "Galveston-Texas": "America/Chicago",
    "New-Orleans": "America/Chicago",
    "New_Orleans-us": "America/Chicago",
    "Mobile": "America/Chicago",
    "Houston": "America/Chicago",
    # US Mississippi River
    "Red_Wing_MN-us": "America/Chicago",
    "Winona_MN-us": "America/Chicago",
    "La_Crosse_WI-us": "America/Chicago",
    "Dubuque_IA-us": "America/Chicago",
    "Clinton_IA-us": "America/Chicago",
    "Davenport_IA-us": "America/Chicago",
    "Hannibal_MO-us": "America/Chicago",
    "Alton_IL-us": "America/Chicago",
    "St_Louis_MO-us": "America/Chicago",
    "Kimmswick_MO-us": "America/Chicago",
    "Chester_IL-us": "America/Chicago",
    "Cape_Girardeau_MO-us": "America/Chicago",
    "Columbus_KY-us": "America/Chicago",
    "New_Madrid_MO-us": "America/Chicago",
    "Memphis_TN-us": "America/Chicago",
    "Tunica_MS-us": "America/Chicago",
    "Helena-West_Helena-us": "America/Chicago",
    "Rosedale_MS-us": "America/Chicago",
    "Greenville_MS-us": "America/Chicago",
    "Vicksburg_MS-us": "America/Chicago",
    "Natchez_MS-us": "America/Chicago",
    "St_Francisville_LA-us": "America/Chicago",
    "Baton_Rouge-us": "America/Chicago",
    "Nottowy_Plantation-us": "America/Chicago",
    "Houmas_House_Plantation-us": "America/Chicago",
    "Oak_Alley_Plantation-us": "America/Chicago",
    # US Hudson River
    "Troy-us": "America/New_York",
    "Albany-us": "America/New_York",
    "Catskill-us": "America/New_York",
    "Kingston-us": "America/New_York",
    "Hyde_Park-us": "America/New_York",
    "West-Point-us": "America/New_York",
    "Sleepy_Hollow-us": "America/New_York",
    "New_York_City-us": "America/New_York",
    # Canada West Coast
    "Vancouver": "America/Vancouver",
    "Victoria-BC": "America/Vancouver",
    "Nanaimo": "America/Vancouver",
    "Prince-Rupert-British-Columbia": "America/Vancouver",
    "Alert-Bay-BC": "America/Vancouver",
    # Canada East
    "Montreal": "America/Toronto",
    "Quebec": "America/Toronto",
    "Halifax": "America/Halifax",
    "Sydney-Cape-Breton-Island": "America/Halifax",
    "Charlottetown-Prince-Edward-Island": "America/Halifax",
    "Saint-John-New-Brunswick": "America/Halifax",
    "Saint-Johns-Newfoundland": "America/St_Johns",
    "Corner-Brook-Newfoundland": "America/St_Johns",
    "Saint-Anthony-Newfoundland": "America/St_Johns",
    "Baddeck-Cape-Breton-Island": "America/Halifax",
    "Gaspe": "America/Toronto",
    "Baie-Comeau": "America/Toronto",
    "Sept-Iles": "America/Toronto",
    "Trois-Rivieres": "America/Toronto",
    "Red-Bay-Labrador": "America/Halifax",
    # Mexico overrides
    "Ensenada": "America/Tijuana",
    "Cabo-San-Lucas": "America/Mazatlan",
    "Mazatlan": "America/Mazatlan",
    "Puerto-Vallarta": "America/Bahia_Banderas",
    "Manzanillo": "America/Mexico_City",
    "Acapulco": "America/Mexico_City",
    "Huatulco": "America/Mexico_City",
    "Zihuatanejo-Ixtapa": "America/Mexico_City",
    "Puerto-Chiapas": "America/Mexico_City",
    "Cozumel": "America/Cancun",
    "Costa-Maya": "America/Cancun",
    "Playa-del-Carmen": "America/Cancun",
    "Calica": "America/Cancun",
    "Progreso": "America/Merida",
    "La-Paz": "America/Mazatlan",
    "Loreto": "America/Mazatlan",
    # Australia overrides
    "Darwin": "Australia/Darwin",
    "Broome": "Australia/Perth",
    "Fremantle": "Australia/Perth",
    "Perth": "Australia/Perth",
    "Bunbury": "Australia/Perth",
    "Busselton": "Australia/Perth",
    "Esperance": "Australia/Perth",
    "Geraldton": "Australia/Perth",
    "Port-Hedland": "Australia/Perth",
    "Exmouth": "Australia/Perth",
    "Albany": "Australia/Perth",
    "Margaret-River": "Australia/Perth",
    "Adelaide": "Australia/Adelaide",
    "Kangaroo-Island": "Australia/Adelaide",
    "Port-Lincoln": "Australia/Adelaide",
    "Penneshaw": "Australia/Adelaide",
    "Robe": "Australia/Adelaide",
    "Melbourne": "Australia/Melbourne",
    "Geelong": "Australia/Melbourne",
    "Portland-AU": "Australia/Melbourne",
    "Phillip-Island": "Australia/Melbourne",
    "Hobart-Tasmania": "Australia/Hobart",
    "Burnie-Tasmania": "Australia/Hobart",
    "Devonport-Tasmania": "Australia/Hobart",
    "Port-Arthur-Tasmania": "Australia/Hobart",
    "Launceston-Tasmania": "Australia/Hobart",
    "Brisbane": "Australia/Brisbane",
    "Mooloolaba": "Australia/Brisbane",
    "Gladstone": "Australia/Brisbane",
    "Cairns": "Australia/Brisbane",
    "Townsville": "Australia/Brisbane",
    "Airlie-Beach": "Australia/Brisbane",
    # Indonesia overrides
    "Bali": "Asia/Makassar",
    "Komodo": "Asia/Makassar",
    "Lombok": "Asia/Makassar",
    "Kupang": "Asia/Makassar",
    "Semarang": "Asia/Jakarta",
    "Surabaya": "Asia/Jakarta",
    # Russia
    "Vladivostok": "Asia/Vladivostok",
    # Canary Islands (Spain but different timezone)
    "Las-Palmas-Gran-Canaria": "Atlantic/Canary",
    "Santa-Cruz-Tenerife": "Atlantic/Canary",
    "Los-Cristianos-Tenerife": "Atlantic/Canary",
    "Arrecife-Lanzarote": "Atlantic/Canary",
    "Puerto-del-Rosario-Fuerteventura": "Atlantic/Canary",
    "El-Hierro": "Atlantic/Canary",
    "San-Sebastian-Gomera": "Atlantic/Canary",
    "Santa-Cruz-La-Palma": "Atlantic/Canary",
    # Azores (Portugal but different timezone)
    "Ponta-Delgada-Sao-Miguel": "Atlantic/Azores",
    "Horta-Faial-Island": "Atlantic/Azores",
    "Praia-da-Victoria-Terceira": "Atlantic/Azores",
    "Santa-Cruz-das-Flores": "Atlantic/Azores",
    # Madeira
    "Funchal-Madeira": "Atlantic/Madeira",
    "Porto-Santo-Island": "Atlantic/Madeira",
    # Easter Island
    "Easter-Island": "Pacific/Easter",
    "Hangaroa": "Pacific/Easter",
    "Anakena-Beach": "Pacific/Easter",
    # Galapagos
    "Galapagos": "Pacific/Galapagos",
}


def slug_to_name(slug):
    """Convert URL slug to readable name."""
    # Remove country suffixes like -fr, -de, -at, etc.
    name = re.sub(r'-[a-z]{2}$', '', slug)
    return name.replace('-', ' ').replace('_', ' ')


def generate_variants(slug, name):
    """Generate fuzzy matching variants for a port name."""
    variants = set()

    # Full name lowercase with spaces
    full = name.lower()
    variants.add(full)

    # Hyphenated version
    hyphenated = slug.lower()
    variants.add(hyphenated)

    # Without country qualifiers
    # Remove things like "-Scotland", "-Sicily", "-Corsica", etc.
    qualifiers = [
        'scotland', 'sicily', 'corsica', 'sardinia', 'crete', 'wales',
        'jamaica', 'antigua', 'dominica', 'papoea', 'sulawesi', 'sumatra',
        'java', 'flores', 'tasmania', 'oregon', 'california', 'texas',
        'florida', 'maine', 'rhode island', 'virginia', 'delaware',
        'prince edward island', 'new brunswick', 'newfoundland', 'labrador',
        'cape breton island', 'british columbia', 'nova scotia',
        'baffin island', 'isle of wight', 'isle of man',
    ]

    for q in qualifiers:
        pattern = re.compile(r'\s+' + re.escape(q) + r'$', re.I)
        shortened = pattern.sub('', full)
        if shortened != full:
            variants.add(shortened)
        pattern2 = re.compile(r'-' + re.escape(q.replace(' ', '-')) + r'$', re.I)
        shortened2 = pattern2.sub('', hyphenated)
        if shortened2 != hyphenated:
            variants.add(shortened2)

    # Short name (first word if multi-word, and it's somewhat unique)
    words = full.split()
    if len(words) >= 2:
        # Add short forms for well-known ports
        first = words[0]
        if first not in ('port', 'saint', 'san', 'la', 'le', 'el', 'los',
                         'las', 'new', 'great', 'fort', 'cape', 'old',
                         'mount', 'isle', 'ile', 'puerto', 'costa',
                         'boca', 'bay', 'east', 'west', 'south', 'north'):
            variants.add(first)

    return variants


def main():
    # Read port-country mapping
    ports = []
    with open('/home/user/ken/whatsinport_port_country_map.txt') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split('|', 1)
            if len(parts) == 2:
                ports.append((parts[0], parts[1]))

    # Also get all port slugs from the filtered list for any we missed
    extra_slugs = set()
    try:
        with open('/home/user/ken/whatsinport_ports_filtered.txt') as f:
            for line in f:
                slug = line.strip()
                if slug:
                    extra_slugs.add(slug)
    except FileNotFoundError:
        pass

    # Build the mapping
    entries = []  # (variant, timezone, region_comment)

    # Track which regions we're in for comments
    current_region = None

    for slug, country in ports:
        # Determine timezone
        tz = PORT_TZ_OVERRIDES.get(slug)
        if not tz:
            tz = COUNTRY_TZ.get(country)
        if not tz:
            continue  # Skip unmappable ports

        name = slug_to_name(slug)
        variants = generate_variants(slug, name)

        for v in sorted(variants):
            if v and len(v) > 1:  # Skip single-char variants
                entries.append((v, tz, country))

    # Sort entries by name
    entries.sort(key=lambda x: x[0])

    # Group by region and write
    regions = {}
    for variant, tz, country in entries:
        # Determine region
        if country in ('United States', 'Canada'):
            region = 'North America'
        elif country in ('Mexico', 'Belize', 'Guatemala', 'Honduras',
                         'El Salvador', 'Nicaragua', 'Costa Rica', 'Panama'):
            region = 'Mexico & Central America'
        elif country in ('Bahamas', 'Jamaica', 'Cuba', 'Dominican Republic',
                         'Puerto Rico', 'US Virgin Islands', 'British Virgin Islands',
                         'Antigua and Barbuda', 'Saint Kitts and Nevis', 'Saint Lucia',
                         'Barbados', 'Grenada', 'Saint Vincent and the Grenadines',
                         'Trinidad and Tobago', 'Dominica', 'Martinique', 'Guadeloupe',
                         'Aruba', 'Curacao', 'Bonaire', 'Sint Maarten', 'Saint Martin',
                         'Cayman Islands', 'Turks and Caicos Islands', 'Bermuda',
                         'Haiti', 'Montserrat', 'Anguilla', 'Saint Barthelemy',
                         'Saba', 'Barbuda'):
            region = 'Caribbean'
        elif country in ('Colombia', 'Venezuela', 'Ecuador', 'Peru', 'Chile',
                         'Argentina', 'Uruguay', 'Brazil', 'Suriname', 'French Guiana',
                         'Falkland Islands', 'South Georgia'):
            region = 'South America'
        elif country in ('United Kingdom', 'Ireland', 'France', 'Spain', 'Portugal',
                         'Italy', 'Greece', 'Turkey', 'Croatia', 'Montenegro',
                         'Albania', 'Slovenia', 'Malta', 'Cyprus', 'Monaco',
                         'Gibraltar'):
            region = 'Mediterranean & Western Europe'
        elif country in ('Netherlands', 'Belgium', 'Germany', 'Denmark', 'Sweden',
                         'Norway', 'Finland', 'Estonia', 'Latvia', 'Lithuania',
                         'Poland', 'Romania', 'Bulgaria', 'Serbia', 'Hungary',
                         'Slovakia', 'Czech Republic', 'Austria', 'Switzerland',
                         'Russia', 'Ukraine', 'Iceland', 'Faroe Islands', 'Svalbard',
                         'Greenland', 'Isle of Man', 'Guernsey', 'Jersey', 'Moldova',
                         'Georgia'):
            region = 'Northern Europe & Baltic'
        elif country in ('Morocco', 'Tunisia', 'Algeria', 'Libya', 'Egypt',
                         'Senegal', 'Gambia', 'Guinea-Bissau', 'Guinea',
                         'Ivory Coast', 'Ghana', 'Togo', 'Benin', 'Nigeria',
                         'Cameroon', 'Gabon', 'Republic of the Congo', 'Angola',
                         'Namibia', 'South Africa', 'Mozambique', 'Tanzania',
                         'Kenya', 'Madagascar', 'Mauritius', 'Reunion', 'Seychelles',
                         'Comoros', 'Mayotte', 'Zanzibar', 'Cape Verde',
                         'Sao Tome and Principe', 'Mauritania', 'Saint Helena'):
            region = 'Africa'
        elif country in ('Israel', 'Jordan', 'Lebanon', 'Saudi Arabia',
                         'United Arab Emirates', 'Oman', 'Qatar', 'Bahrain',
                         'Kuwait', 'Iran', 'Iraq', 'Syria', 'Yemen'):
            region = 'Middle East'
        elif country in ('India', 'Sri Lanka', 'Maldives', 'Thailand', 'Vietnam',
                         'Cambodia', 'Myanmar', 'Malaysia', 'Singapore', 'Indonesia',
                         'Philippines', 'Brunei', 'Taiwan', 'South Korea', 'Japan',
                         'China', 'Hong Kong', 'Pakistan', 'East Timor'):
            region = 'Asia'
        elif country in ('Australia', 'New Zealand', 'Fiji', 'Papua New Guinea',
                         'Solomon Islands', 'Vanuatu', 'New Caledonia', 'Tonga',
                         'Samoa', 'American Samoa', 'Cook Islands', 'French Polynesia',
                         'Guam', 'Palau', 'Micronesia', 'Marshall Islands',
                         'Kiribati', 'Norfolk Island', 'Pitcairn Islands',
                         'Saipan', 'Northern Mariana Islands', 'Chatham Islands',
                         'Niue', 'Tuvalu'):
            region = 'Pacific & Oceania'
        elif country == 'Antarctica':
            region = 'Antarctica'
        else:
            region = 'Other'

        if region not in regions:
            regions[region] = []
        regions[region].append((variant, tz))

    # Write the file
    region_order = [
        'North America', 'Mexico & Central America', 'Caribbean',
        'South America', 'Mediterranean & Western Europe',
        'Northern Europe & Baltic', 'Africa', 'Middle East',
        'Asia', 'Pacific & Oceania', 'Antarctica', 'Other'
    ]

    with open('/home/user/ken/tz-cities', 'w') as f:
        f.write("# City-to-timezone mapping for the tz command\n")
        f.write("# Format: city_name|timezone\n")
        f.write("# Source: whatsinport.com (~1200 cruise ports)\n")
        f.write("# Includes fuzzy matching variants for each port\n")
        f.write("#\n")
        f.write("# Add your own entries at the bottom.\n\n")

        seen = set()
        for region in region_order:
            if region not in regions:
                continue
            f.write(f"# --- {region} ---\n")
            for variant, tz in sorted(regions[region]):
                key = f"{variant}|{tz}"
                if key not in seen:
                    seen.add(key)
                    f.write(f"{variant}|{tz}\n")
            f.write("\n")

    print(f"Generated {len(seen)} entries across {len(regions)} regions")


if __name__ == '__main__':
    main()
