#!/bin/bash
# For each country page, extract port links and map them to the country
output_file="/home/user/ken/whatsinport_port_country_map.txt"
> "$output_file"

# Also handle single-port countries from dropdown
echo "Anguilla|Anguilla" >> "$output_file"
echo "Aruba|Aruba" >> "$output_file"
echo "Georgetown|Ascension" >> "$output_file"
echo "Bridgetown|Barbados" >> "$output_file"
echo "Cotonou|Benin" >> "$output_file"
echo "Bonaire|Bonaire" >> "$output_file"
echo "Sihanoukville|Cambodia" >> "$output_file"
echo "Victoria|Cameroon" >> "$output_file"
echo "Pointe-Noire|Congo" >> "$output_file"
echo "Curacao|Curacao" >> "$output_file"
echo "Hangaroa|Easter Island" >> "$output_file"
echo "Acajutla|El Salvador" >> "$output_file"
echo "Banjul|Gambia" >> "$output_file"
echo "Batumi|Georgia" >> "$output_file"
echo "Gibraltar|Gibraltar" >> "$output_file"
echo "Guam|Guam" >> "$output_file"
echo "Conakry|Guinea" >> "$output_file"
echo "Bissau|Guinea Bissau" >> "$output_file"
echo "Labadee|Haiti" >> "$output_file"
echo "Mombasa|Kenya" >> "$output_file"
echo "Klaipeda|Lithuania" >> "$output_file"
echo "Funchal-Madeira|Madeira" >> "$output_file"
echo "Male|Maldives" >> "$output_file"
echo "Port-Louis|Mauritius" >> "$output_file"
echo "Monte-Carlo|Monaco" >> "$output_file"
echo "Alofi|Niue" >> "$output_file"
echo "Koror|Palau" >> "$output_file"
echo "Doha|Qatar" >> "$output_file"
echo "Pointe-des-Galets|Reunion" >> "$output_file"
echo "Saba|Saba" >> "$output_file"
echo "Gustavia|Saint Barthelemy" >> "$output_file"
echo "Saint-Lucia|Saint Lucia" >> "$output_file"
echo "Saint-Pierre-and-Miquelon|Saint Pierre and Miquelon" >> "$output_file"
echo "Apia-Samoa-i-Sisifo|Samoa" >> "$output_file"
echo "Sao-Tome|Sao Tome and Principe" >> "$output_file"
echo "Dakar|Senegal" >> "$output_file"
echo "Singapore|Singapore" >> "$output_file"
echo "Philipsburg-Sint-Maarten|Sint Maarten" >> "$output_file"
echo "Paramaribo|Suriname" >> "$output_file"
echo "Lome|Togo" >> "$output_file"
echo "Grand-Turk|Turks and Caicos" >> "$output_file"

while IFS= read -r page; do
  country=$(echo "$page" | sed 's/\.html$//' | sed 's/-/ /g')
  url="https://www.whatsinport.com/$page"
  
  # Fetch page and extract .htm links (port pages)
  ports=$(curl -s "$url" 2>/dev/null | grep -oP 'href="([^"]+)\.htm"' | sed 's/href="//;s/\.htm"//' | sort -u)
  
  for port in $ports; do
    # Skip non-port links
    if [[ "$port" != "hints" && "$port" != "Pricelevels" && "$port" != "index" ]]; then
      echo "${port}|${country}" >> "$output_file"
    fi
  done
  
  echo "Fetched $page: $(echo "$ports" | wc -w) ports"
done < /home/user/ken/whatsinport_country_pages.txt

echo "Total mappings: $(wc -l < "$output_file")"
