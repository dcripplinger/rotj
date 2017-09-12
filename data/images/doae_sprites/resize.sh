#!/bin/bash

for i in *.gif; do
    printf "Resize $i\n"
    convert "$i" -sample 16x16 "$i"
done
