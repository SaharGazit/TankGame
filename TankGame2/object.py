import pygame
import math
import time


class Object:
    SPRITE_DIRECTORY = "resources/objects"
    UI_DIRECTORY = "resources/ui"

    camera_position = [0, 0]
    screen = None  # pygame screen used to draw the objects
    screen_size = None
    scale_factor = None

    def __init__(self, starting_position, rotation, scale, texture, object_id):
        self.id = object_id
        self.global_position = starting_position  # global position in the world map
        self.rotation = rotation
        self.scale = (int(scale[0] * Object.scale_factor[0]), int(scale[1] * Object.scale_factor[1]))  # size of the object
        self.to_destroy = False  # if true, the object is about to be removed from the objects list

        # PNG of the object
        self.texture = pygame.transform.scale(texture, self.scale)
        self.block_collision = [False, False, False, False]

    def draw_object(self):
        self.screen.blit(self.texture, self.local_position())

    # returns all objects that collide with this one
    def get_all_colliding_objects(self, candidates):
        indices = self.get_rect().collidelistall([i.get_rect() for i in candidates])
        return [candidates[i] for i in indices]

    # returns the local_position - the position of the object on the user's screen
    def local_position(self):
        # return self.global_position[0] - Object.camera_position[0], self.global_position[1] - Object.camera_position[1]
        return (self.global_position[0] - Object.camera_position[0]) * Object.scale_factor[0], (self.global_position[1] - Object.camera_position[1]) * Object.scale_factor[1]

    # returns the rect. takes already existing rect from the object's texture, and adds the rect position
    def get_rect(self):
        rect = self.texture.get_rect()
        local_position = self.local_position()
        rect.x = local_position[0]
        rect.y = local_position[1]
        return rect

    # checks if the object is in the screen
    def in_screen(self):
        local_position = self.local_position()
        return local_position[0] + self.scale[0] > 0 and local_position[0] < Object.screen_size[0] and local_position[1] + self.scale[1] > 0 and local_position[1] < Object.screen_size[1]

    def update(self, everything):
        pass

    # get distance between two objects using the Pythagorean theorem
    @staticmethod
    def distance(obj1, obj2):
        return math.sqrt(math.pow(obj2.global_position[0] - obj1.global_position[0], 2) + math.pow(obj2.global_position[1] - obj1.global_position[1], 2))

    @staticmethod
    def local_to_global(local):
        return [(local[0] + Object.camera_position[0]) / Object.scale_factor[0], (local[1] + Object.camera_position[1]) / Object.scale_factor[1]]


class Player(Object):
    MAX_SPEED = 5.2
    ACCELERATION = 0.8
    DEFAULT_HP = 3
    next_player_id = 1

    name_colors = [(50, 50, 50), (0, 0, 255), (177, 0, 0)]

    def __init__(self, user, starting_position, main=True):
        # inherited from Object class
        super().__init__(starting_position, 0, (48, 48), pygame.image.load(f"{Object.SPRITE_DIRECTORY}/tank_hull.png"), Player.next_player_id)
        Player.next_player_id += 1

        # player's user
        self.user = user
        # name
        name_font = pygame.font.Font("resources/fonts/font2.otf", int(15 * Object.scale_factor[0]))
        self.name_text = name_font.render(user.name, False, Player.name_colors[user.team])
        self.name_size = name_font.size(user.name)

        # movement
        self.acceleration = [0, 0]
        self.speed_x = 0
        self.speed_y = 0

        # player info
        self.main = main
        self.max_hp = Player.DEFAULT_HP
        self.hp = self.max_hp
        self.alive = True
        self.powerups = {}  # list of powerup effects currently on the player.

        # turret texture
        self.turret_texture = pygame.image.load(f"{Object.SPRITE_DIRECTORY}/tank_turret.png")

    # this function runs every game loop and is responsible for different continuous actions such as moving and rotating.
    def update(self, everything):
        if self.main:
            self.move_player()
            self.rotate_by_mouse()
            self.handle_powerups()
            self.draw_player_ui()
        else:
            main = everything[0]
            if self.alive or not main.alive:
                # update volume factor according to distance
                self.user.set_volume_factor(self.distance(main, self))
            else:
                # mute voice if the player is a ghost, and main player isn't one
                self.user.set_volume_factor(1000)

        if self.alive:
            for coll in self.get_all_colliding_objects(everything):
                if type(coll) == Powerup:

                    # add the powerup effect to the player
                    self.powerups[coll.effect] = time.perf_counter()

                    # speed powerup (increases acceleration and max speed)
                    if coll.effect == 'speed':
                        self.acceleration = [self.acceleration[0] * 5, self.acceleration[1] * 5]

                    # heal powerup (refills hp)
                    elif coll.effect == "heal":
                        # refills hp unless it is already at max value
                        if self.hp < self.max_hp:
                            self.hp = self.max_hp
                        else:
                            # skip destroy object
                            continue

                    # 1up powerup (adds 1 to max hp)
                    elif coll.effect == "1up":
                        self.max_hp += 1
                        self.hp += 1

                    # destroy powerup
                    coll.to_destroy = True

                # bullet hit decreases hp
                if type(coll) == Bullet:
                    # checks if the bullet belongs to a different player, or if the bullet hit another wall
                    # this is to prevent the bullet from colliding with the shooter
                    if len(coll.wall_list) > 1 or coll.parent.user.team != self.user.team:
                        # decrease hp by 1. if hp drops to 0, player is dead
                        self.hp -= 1 + coll.fire
                        if self.hp <= 0:
                            self.kill()
                        # destroy bullet
                        coll.to_destroy = True

                if type(coll) == Block:
                    side = coll.get_side(self)
                    self.block_collision[side] = True  # prevent moving in this direction

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
        campos_x = self.scale[0] / 2 + self.global_position[0] - Object.screen_size[0] / (2 * Object.scale_factor[0])
        campos_y = self.scale[1] / 2 + self.global_position[1] - Object.screen_size[1] / (2 * Object.scale_factor[1])
        Object.camera_position = [campos_x, campos_y]

        # reset all blockers
        for i in range(4):
            self.block_collision[i] = False

    # sets the rotation of the player by the mouse position
    def rotate_by_mouse(self):
        # get mouse position
        target = pygame.mouse.get_pos()

        # calculate distance between mouse and player
        c = self.local_position()
        x_distance = target[0] - (c[0] + 22.5 * Object.scale_factor[0])
        y_distance = target[1] - (c[1] + 22.5 * Object.scale_factor[1])

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
        center = super().get_rect().center
        turret_sprite = pygame.transform.rotate(self.turret_texture, -self.rotation - 90)
        turret_rect = turret_sprite.get_rect(center=center)
        # scale turret
        turret_sprite = pygame.transform.scale(turret_sprite, (int(turret_rect.width * Object.scale_factor[0]), int(turret_rect.height * Object.scale_factor[1])))
        turret_rect = turret_sprite.get_rect(center=center)

        # draw name
        Object.screen.blit(self.name_text, (center[0] - self.name_size[0] / 2, center[1] + 30 * self.scale_factor[1]))

        # draw turret
        Object.screen.blit(turret_sprite, turret_rect)

    # draw in-game ui (for example, hp hearts)
    def draw_player_ui(self):
        hp_texture = pygame.image.load(f"{Object.UI_DIRECTORY}/hitpoint.png")
        ehp_texture = pygame.image.load(f"{Object.UI_DIRECTORY}/empty_hitpoint.png")
        hp_sprite = pygame.transform.scale(hp_texture, (int(70 * Object.scale_factor[0]), int(70 * Object.scale_factor[1])))
        ehp_sprite = pygame.transform.scale(ehp_texture, (int(70 * Object.scale_factor[0]), int(70 * Object.scale_factor[1])))
        # draw full hit points
        for i in range(self.hp):
            Object.screen.blit(hp_sprite, ((100 * i + 30) * self.scale_factor[0], 25 * self.scale_factor[1]))
        # draw empty hit points
        for i in range(self.max_hp - self.hp):
            Object.screen.blit(ehp_sprite, ((100 * (self.hp + i) + 30) * self.scale_factor[0], 25 * self.scale_factor[1]))

    def kill(self):
        # in case the player was killed while having more than 0 hp
        if self.hp != 0:
            self.hp = 0

        self.alive = False

        # make player components transparent
        self.texture.set_alpha(100)
        self.turret_texture.set_alpha(100)
        self.name_text.set_alpha(100)


class Block(Object):
    CORNER_FIX = 1

    def __init__(self, starting_position, size, block_type, block_id):
        super().__init__(starting_position, 0, size, pygame.image.load(f"{Object.SPRITE_DIRECTORY}/{block_type}.png"), block_id)

        self.block_type = block_type
        # list of colliders from every direction
        self.side_colliders = []

    # def update(self, everything):
    #     # update side colliders
    #     local = self.local_position()
    #     self.side_colliders = [pygame.Rect(local[0] + 6, local[1] - 4, 89, 4),
    #                            pygame.Rect(local[0] + 101, local[1] + 6, 4, 89),
    #                            pygame.Rect(local[0] + 6, local[1] + 101, 89, 4),
    #                            pygame.Rect(local[0] - 4, local[1] + 6, 4, 89)]

        # # get collided object lists
        # collide_list = self.get_all_colliding_objects(everything)
        # for side in range(4):  # checks through every side of the block
        #     for collided in collide_list[side]:  # checks every object that collided with this side
        #
        #         # bullet collision with a block
        #         if type(collided) == Bullet:
        #             if self.block_type == "wall":
        #                 # check if the last wall this bullet has hit is not this one, to prevent the bullet from glitching inside the block
        #                 if collided.wall_list[-1] != self.id:
        #                     collided.wall_list.append(self.id)  # add this wall to the bullet's wall list
        #                     collided.block_collision[side] = True  # "tell" the bullet to change direction accordingly
        #             elif self.block_type == "box":
        #                 # destroy bullet
        #                 collided.to_destroy = True
        #
        #         # player collision with a block
        #         if type(collided) == Player:
        #             # prevent player from moving to the direction of the block
        #             collided.block_collision[side] = True

    def draw_object(self, debug_colliders=False):
        if debug_colliders:
            # for collider in self.side_colliders:
            #     pygame.draw.rect(Object.screen, (255, 255, 255), collider)
            pygame.draw.rect(Object.screen, (255, 0, 0), self.get_rect())

        super().draw_object()

    # returns at which side of the block another object is (top, right, bottom, left)
    def get_side(self, obj: Object):
        # get the top left and the bottom right corners of the block and the referenced object
        block_corner = self.local_position()[0] + self.scale[0] - 3 * Object.scale_factor[0], self.local_position()[1] + self.scale[1] - 3 * Object.scale_factor[1]
        obj_corner = obj.local_position()[0] + obj.scale[0] - 3 * Object.scale_factor[0], obj.local_position()[1] + obj.scale[1] - 3 * Object.scale_factor[1]

        # on the top side
        if self.local_position()[1] + 2 * Object.scale_factor[1] > obj_corner[1]:
            return 0
        # on the right side
        if block_corner[0] < obj.local_position()[0]:
            return 1
        # on the bottom side
        if block_corner[1] < obj.local_position()[1]:
            return 2
        # on the left side
        if self.local_position()[0] + 2 * Object.scale_factor[0] > obj_corner[0]:
            return 3

    # blocks have a bigger collider than their sprite
    def get_rect(self):
        rect = pygame.Rect(0, 0, self.scale[0] + 10 * Object.scale_factor[0], self.scale[1] + 10 * Object.scale_factor[1])
        rect.x = self.local_position()[0] - 5 * Object.scale_factor[0]
        rect.y = self.local_position()[1] - 5 * Object.scale_factor[1]

        return rect


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
        bullet_position = [parent.global_position[0] + (parent.scale[0] / 2 - Bullet.SCALE[0] * Object.scale_factor[0] / 2), parent.global_position[1] + (parent.scale[1] / 2 - Bullet.SCALE[1] * Object.scale_factor[1] / 2)]
        bullet_position[0] += self.x_speed * Bullet.DISTANCE_FROM_CENTER * Object.scale_factor[0]
        bullet_position[1] += self.y_speed * Bullet.DISTANCE_FROM_CENTER * Object.scale_factor[1]

        super().__init__(bullet_position, parent.rotation, Bullet.SCALE, pygame.image.load(f"{Object.SPRITE_DIRECTORY}/bullet.png"), 0)
        # fire bullet
        self.fire = "strength" in parent.powerups.keys()
        self.fire_texture = pygame.image.load(f"{Object.SPRITE_DIRECTORY}/fire_bullet.png")
        self.fire_texture = pygame.transform.scale(self.fire_texture, self.scale)

        # The player who shot the bullet
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
            self.to_destroy = True
        # reverse the bullets speed when it hits a wall
        if self.block_collision[0] or self.block_collision[2]:
            self.y_speed *= -1
        if self.block_collision[1] or self.block_collision[3]:
            self.x_speed *= -1

        # reset block collisions
        self.block_collision = [False, False, False, False]

        # handle collisions
        for coll in self.get_all_colliding_objects(everything):

            # collision with another bullet (destruction)
            if type(coll) == Bullet:
                self.to_destroy = True
                coll.to_destroy = True

            # collision with a block
            elif type(coll) == Block:
                # collision with a box block (destruction)
                if coll.block_type == "box":
                    self.to_destroy = True
                # collision with a wall block (bouncing)
                # requires the last wall in the bullet's wall list to be a different wall (or not wall)
                elif coll.block_type == "wall" and coll.id != self.wall_list[-1]:
                    side = coll.get_side(self)
                    if side is None:  # if bullet is shot inside a block (destruction)
                        self.to_destroy = True
                    else:
                        self.block_collision[coll.get_side(self)] = True  # "tell" the bullet to change direction accordingly
                        self.wall_list.append(coll.id)  # add this wall to the bullet's wall list

    def draw_object(self):
        if self.fire:
            self.screen.blit(self.fire_texture, self.local_position())
        else:
            super().draw_object()



class Powerup(Object):
    effects_duration = {'speed': 5, "heal": 0, "1up": 0, 'strength': 5}


    def __init__(self, starting_position, effect):
        # inherited from Object class
        super().__init__(starting_position, 0, (32, 32), pygame.image.load(f"{Object.SPRITE_DIRECTORY}/{effect}.png"), 0)

        self.effect = effect  # the effect the player would receive as they take the powerup.
        self.duration = Powerup.effects_duration[effect]  # the duration the effect would stay on the player


