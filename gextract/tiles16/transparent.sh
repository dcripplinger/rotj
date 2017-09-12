#!/bin/bash

for i in *.png; do
    convert $i -transparent black $i
done
