#!/bin/bash

convert \( palace_11.png palace_12.png palace_13.png palace_14.png palace_15.png palace_16.png +append \) \
\( palace_21.png palace_22.png palace_23.png palace_24.png palace_25.png palace_26.png +append \) \
\( palace_31.png palace_32.png palace_33.png palace_34.png palace_35.png palace_36.png +append \) \
\( palace_41.png palace_42.png palace_43.png palace_44.png palace_45.png palace_46.png +append \) \
\( damaged_building_1.png damaged_building_2.png damaged_building_3.png damaged_building_4.png broken_front_wall.png broken_left_wall.png +append \) \
\( damaged_building_5.png damaged_building_6.png damaged_building_7.png damaged_building_8.png destroyed_building_1.png destroyed_building_2.png +append \) \
\( broken_building_1.png broken_building_2.png broken_building_3.png broken_building_4.png front_wall.png grass.png +append \) \
\( broken_building_5.png broken_building_6.png broken_building_7.png broken_building_8.png left_wall_end.png left_wall.png +append \) \
\( sand.png top_right_wall.png bridge_left.png bridge_right.png pavement.png city_wall_nw.png +append \) \
\( city_wall_se.png water.png city_wall_sw2.png +append \) \
-background none -append tileset_destroyed_cities.png
