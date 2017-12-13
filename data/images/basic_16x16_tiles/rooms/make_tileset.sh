#!/bin/bash

convert \( black.png chair.png corner_shadow.png floor.png outer_corner_shadow.png +append \) \
\( side_shadow.png table.png top_shadow.png under_corner_shadow.png wall.png +append \) \
\( wall_top.png pot_gray.png floor_green.png corner_shadow_green.png outer_corner_shadow_green.png +append \) \
\( side_shadow_green.png top_shadow_green.png under_corner_shadow_green.png wall2.png wall_top2.png +append \) \
\( bed.png bed2.png desk.png bookshelf_left.png bookshelf_right.png +append \) \
\( floor_red.png outer_corner_shadow_red.png side_shadow_red.png top_shadow_red.png under_corner_shadow_red.png +append \) \
\( corner_shadow_red.png pot_pic.png +append \) \
-background none -append tileset_rooms.png
