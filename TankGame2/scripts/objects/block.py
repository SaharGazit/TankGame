import pygame
from TankGame2.objects.object import Object


class Block(Object):

    def __init__(self, starting_position, size):
        super().__init__(starting_position, 0, size, pygame.image.load("../resources/tankbody.png"))

