#!/bin/bash

convert \( tent1.png tent2.png tent3.png tent4.png tent5.png +append \) \
\( tent6.png tent7.png tent8.png tent9.png tent10.png +append \) \
\( fence1.png fence2.png fence3.png fence4.png fence5.png +append \) \
\( tower1.png ground.png tent11.png tent12.png tent13.png +append \) \
\( tower2.png tower3.png gate_left.png gate_center.png gate_right.png +append \) \
\( flag-red.png flag-yellow.png flag-green.png flag-blue.png flag-black.png +append \) \
\( grass_nw.png grass_n.png grass_ne.png grass_e.png grass.png +append \) \
\( grass_sw.png grass_s.png grass_se.png grass_w.png water.png +append \) \
\( ground_grass_nw.png ground_grass_n.png ground_grass_ne.png ground_grass_e.png +append \) \
\( ground_grass_sw.png ground_grass_s.png ground_grass_se.png ground_grass_w.png +append \) \
\( ground_water_nw.png ground_water_n.png ground_water_ne.png ground_water_e.png +append \) \
\( ground_water_sw.png ground_water_s.png ground_water_se.png ground_water_w.png +append \) \
-background none -append tileset_camps.png
