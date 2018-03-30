#!/usr/bin/env python

# Usage:  $> ./overworld_convert.py
# It will prompt "Paste lines:"
# Copy and paste the csv portion of the overworld tmx file and hit enter until it prints output
# Copy and paste the output back into the tmx file, replacing the csv data already there.

import sys

tile_mapping = {'1': '35',  '2': '37',  '3': '36',  '4': '25',  '5': '2',   '6': '3',   '7': '1',   '8': '10',
                '9': '11',  '10': '9',  '11': '34', '12': '17', '13': '21', '14': '29', '15': '28', '16': '19',
                '17': '18', '18': '20', '19': '31', '20': '30', '21': '26', '22': '5',  '23': '4',  '24': '13',
                '25': '12', '26': '27', '27': '32', '28': '14', '29': '23', '30': '22', '31': '24', '32': '7',
                '33': '6',  '34': '8',  '35': '16', '36': '33', '37': '38', '38': '39', '39': '40', '40': '15',
                '': '',
                }


print "Paste lines:"
run = True
line_buffer = []
while run:
    line = sys.stdin.readline().rstrip('\n')
    if line == '':
        run = False
    vals = line.split(',')
    new_vals = [tile_mapping[x] for x in vals]
    new_line = ','.join(new_vals)
    line_buffer.append(new_line)


print "****************************************************************************************"
print "*** Output *****************************************************************************"
print "****************************************************************************************"
for line in line_buffer:
    print line
