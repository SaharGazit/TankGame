import pygame
from player import Player
from block import Block
from bullet import Bullet
from object import Object
from powerup import Powerup


class Game:
    SCREEN_DIVIDER = 1

    def __init__(self, client):
        self.monitor_info = None
        self.screen = None

        self.client = client

    def main(self):
        # initiate program
        pygame.init()
        pygame.display.set_caption('TANK GAME')

        # screen settings
        self.monitor_info = pygame.display.Info()
        Object.screen_edges = [self.monitor_info.current_w, self.monitor_info.current_h]
        self.screen = pygame.display.set_mode((int(self.monitor_info.current_w / Game.SCREEN_DIVIDER), int(self.monitor_info.current_h / Game.SCREEN_DIVIDER)))
        Object.screen = self.screen

        # objects currently on the map
        this_player = Player("PLAYER", [self.monitor_info.current_w / 2 - 22.5, self.monitor_info.current_h / 2 - 22.5], self.monitor_info, True)
        objects = [this_player, Block((500, 500), (100, 100), "wall", 0), Block((700, 500), (100, 100), "wall", 1), Block((1100, 500), (100, 100), "box", 2), Block((1300, 500), (100, 100), "box", 3), Powerup((1000, 1000), 'speed')]

        # clock
        clock = pygame.time.Clock()

        # main game loop
        running = True
        while running:
            for event in pygame.event.get():
                # if user closes the window, stop the game from running.
                if event.type == pygame.QUIT:
                    running = False

                # WASD keys for moving with the player. the player receives acceleration by pressing down a key.
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        this_player.add_force(0)
                    if event.key == pygame.K_d:
                        this_player.add_force(1)
                    if event.key == pygame.K_s:
                        this_player.add_force(2)
                    if event.key == pygame.K_a:
                        this_player.add_force(3)

                # the player loses acceleration (accelerated backwards) by un-pressing a key
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_w:
                        this_player.add_force(2)
                    if event.key == pygame.K_d:
                        this_player.add_force(3)
                    if event.key == pygame.K_s:
                        this_player.add_force(0)
                    if event.key == pygame.K_a:
                        this_player.add_force(1)

                    # pressing escape will also exit the game
                    if event.key == pygame.K_ESCAPE:
                        running = False

                # pressing left mouse buttons shoots a bullet
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # (1 = left mouse click)
                        # creates a bullet with the position and rotation of the player
                        shooter_pos = this_player.global_position
                        objects.append(Bullet([shooter_pos[0] + (this_player.scale[0] / 2 - Bullet.SCALE[0] / 2), shooter_pos[1] + (this_player.scale[1] / 2 - Bullet.SCALE[1] / 2)], this_player.rotation))

            # game remains at 60 FPS
            clock.tick(60)
            # clears out the screen every game loop
            self.screen.fill((159, 168, 191))

            # loop for handling every object
            for o in objects[1:] + [this_player]:  # the player is "pushed" to the end in order to draw it last

                # prevents the object from colliding with itself
                potential_collisions = list(objects)
                potential_collisions.remove(o)
                # update object
                o.update(potential_collisions)

                # destroy object if needed by removing it from the objects list
                if o.to_destroy:
                    objects.remove(o)

                # draw object
                if o.in_screen():
                    o.draw_object()

            # update screen
            pygame.display.flip()

        # when main game loop is finished, close pygame
        pygame.quit()


if __name__ == "__main__":
    game = Game(None)
    game.main()
