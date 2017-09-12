#!/bin/bash

convert \( bridge_horizontal.png bridge_snowy_horizontal.png bridge_vertical.png cave.png city_n.png city_ne.png city_nw.png city_s.png +append \) \
        \( city_se.png city_sw.png desert.png fence.png fence_right.png forest.png forest_snowy.png gate_center.png +append \) \
        \( gate_left.png gate_right.png grass.png hills.png mountains.png mountains_big_ne.png mountains_big_nw.png mountains_big_se.png +append \) \
        \( mountains_big_sw.png mountains_snowy.png path.png shore_e.png shore_n.png shore_ne.png shore_nw.png shore_s.png +append \) \
        \( shore_se.png shore_sw.png shore_w.png snow.png tents.png village_left.png village_right.png water.png +append \) \
        -background none -append   0_tileset_overworld.png
