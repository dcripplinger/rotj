#!/bin/bash

convert \( tent1.png tent2.png tent3.png tent4.png tent5.png +append \) \
\( tent6.png tent7.png tent8.png tent9.png tent10.png +append \) \
\( fence1.png fence2.png fence3.png fence4.png fence5.png +append \) \
\( tower1.png ground.png tent11.png tent12.png tent13.png +append \) \
\( tower2.png tower3.png +append \) \
-background none -append tileset_camps.png
