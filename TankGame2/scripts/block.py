import pygame
from object import Object
from bullet import Bullet
from player import Player


class Block(Object):

    def __init__(self, starting_position, size, block_type, block_id):
        super().__init__(starting_position, 0, size, pygame.image.load(f"../resources/{block_type}.png"), block_id)

        self.block_type = block_type
        # list of colliders from every direction
        self.side_colliders = []

    def update(self, everything):
        # update side colliders
        local = self.local_position()
        self.side_colliders = [pygame.Rect(local[0] + 3, local[1], 95, 3),
                               pygame.Rect(local[0] + 97, local[1] + 3, 3, 95),
                               pygame.Rect(local[0] + 3, local[1] + 97, 95, 3),
                               pygame.Rect(local[0], local[1] + 3, 3, 95)]

        # get collided object lists
        collide_list = self.get_all_colliding_objects(everything)
        for side in range(4):  # checks through every side of the block
            for collided in collide_list[side]:  # checks every object that collided with this side

                # bullet collision with a block
                if type(collided) == Bullet:
                    if self.block_type == "wall":
                        # check if the last wall this bullet has hit is not this one, to prevent the bullet from glitching inside the block
                        if collided.wall_list[-1] != self.id:
                            collided.wall_list.append(self.id)  # add this wall to the bullet's wall list
                            collided.block_collision[side] = True  # "tell" the bullet to change direction accordingly
                    elif self.block_type == "box":
                        # destroy bullet
                        collided.to_destroy = True

                # player collision with a block
                if type(collided) == Player:
                    # prevent player from moving to the direction of the block
                    collided.block_collision[side] = True

    def get_all_colliding_objects(self, candidates):
        colliding = []
        for side in self.side_colliders:
            indices = side.collidelistall([i.get_rect() for i in candidates])
            colliding.append([candidates[i] for i in indices])
        return colliding
