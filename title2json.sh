#!/bin/bash

while IFS= read -r line; do
	num=$(echo "$line" | cut -f1 | sed -e 's/ //g')
	name=$(echo "$line" | cut -f2)
	mv "movies/$num.json" /tmp/tmp.json
	jq -r ".title |= \"$name\"" /tmp/tmp.json > "movies/$num.json"
done < <(cat 2018_movie_clean | cut -f1-2)
