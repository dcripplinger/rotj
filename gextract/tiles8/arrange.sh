#!/bin/bash

i=0
j=0
for f in `ls *.bmp | sort -V`; do
    if [ $((i%4)) -eq 0 ]; then
        a=$f
    elif [ $((i%4)) -eq 1 ]; then
        b=$f
    elif [ $((i%4)) -eq 2 ]; then
        c=$f
    elif [ $((i%4)) -eq 3 ]; then
        d=$f
        printf -v formatted_number "%09d" $j
        convert \( $a $c +append \) \
                \( $b $d +append \) \
                -background none -append ../tiles16/$formatted_number.png
        j=$(expr $j + 1)
    fi
    i=$(expr $i + 1)
done
