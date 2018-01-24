#!/bin/bash

convert \( black.png ground.png wall1.png wall2.png wall3.png +append \) \
\( wall4.png wall5.png wall6.png wall7.png pot.png +append \) \
\( grate1.png grate2.png carpet1.png carpet2.png carpet3.png +append \) \
\( carpet4.png carpet5.png carpet6.png carpet7.png carpet8.png +append \) \
\( carpet9.png chair.png +append \) \
-background none -append tileset_tent.png
