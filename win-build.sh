#!/bin/bash

pyinstaller src/rotj.py -y
cp -r data dist/rotj/
rm dist/rotj/data/state/*.json