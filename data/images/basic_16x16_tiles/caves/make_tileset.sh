#!/bin/bash

convert \( black.png downstairs.png ground.png ground_2.png ground_3.png ground_4.png rock.png rock_2a.png +append \) \
\( rock_2b.png rock_2_E.png rock_2_Eb.png rock_2_Ec.png rock_2_Ed.png rock_2_N.png rock_2_NE.png rock_2_NW.png +append \) \
\( rock_2_W.png rock_2_Wb.png rock_2_Wc.png rock_3a.png rock_3b.png rock_3c.png rock_3d.png rock_4.png +append \) \
\( shadow.png shadow_2.png shadow_3.png shadow_4.png upstairs.png upstairs_4.png wall.png wall_2.png +append \) \
\( wall_2b.png wall_3.png wall_4.png downstairs_2_right.png downstairs_2_left.png upstairs_2_right.png downstairs_left.png upstairs_4_left.png +append \) \
\( downstairs_4_right.png downstairs_4_left.png upstairs_3_right.png upstairs_3_left.png water.png +append \) \
-background none -append   tileset_caves.png
