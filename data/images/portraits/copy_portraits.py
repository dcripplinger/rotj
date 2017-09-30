import subprocess

with open('names.txt') as f:
    names = f.read().splitlines()
with open('portraits.txt') as f:
    portraits = f.read().splitlines()

for i, name in enumerate(names):
    portrait = portraits[i]
    if portrait.endswith('.png'):
        subprocess.call(['cp', 'minor/{}'.format(portrait), '{}.png'.format(name.lower())])
