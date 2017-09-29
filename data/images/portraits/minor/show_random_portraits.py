import os, random, sys, time, subprocess

while True:
    filename = random.choice(os.listdir(sys.argv[1]))
    print filename
    p = subprocess.Popen(['feh', '-F', '-Z', '--force-aliasing', '{}/{}'.format(sys.argv[1], filename)])
    time.sleep(1)
    p.kill()
