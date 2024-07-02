import random

the_map = "objects = [this_player, "
powerups = ["'heal'", "'1up'", "'speed'", "'strength'"]

for i in range(250):
    size = random.randint(50, 200)
    the_map += f"Block({(random.randrange(-5000, 5000), random.randrange(-5000, 5000))}, {(size, size)}, 'wall', {i}), "

for i in range(250, 500):
    size = random.randint(50, 200)
    the_map += f"Block({(random.randrange(-5000, 5000), random.randrange(-5000, 5000))}, {(size, size)}, 'box', {i}), "

for i in range(250, 500):
    the_map += f"Powerup({(random.randrange(-5000, 5000), random.randrange(-5000, 5000))}, {powerups[random.randint(0, 3)]}), "

the_map = the_map[:-2] + "]"
print(the_map)