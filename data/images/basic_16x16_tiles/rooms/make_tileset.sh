#!/bin/bash

convert \( black.png chair.png corner_shadow.png floor.png outer_corner_shadow.png \) \
\( side_shadow.png table.png top_shadow.png under_corner_shadow.png wall.png \) \
\( wall_top.png \) \
-background none -append tileset_rooms.png