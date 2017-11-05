#!/bin/bash

convert \( bridge_horiz.png door.png grass.png grass_e.png grass_n.png +append \) \
\( grass_ne.png grass_nw.png grass_s.png grass_se.png grass_sw.png +append \) \
\( grass_w.png house_ne.png house_nw.png house_se.png house_sw.png +append \) \
\( path.png path_e.png path_ne.png path_ns.png path_nw.png +append \) \
\( path_s.png path_se.png path_sw.png path_w.png path_we.png +append \) \
\( roof1.png roof2.png roof3.png sand.png tree1.png +append \) \
\( tree2.png wall.png water.png window.png path_n.png +append \) \
-background none -append   tileset_cities.png
