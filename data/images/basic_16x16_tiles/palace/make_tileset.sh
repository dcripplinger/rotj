#!/bin/bash

convert \( carpet1.png carpet2.png carpet3.png carpet4.png carpet5.png +append \) \
\( carpet6.png carpet7.png carpet8.png carpet9.png carpet10.png +append \) \
\( carpet11.png carpet12.png carpet13.png carpet14.png carpet15.png +append \) \
\( carpet16.png pillar_bottom.png pillar_top.png platform_back1.png platform_back2.png +append \) \
\( platform_back3.png platform_back4.png platform_back5.png platform_back6.png platform_back7.png +append \) \
\( platform_left.png platform_right.png steps1.png steps2.png steps3.png +append \) \
\( steps4.png throne_back.png throne_seat.png tile1.png tile2.png +append \) \
\( tile3.png black.png wall.png wall_top.png +append \) \
-background none -append tileset_palace.png
