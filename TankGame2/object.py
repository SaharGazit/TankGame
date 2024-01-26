
import pygame


class Object:
    camera_position = [0, 0]
    screen_edges = [0, 0]  # marks the positions of the right side and the bottom of the screen
    screen = None  # pygame screen used to draw the objects

    def __init__(self, starting_position, rotation, scale, texture):
        self.global_position = starting_position  # global position in the world map
        self.rotation = rotation
        self.scale = scale  # size of the object
        self.to_destroy = False  # if true, the object is about to be removed from the objects list

        # PNG of the object
        self.texture = pygame.transform.smoothscale(texture, (self.scale[0], self.scale[1]))

    def draw_object(self):
        self.screen.blit(self.texture, self.local_position())

    # returns all objects that collide with this one
    def get_all_colliding_objects(self, candidates):
        indices = self.get_rect().collidelistall([i.get_rect() for i in candidates])
        return [candidates[i] for i in indices]

    # returns the local_position - the position of the object on the user's screen
    def local_position(self):
        return self.global_position[0] - Object.camera_position[0], self.global_position[1] - Object.camera_position[1]

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
        return local_position[0] + self.scale[0] > 0 and local_position[0] < Object.screen_edges[0] and local_position[1] + self.scale[1] > 0 and local_position[1] < Object.screen_edges[1]

    def update(self, everything):
        pass

    # marks the object to be destroyed
    def destroy(self):
        self.to_destroy = True
