import math
import time

import pygame.image

from block import Block
from object import Object


class Bullet(Object):
    SPEED = 25
    COLOR = (255, 0, 0)
    SCALE = (15, 15)

    def __init__(self, position, rotation):
        super().__init__(position, rotation, Bullet.SCALE, pygame.image.load("../resources/bullet.png"))

        # Calculate x and y components of the velocity vector
        self.x_speed = Bullet.SPEED * math.cos(math.radians(rotation))
        self.y_speed = Bullet.SPEED * math.sin(math.radians(rotation))

        # Get time of creation to set time for burnout
        self.time_of_creation = time.perf_counter()

    def update(self, everything):
        # update bullet position using its speed
        self.global_position[0] += self.x_speed
        self.global_position[1] += self.y_speed

        # destroy bullet if it burned out
        if self.time_of_creation + 1 <= time.perf_counter():
            self.destroy()

        # remove the player that had shot the bullet, so they won't collide with each other.
        everything.pop(0)
        # take the object colliding
        i = self.get_rect().collidelist([i.get_rect() for i in everything])
        if i != -1:
            obj = everything[i]
            # if it's a block, destroy bullet
            if type(obj) == Block:
                self.destroy()


