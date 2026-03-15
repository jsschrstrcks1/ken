#!/bin/bash
output_file="/home/user/ken/whatsinport_port_country_map.txt"

pages=(
"Australia.html" "Bahrain.html" "Chile.html" "French-Polynesia.html" 
"Jamaica.html" "Japan.html" "Jordan.html" "Kiribati.html" "Malta.html"
"Netherlands-Antilles.html" "Poland.html" "Portugal.html" "Puerto-Rico.html" 
"Romania.html" "Saint-Helena.html" "Saint-Martin.html" "Saudi-Arabia.html" 
"Sri-Lanka.html" "Thailand.html" "US-Virgin-Islands.html"
)

for page in "${pages[@]}"; do
  country=$(echo "$page" | sed 's/\.html$//' | sed 's/-/ /g')
  url="https://www.whatsinport.com/$page"
  
  html=$(curl -s --max-time 15 "$url" 2>/dev/null)
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
