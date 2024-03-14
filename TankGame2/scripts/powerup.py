from object import Object
import pygame


class Powerup(Object):
    effects_duration = {'speed': 5}

    def __init__(self, starting_position, effect):
        # inherited from Object class
        super().__init__(starting_position, 0, (32, 32), pygame.image.load("../resources/speed.png"))

        self.effect = effect  # the effect the player would receive as they take the powerup.
        self.duration = Powerup.effects_duration[effect]  # the duration the effect would stay on the player
