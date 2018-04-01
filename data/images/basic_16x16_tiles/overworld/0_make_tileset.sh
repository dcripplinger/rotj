#!/bin/bash

convert \( city_nw.png city_n.png city_ne.png mountains_big_nw.png mountains_big_ne.png shore_se.png shore_s.png shore_sw.png +append \) \
        \( city_sw.png city_s.png city_se.png mountains_big_sw.png mountains_big_se.png shore_e.png water.png shore_w.png +append \) \
        \( fence.png gate_left.png gate_center.png gate_right.png fence_right.png shore_ne.png shore_n.png shore_nw.png +append \) \
        \( cave.png mountains.png mountains_snowy.png forest_snowy.png forest.png hills.png grass.png path.png +append \) \
        \( snow.png desert.png bridge_horizontal.png bridge_vertical.png bridge_snowy_horizontal.png tents.png village_left.png village_right.png +append \) \
        \( broken_fence.png +append \) \
        -background none -append   0_tileset_overworld.png
