#!/bin/bash
output_file="/home/user/ken/whatsinport_port_country_map.txt"

# Pages that returned 0 results
pages=(
"Alaska.html" "American-Samoa.html" "Antarctica.html" "Argentina.html" "Australia.html" 
"Azores.html" "Bahrain.html" "Belgium.html" "Belize.html" "Canary-Islands.html" 
"Chile.html" "Croatia.html" "Cyprus.html" "French-Polynesia.html" 
"Ivory-Coast.html" "Jamaica.html" "Japan.html" "Jordan.html" "Kiribati.html" 
"Madagascar.html" "Malaysia.html" "Malta.html" "Mexico.html" "Mozambique.html" 
"Netherlands-Antilles.html" "Netherlands.html" "New-Caledonia.html" "New-Zealand.html" 
"Nicaragua.html" "Norway.html" "Pakistan.html" "Panama.html" "Peru.html" 
"Philippines.html" "Poland.html" "Portugal.html" "Puerto-Rico.html" "Romania.html" 
"Saint-Helena.html" "Saint-Martin.html" "Saudi-Arabia.html" "Solomon-Islands.html" 
"South-Africa.html" "Sri-Lanka.html" "Svalbard.html" "Sweden.html" "Thailand.html" 
"Tonga.html" "Turkey.html" "US-Virgin-Islands.html" "United-Kingdom.html"
)

for page in "${pages[@]}"; do
  country=$(echo "$page" | sed 's/\.html$//' | sed 's/-/ /g')
  url="https://www.whatsinport.com/$page"
  
  html=$(curl -s --max-time 10 "$url" 2>/dev/null)
  ports=$(echo "$html" | grep -oP 'href="([^"]+)\.htm"' | sed 's/href="//;s/\.htm"//' | sort -u)
  
  count=0
  for port in $ports; do
    if [[ "$port" != "hints" && "$port" != "Pricelevels" && "$port" != "index" ]]; then
      echo "${port}|${country}" >> "$output_file"
      count=$((count+1))
    fi
  done
  
  echo "Fetched $page: $count ports"
done

echo "Total mappings: $(wc -l < "$output_file")"
