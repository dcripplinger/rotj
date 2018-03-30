#!/bin/bash

convert \( +append \) \
\( city_wall_nw.png city_wall_ne.png city_wall_e.png city_wall_w.png city_wall_nw2.png city_wall_ne2.png +append \) \
\( city_wall_sw2.png city_wall_se2.png city_wall_sw.png city_wall_n.png city_wall_se.png well.png +append \) \
\( grass_nw.png grass_n.png grass_ne.png grass.png bridge_left.png bridge_right.png +append \) \
\( grass_sw.png grass_s.png grass_se.png grass_e.png grass_w.png bridge_vert.png +append \) \
\( path_nw.png path_n.png path_ne.png path_ns.png path_we.png bridge_horiz.png +append \) \
\( path_sw.png path_s.png path_se.png path_e.png path_w.png path.png +append \) \
\( house_nw.png roof1.png roof2.png roof3.png house_ne.png water.png +append \) \
\( house_sw.png window.png door.png wall.png house_se.png pavement.png +append \) \
\( tree1.png palace1.png palace2.png palace3.png palace4.png sand.png +append \) \
\( tree2.png palace5.png palace6.png palace7.png palace8.png palace9.png +append \) \
\( palace10.png palace11.png palace12.png palace13.png palace14.png palace15.png +append \) \
\( palace16.png palace17.png palace18.png palace19.png palace20.png palace21.png +append \) \
-background none -append   tileset_cities2.png
