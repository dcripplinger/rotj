#!/usr/bin/env python

# Usage:  $> ./cities_convert.py
# It will prompt "Paste lines:"
# Copy and paste the csv portion of a city tmx file and hit enter until it prints output
# Copy and paste the output back into the tmx file, replacing the csv data already there.
# Make sure you change the tileset specified in the tmx file from cities_tileset.tsx to cities2.tsx

import sys

tile_mapping = {'1': '30', '2': '45', '3': '16', '4': '22', '5': '14',
                '6': '15', '7': '13', '8': '20', '9': '21', '10': '19',
                '11': '23', '12': '41', '13': '37', '14': '47', '15': '43',
                '16': '36', '17': '34', '18': '27', '19': '28', '20': '25',
                '21': '32', '22': '33', '23': '31', '24': '35', '25': '29',
                '26': '38', '27': '39', '28': '40', '29': '54', '30': '49',
                '31': '55', '32': '46', '33': '42', '34': '44', '35': '26',
                '36': '9',  '37': '11', '38': '3',  '39': '10', '40': '4',
                '41': '48', '42': '2',  '43': '1',  '44': '50', '45': '51',
                '46': '52', '47': '53', '48': '56', '49': '57', '50': '58',
                '51': '59', '52': '60', '53': '61', '54': '62', '55': '63',
                '56': '64', '57': '65', '58': '66', '59': '67', '60': '68',
                '61': '69', '62': '70', '63': '71', '64': '72', '65': '24',
                '66': '7',  '67': '8', '': '',
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
