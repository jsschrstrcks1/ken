import json

# Manual mappings for the 114 unmapped ports
manual_map = {
    'Al-Khoms': 'Libya',
    'Beirut': 'Lebanon',
    'Bonne-Bay': 'Canada',
    'Hodeidah': 'Yemen',
    'Isola-di-Pantelleria': 'Italy',
    'Latakia': 'Syria',
    'Layoune': 'Western Sahara',
    'Mandal': 'Norway',
    'Matsuyama': 'Japan',
    'Namsos': 'Norway',
    'Nouakchott': 'Mauritania',
    'Omaezaki': 'Japan',
    'Oranjestad': 'Aruba',
    'Oye-Storfjord': 'Norway',
    'Palm-Beach': 'USA',
    'Provincetown': 'USA',
    'Reine': 'Norway',
    'Rodrigues': 'Mauritius',
    'Sakata': 'Japan',
    'Scheveningen': 'Netherlands',
    'Tartus': 'Syria',
    'Tokushima': 'Japan',
    'Tripolis': 'Libya',
    'Vibo-Valentia': 'Italy',
    'Vikoyri': 'Norway',
    'Wilmington-Delaware': 'USA',
    'Yangon-Rangoon': 'Myanmar',
    'Gdansk-City': 'Poland',
    'Hue': 'Vietnam',
    'Aasiaat-Egedesminde': 'Greenland',
    'Agatti-Lakshadweep': 'India',
    'Aldabra': 'Seychelles',
    'Anakena-Beach': 'Easter Island',
    'Attu-Aleutian-Islands': 'Alaska',
    'Auckland-Island': 'New Zealand',
    'Avarua-Rarotonga': 'Cook Islands',
    'Aveiro': 'Portugal',
    'Bandanaira-Bandar-Besar': 'Indonesia',
    'Bangaram-Lakshadweep': 'India',
    'Bantry': 'Ireland',
    'Barrow-AK': 'Alaska',
    'Basaruto-Island': 'Mozambique',
    'Beechey-Island-Barrow-Strait': 'Canada',
    'Bintan-Island': 'Indonesia',
    'Broughton-Island': 'Canada',
    'Button-Island': 'Canada',
    'Cambridge-Bay-Victoria-Island': 'Canada',
    'Campbell-Island': 'New Zealand',
    'Cape-Dorset': 'Canada',
    'Cayo-Levantado': 'Dominican Republic',
    'Charlotte-Amalie-Saint-Thomas': 'US Virgin Islands',
    'Chichi-Shima-Bonin-Islands': 'Japan',
    'Christianso-Island': 'Denmark',
    'Coburg-Island-Lady-Ann-Strait': 'Canada',
    'Cres': 'Croatia',
    'Diana-Bay': 'Canada',
    'Dundas-Harbor-Nunavut-Territory': 'Canada',
    'El-Porvenir-San-Blas': 'Panama',
    'Emerald-Bay': 'Bahamas',
    'Erics-Cove-Ivujivik': 'Canada',
    'Florianopolis': 'Brazil',
    'Fulanga-Island': 'Fiji',
    'Gairloch-Scotland': 'United Kingdom',
    'Giardini-Naxos': 'Italy',
    'Golfo-de-San-Miguel-Darien-Jungle': 'Panama',
    'Hamilton-Inlet': 'Canada',
    'Hebron-Labrador': 'Canada',
    'Heiligendamm': 'Germany',
    'Herschel-Island': 'Canada',
    'Holman': 'Canada',
    'Hurghada': 'Egypt',
    'Iqaluit-Frobisher-Bay': 'Canada',
    'Isla-de-la-Plata': 'Ecuador',
    'Isle-of-Iona-Scotland': 'United Kingdom',
    'Iwo-Jima': 'Japan',
    'Jayapura': 'Indonesia',
    'Jenny-Lind-Island': 'Canada',
    'Kadmat-Island-Lakshadweep': 'India',
    'Kingscote': 'Australia',
    'Kiska-Island-Aleutian-Islands': 'Alaska',
    'Kuramati': 'Maldives',
    'Mamoutzou-Mayotte': 'Mayotte',
    'Manitsoq': 'Greenland',
    'Marbella': 'Spain',
    'Marigot-Bay': 'Saint Lucia',
    'Maug': 'Northern Mariana Islands',
    'Norris-Point-Newfoundland': 'Canada',
    'Nosy-Boraha': 'Madagascar',
    'Nosy-Mangabe': 'Madagascar',
    'Pangnirtung-Baffin-Island': 'Canada',
    'Paracas': 'Peru',
    'Peel-Sound': 'Canada',
    'Pigeon-Island': 'Saint Lucia',
    'Point-Hope-AK': 'Alaska',
    'Pond-Inlet-Baffin-Island': 'Canada',
    'Port-Castries': 'Saint Lucia',
    'Poum': 'New Caledonia',
    'Prainha': 'Brazil',
    'Qasigianguit': 'Greenland',
    'Resolute': 'Canada',
    'Ross-Point-Coronation-Gulf': 'Canada',
    'Saint-Brides-Newfoundland': 'Canada',
    'Saint-Matthew-Island-Bering-Sea': 'Alaska',
    'Saint-Paul-Pribilof-Islands': 'Alaska',
    'Sao-Felipe-Fogo': 'Cape Verde',
    'Seguam-Island-AK': 'Alaska',
    'Sept_Iles': 'Canada',
    'Smoking-Hills': 'Canada',
    'Son-Con': 'Vietnam',
    'Tanaga-Island-AK': 'Alaska',
    'Taolanaro': 'Madagascar',
    'Tioman-Island': 'Malaysia',
    'Twillingate-Newfoundland': 'Canada',
    'Vaitape-Bora-Bora': 'French Polynesia',
    'Veli-Brijun-Brijuni-Islands': 'Croatia',
    'Vung-Tau': 'Vietnam',
    'Wineglass-Bay-Oyster-Bays-Tasmania': 'Australia',
}

# Load existing JSON
with open('/home/user/ken/whatsinport_all_ports.json') as f:
    ports = json.load(f)

# Apply manual mappings
for port in ports:
    if not port['country'] and port['slug'] in manual_map:
        port['country'] = manual_map[port['slug']]

# Check if any still unmapped
unmapped = [p for p in ports if not p['country']]
print(f"Still unmapped: {len(unmapped)}")
for p in unmapped:
    print(f"  {p['slug']}")

# Save updated JSON
with open('/home/user/ken/whatsinport_all_ports.json', 'w') as f:
    json.dump(ports, f, indent=2)

# Print summary
print(f"\nTotal ports: {len(ports)}")
print(f"Mapped: {sum(1 for p in ports if p['country'])}")
print(f"Ocean: {sum(1 for p in ports if p['type'] == 'ocean')}")
print(f"River: {sum(1 for p in ports if p['type'] == 'river')}")

# Count unique countries
countries = set(p['country'] for p in ports if p['country'])
print(f"Unique countries/regions: {len(countries)}")
