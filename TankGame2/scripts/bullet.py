import math
import time

import pygame.image

from object import Object


class Bullet(Object):
    SPEED = 15
    COLOR = (255, 0, 0)
    SCALE = (15, 15)

    def __init__(self, position, rotation):
        super().__init__(position, rotation, Bullet.SCALE, pygame.image.load("../resources/bullet.png"), 0)

        # Calculate x and y components of the velocity vector
        self.x_speed = Bullet.SPEED * math.cos(math.radians(rotation))
        self.y_speed = Bullet.SPEED * math.sin(math.radians(rotation))
        self.wall_list = [-1]  # list of wall blocks collided with (contains dupes)

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

