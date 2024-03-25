import math
import time

import pygame.image

from object import Object


class Bullet(Object):
    # notice: increasing bullet speed might result in unexpected collision glitches (both visual and practical)
    SPEED = 8
    SCALE = (15, 15)
    DISTANCE_FROM_CENTER = 6  # on spawn

    def __init__(self, parent):

        # Calculate x and y components of the velocity vector
        self.x_speed = Bullet.SPEED * math.cos(math.radians(parent.rotation))
        self.y_speed = Bullet.SPEED * math.sin(math.radians(parent.rotation))

        # get bullet spawn position (which is between the base and the tip of the turret)
        bullet_position = [parent.global_position[0] + (parent.scale[0] / 2 - Bullet.SCALE[0] / 2), parent.global_position[1] + (parent.scale[1] / 2 - Bullet.SCALE[1] / 2)]
        bullet_position[0] += self.x_speed * Bullet.DISTANCE_FROM_CENTER
        bullet_position[1] += self.y_speed * Bullet.DISTANCE_FROM_CENTER


        super().__init__(bullet_position, parent.rotation, Bullet.SCALE, pygame.image.load("../resources/bullet.png"), 0)

        # The play who shot the bullet
        self.parent = parent
        self.wall_list = [-1]  # list of wall blocks ids collided with (contains dupes)

        # Get time of creation to set time for burnout
        self.time_of_creation = time.perf_counter()
        self.lifetime = 2

    def update(self, everything):
        # update bullet position using its speed
        self.global_position[0] += self.x_speed
        self.global_position[1] += self.y_speed

        # destroy bullet if it burned out
        if self.time_of_creation + self.lifetime <= time.perf_counter():
            self.destroy()
        # reverse the bullets speed when it hits a wall
        if self.block_collision[0] or self.block_collision[2]:
            self.y_speed *= -1
        if self.block_collision[1] or self.block_collision[3]:
            self.x_speed *= -1

        # reset block collisions
        self.block_collision = [False, False, False, False]

