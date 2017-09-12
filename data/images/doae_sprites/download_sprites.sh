#!/bin/bash

for i in *.gif; do
    printf "Downloading $i\n"
    curl http://kongming.net/doae/i/hax/sprites/"$i" > "$i"
done
