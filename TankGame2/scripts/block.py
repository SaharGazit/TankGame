import pygame
from object import Object
from bullet import Bullet


class Block(Object):

    def __init__(self, starting_position, size, block_type, block_id):
        super().__init__(starting_position, 0, size, pygame.image.load(f"../resources/{block_type}.png"), block_id)

        self.block_type = block_type
        # list of colliders from every direction
        self.side_colliders = []

    def update(self, everything):
        # update side colliders
        if self.block_type == "wall":
            local = self.local_position()
            self.side_colliders = [pygame.Rect(local[0] + 3, local[1], 95, 3),
                                   pygame.Rect(local[0] + 97, local[1] + 3, 3, 95),
                                   pygame.Rect(local[0] + 3, local[1] + 97, 95, 3),
                                   pygame.Rect(local[0], local[1] + 3, 3, 95)]

            # get collided object lists
            collide_list = self.get_all_colliding_objects(everything)
            for side in range(4):  # checks through every side of the block
                for collided in collide_list[side]:  # checks every object that collided with this side

                    if type(collided) == Bullet:
                        if collided.wall_list[-1] != self.id:
                            collided.wall_list.append(self.id)
                            collided.block_collision[side] = True

    def get_all_colliding_objects(self, candidates):
        colliding = []
        for side in self.side_colliders:
            indices = side.collidelistall([i.get_rect() for i in candidates])
            colliding.append([candidates[i] for i in indices])
        return colliding

