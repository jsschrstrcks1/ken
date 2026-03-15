import json

# Load port-country mappings
port_country = {}
with open('/home/user/ken/whatsinport_port_country_map.txt') as f:
    for line in f:
        line = line.strip()
        if '|' in line:
            slug, country = line.split('|', 1)
            # If duplicate slug, keep first (or could merge)
            if slug not in port_country:
                port_country[slug] = country

# Load all port slugs from sitemap
all_ports = []
with open('/home/user/ken/whatsinport_ports_filtered.txt') as f:
    for line in f:
        slug = line.strip()
        if not slug:
            continue
        
        # Determine if it's a river cruise port
        river_suffixes = {
            'fr': 'France', 'de': 'Germany', 'at': 'Austria', 'ch': 'Switzerland',
            'hu': 'Hungary', 'sk': 'Slovakia', 'hr': 'Croatia', 'bg': 'Bulgaria',
            'ro': 'Romania', 'md': 'Moldova', 'nl': 'Netherlands', 'be': 'Belgium',
            'cz': 'Czech Republic', 'rs': 'Serbia', 'pt': 'Portugal', 'eg': 'Egypt',
            'us': 'USA', 'vn': 'Vietnam', 'kh': 'Cambodia', 'cn': 'China',
            'br': 'Brazil', 'pe': 'Peru', 'in': 'India'
        }
        
        is_river = False
        river_country = None
        for suffix, country_name in river_suffixes.items():
            if slug.endswith(f'-{suffix}'):
                is_river = True
                river_country = country_name
                break
        
        port_name = slug.replace('-', ' ').replace('_', ' ')
        url = f"https://www.whatsinport.com/{slug}.htm"
        
        country = river_country if is_river else port_country.get(slug, '')
        
        port_entry = {
            'slug': slug,
            'port_name': port_name,
            'url': url,
            'country': country,
            'type': 'river' if is_river else 'ocean'
        }
        all_ports.append(port_entry)

# Stats
total = len(all_ports)
mapped = sum(1 for p in all_ports if p['country'])
unmapped = [p for p in all_ports if not p['country']]
ocean_ports = [p for p in all_ports if p['type'] == 'ocean']
river_ports = [p for p in all_ports if p['type'] == 'river']

print(f"Total ports: {total}")
print(f"Ocean/sea ports: {len(ocean_ports)}")
print(f"River cruise ports: {len(river_ports)}")
print(f"Mapped to country: {mapped}")
print(f"Unmapped: {len(unmapped)}")

if unmapped:
    print("\nUnmapped ports:")
    for p in unmapped:
        print(f"  {p['slug']}")

# Save JSON
with open('/home/user/ken/whatsinport_all_ports.json', 'w') as f:
    json.dump(all_ports, f, indent=2)

print(f"\nSaved to whatsinport_all_ports.json")

# Save country summary
countries = {}
for p in all_ports:
    c = p['country'] or 'UNMAPPED'
    countries.setdefault(c, []).append(p['slug'])

print(f"\nCountries/regions: {len(countries)}")
for c in sorted(countries.keys()):
    print(f"  {c}: {len(countries[c])} ports")
