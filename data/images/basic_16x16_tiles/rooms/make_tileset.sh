#!/bin/bash

convert \( black.png chair.png corner_shadow.png floor.png outer_corner_shadow.png +append \) \
\( side_shadow.png table.png top_shadow.png under_corner_shadow.png wall.png +append \) \
\( wall_top.png +append \) \
-background none -append tileset_rooms.png