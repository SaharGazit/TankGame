import pygame
from TankGame2.object import Object, Player, Powerup, Bullet, Block


class Game:
    SCREEN_DIVIDER = 1

    def __init__(self, screen, client):
        self.screen = screen
        self.client = client
        if client is None:
            self.practice = True
        elif client.connected:
            self.practice = False
        else:
            self.practice = True

        self.exit_code = 0

    def main(self):  # (pygame is initialized beforehand)
        # object screen settings
        screen_size = self.screen.get_size()
        Object.screen_size = screen_size
        Object.screen = self.screen

        this_player_start_positions = [0, 0]
        if not self.client.offline_mode:
            # get starter positions
            positions = self.client.get_buffer_data(False)

            # get own position
            for pos in positions:
                pos = pos.split('|')
                if pos[0] == self.client.name:
                    this_player_start_positions = [int(pos[1]), int(pos[2])]

        # objects currently on the map
        this_player = Player("PLAYER", this_player_start_positions, True)
        objects = [this_player, Block((500, 500), (100, 100), "wall", 0), Block((700, 500), (100, 100), "wall", 1), Block((1100, 500), (100, 100), "box", 2), Block((1300, 500), (100, 100), "box", 3), Powerup((1000, 1000), 'speed')]

        # clock
        clock = pygame.time.Clock()


        # main game loop
        while self.exit_code == 0:
            for event in pygame.event.get():
                # if user closes the window, stop the game from running.
                if event.type == pygame.QUIT:
                    self.exit_code = -1

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
                    if event.key == pygame.K_k:
                        this_player.global_position[1] -= 10  # temp

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
                        # TODO: pause menu
                        self.exit_code = 1

                # pressing left mouse buttons shoots a bullet
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # (1 = left mouse click)
                        # creates a bullet with the position and rotation of the player
                        objects.append(Bullet(this_player))

            # game remains at 60 FPS
            clock.tick(60)
            # clears out the screen every game loop
            self.screen.fill((159, 168, 191))

            if not self.client.offline_mode:
                # loop for handling server data
                for data in self.client.get_buffer_data():
                    print(data)

                # send personal data to server
                self.client.send_player_status(f"{this_player.global_position[0]}, {this_player.global_position[1]}")

            # loop for handling every object
            for o in objects[1:] + [this_player]:  # the player is "pushed" to the end in order to draw it last

                # prevents the object from colliding with itself
                potential_collisions = list(objects)  # TODO: move this into the object's class?
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

        # return exit code to the lobby when the main loop is over
        return self.exit_code
