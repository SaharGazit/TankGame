import math
import time

import pygame
from object import Object
from bullet import Bullet
from powerup import Powerup


class Player(Object):
    MAX_SPEED = 5.2
    ACCELERATION = 0.8

    def __init__(self, name, starting_position, monitor_info, main_player=False):
        # inherited from Object class
        super().__init__(starting_position, 0, (48, 48), pygame.image.load("../resources/tank_hull.png"), 1)

        # player data
        self.name = name  # player's name
        self.main_player = main_player  # true if this Player object belongs to the user of this program.

        # gameplay variables
        self.acceleration = [0, 0]
        self.speed_x = 0
        self.speed_y = 0
        self.powerups = {}  # list of powerup effects currently on the player.
        self.rotation = 0

        # technical
        self.monitor_info = monitor_info
        self.movement_colliders = [pygame.Rect(self.global_position[0] + 9, self.global_position[1] + 2, 30, 3), pygame.Rect(self.global_position[0] + 43, self.global_position[1] + 9, 3, 30), pygame.Rect(self.global_position[0] + 9, self.global_position[1] + 42, 30, 3), pygame.Rect(self.global_position[0] + 2, self.global_position[1] + 9, 3, 30)]
        self.turret_texture = pygame.image.load("../resources/tank_turret.png")

    # this function runs every game loop and is responsible for different continuous actions such as moving and rotating.
    def update(self, everything):
        self.move_player()
        self.rotate_by_mouse()
        self.handle_powerups()

        for coll in self.get_all_colliding_objects(everything):
            if type(coll) == Powerup:

                # add the powerup effect to the player
                self.powerups[coll.effect] = time.perf_counter()

                # speed effect fix
                if coll.effect == 'speed':
                    self.acceleration = [self.acceleration[0] * 5, self.acceleration[1] * 5]

                # destroy powerup
                coll.to_destroy = True

            if type(coll) == Bullet:
                if len(coll.wall_list) > 1 or coll.parent.id != self.id:
                    print("Hit by a bullet")
                    # TODO: bullet effects
                    coll.to_destroy = True

    def move_player(self):
        # increase maximum speed if player is under "speed" effect
        max_speed = Player.MAX_SPEED
        if 'speed' in self.powerups:
            max_speed += 5

        # increase or decrease speed by acceleration, and check that it doesn't pass the max/min speed.
        if -max_speed <= self.speed_x <= max_speed:
            self.speed_x += self.acceleration[0]
        if -max_speed <= self.speed_y <= max_speed:
            self.speed_y += self.acceleration[1]

        # increase or decrease position by speed. check if play is not blocked in the direction he goes to.
        if (self.speed_x > 0 and not self.block_collision[3]) or (self.speed_x < 0 and not self.block_collision[1]):
            self.global_position[0] += self.speed_x
        if (self.speed_y > 0 and not self.block_collision[0]) or (self.speed_y < 0 and not self.block_collision[2]):
            self.global_position[1] += self.speed_y

        # reduce speed by natural deceleration
        self.speed_x *= 0.940
        self.speed_y *= 0.940

        if -0.1 < self.speed_x < 0.1:
            self.speed_x = 0
        if -0.1 < self.speed_y < 0.1:
            self.speed_y = 0

        # update camera
        Object.camera_position = [22.5 + self.global_position[0] - self.monitor_info.current_w / 2, 22.5 + self.global_position[1] - self.monitor_info.current_h / 2]

        # reset all blockers
        for i in range(4):
            self.block_collision[i] = False

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

    def draw_object(self):
        # draw hull
        super().draw_object()

        # rotate the turret
        turret_sprite = pygame.transform.rotate(self.turret_texture, -self.rotation - 90)
        turret_rect = turret_sprite.get_rect(center=super().get_rect().center)
        # minor position fixes
        turret_rect.x -= 1
        turret_rect.y -= 1

        # draw turret
        Object.screen.blit(turret_sprite, turret_rect)
