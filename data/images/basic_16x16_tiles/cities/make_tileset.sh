#!/bin/bash

convert \( bridge_horiz.png door.png grass.png grass_e.png grass_n.png +append \) \
\( grass_ne.png grass_nw.png grass_s.png grass_se.png grass_sw.png +append \) \
\( grass_w.png house_ne.png house_nw.png house_se.png house_sw.png +append \) \
\( path.png path_e.png path_ne.png path_ns.png path_nw.png +append \) \
\( path_s.png path_se.png path_sw.png path_w.png path_we.png +append \) \
\( roof1.png roof2.png roof3.png sand.png tree1.png +append \) \
\( tree2.png wall.png water.png window.png path_n.png +append \) \
\( city_wall_sw.png city_wall_se.png city_wall_e.png city_wall_n.png city_wall_w.png +append \) \
\( pavement.png city_wall_ne.png city_wall_nw.png palace1.png palace2.png +append \) \
\( palace3.png palace4.png palace5.png palace6.png palace7.png +append \) \
\( palace8.png palace9.png palace10.png palace11.png palace12.png +append \) \
\( palace13.png palace14.png palace15.png palace16.png palace17.png +append \) \
\( palace18.png palace19.png palace20.png palace21.png bridge_vert.png +append \) \
\( city_wall_sw2.png city_wall_se2.png +append \) \
-background none -append   tileset_cities.png
