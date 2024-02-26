import math
import time

import pygame
from object import Object
from block import Block
from powerup import Powerup


class Player(Object):
    MAX_SPEED = 5.2
    ACCELERATION = 0.8

    def __init__(self, name, starting_position, monitor_info, main_player=False):
        # inherited from Object class
        super().__init__(starting_position, 0, (48, 48), pygame.image.load("../resources/tankbody.png"))

        # player data
        self.name = name  # player's name
        self.main_player = main_player  # true if this Player object belongs to the user of this program.

        # gameplay variables
        self.acceleration = [0, 0]
        self.speed = [0, 0]
        self.powerups = {}  # list of powerup effects currently on the player.

        # technical
        self.monitor_info = monitor_info
        self.blocked_direction = [False, False, False, False]
        self.movement_colliders = [pygame.Rect(self.global_position[0] + 9, self.global_position[1] + 2, 30, 3), pygame.Rect(self.global_position[0] + 43, self.global_position[1] + 9, 3, 30), pygame.Rect(self.global_position[0] + 9, self.global_position[1] + 42, 30, 3), pygame.Rect(self.global_position[0] + 2, self.global_position[1] + 9, 3, 30)]

    # this function runs every game loop and is responsible for different continuous actions such as moving and rotating.
    def update(self, everything):
        self.move_player()
        self.rotate_by_mouse()
        self.handle_powerups()

        #  for c in self.movement_colliders:
        #  pygame.draw.rect(self.screen, (255, 255, 255), c)

        collide_list = self.get_all_colliding_objects(everything)
        for side in range(4):  # checks every side of the player
            for collided in collide_list[side]:  # checks every object that collided with the play at the moment

                if type(collided) == Block:
                    # block movement to the direction the block has collided with.
                    self.blocked_direction[side] = True

                if type(collided) == Powerup:

                    effect = collided.effect
                    # speed effect fix
                    if effect == 'speed':
                        self.acceleration = [self.acceleration[0] * 5, self.acceleration[1] * 5]
                    # add the powerup effect to the player
                    self.powerups[collided.effect] = time.perf_counter()

                    # destroy object
                    collided.to_destroy = True

    def move_player(self):
        # increase maximum speed if player is under "speed" effect
        max_speed = Player.MAX_SPEED
        if 'speed' in self.powerups:
            max_speed += 5

        # increase or decrease speed by acceleration, and check that it doesn't pass the max/min speed.
        if -max_speed <= self.speed[0] <= max_speed:
            self.speed[0] += self.acceleration[0]
        if -max_speed <= self.speed[1] <= max_speed:
            self.speed[1] += self.acceleration[1]

        # increase or decrease position by speed. check if play is not blocked in the direction he goes to.
        if (self.speed[0] > 0 and not self.blocked_direction[1]) or (self.speed[0] < 0 and not self.blocked_direction[3]):
            self.global_position[0] += self.speed[0]
        if (self.speed[1] > 0 and not self.blocked_direction[2]) or (self.speed[1] < 0 and not self.blocked_direction[0]):
            self.global_position[1] += self.speed[1]

        # reduce speed by natural deceleration
        self.speed[0] *= 0.940
        self.speed[1] *= 0.940

        if -0.1 < self.speed[0] < 0.1:
            self.speed[0] = 0
        if -0.1 < self.speed[1] < 0.1:
            self.speed[1] = 0

        # update camera
        Object.camera_position = [22.5 + self.global_position[0] - self.monitor_info.current_w / 2, 22.5 + self.global_position[1] - self.monitor_info.current_h / 2]

        # reset all blockers
        for i in range(4):
            self.blocked_direction[i] = False

    # sets the rotation of the player by the mouse position
    def rotate_by_mouse(self):
        # get mouse position
        target = pygame.mouse.get_pos()

        # calculate distance between mouse and player
        c = self.local_position()
        y_distance = target[1] - (c[1] + 22.5)
        x_distance = target[0] - (c[0] + 22.5)

        # calculate rotation angle using the arc-tangent function
        self.rotation = math.degrees(math.atan2(y_distance, x_distance))

    # handles acceleration
    def add_force(self, direction):
        # increase acceleration if player is under "speed" effect
        acceleration = Player.ACCELERATION
        if 'speed' in self.powerups:
            acceleration *= 5

        # assuming direction 0 is up, 1 is right, 2 is down, and 3 is left
        if direction == 0:
            self.acceleration[1] -= acceleration  # Adjust the value as needed
        elif direction == 1:
            self.acceleration[0] += acceleration
        elif direction == 2:
            self.acceleration[1] += acceleration
        elif direction == 3:
            self.acceleration[0] -= acceleration

    def get_rect(self):
        return self.movement_colliders

    # returns a list of objects colliding with each side of the player
    def get_all_colliding_objects(self, candidates):
        colliding = []
        for side in self.get_rect():
            indices = side.collidelistall([i.get_rect() for i in candidates])
            colliding.append([candidates[i] for i in indices])
        return colliding

    def handle_powerups(self):
        to_delete = []
        for i in self.powerups:
            # check if the effect should be over
            if self.powerups[i] + Powerup.effects_duration[i] <= time.perf_counter():
                to_delete.append(i)

        # delete effects that should be over
        for i in to_delete:

            # speed effect fix
            if i == 'speed':
                self.acceleration = [self.acceleration[0] / 5, self.acceleration[1] / 5]

            del self.powerups[i]

