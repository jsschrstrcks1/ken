import json, csv

with open('/home/user/ken/whatsinport_all_ports.json') as f:
    ports = json.load(f)

# Write CSV
with open('/home/user/ken/whatsinport_all_ports.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['slug', 'port_name', 'country', 'type', 'url'])
    for p in sorted(ports, key=lambda x: x['slug']):
        writer.writerow([p['slug'], p['port_name'], p['country'], p['type'], p['url']])

print(f"CSV written: {len(ports)} rows")

# Print first 20 as sample
print("\nSample entries:")
for p in sorted(ports, key=lambda x: x['slug'])[:20]:
    print(f"  {p['slug']:40s} | {p['country']:25s} | {p['type']}")

# Country counts
from collections import Counter
country_counts = Counter(p['country'] for p in ports)
print(f"\nTop 20 countries by port count:")
for country, count in country_counts.most_common(20):
    print(f"  {country:30s}: {count}")
