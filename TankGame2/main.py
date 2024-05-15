import pygame
from object import Object, Player, Powerup, Bullet, Block


class Game:

    def __init__(self, screen, client):
        self.screen = screen
        self.client = client
        if client is None:
            self.practice = True
        elif client.running_udp:
            self.practice = False
        else:
            self.practice = True

        self.exit_code = 0

    def main(self):  # (pygame is initialized beforehand)
        # object screen settings
        screen_size = self.screen.get_size()
        Object.screen_size = screen_size
        Object.scale_factor = (screen_size[0] / 1920, screen_size[1] / 1080)
        Object.screen = self.screen

        this_player_start_positions = [0, 0]
        if not self.practice:
            # get starter positions
            positions = self.client.get_buffer_data(False)

            # get own position
            for pos in positions:
                pos = pos.split('|')
                if pos[0] == self.client.name:
                    this_player_start_positions = [int(pos[1]), int(pos[2])]

            # start voice listener
            self.client.start_voice_client()

        # objects currently on the map
        this_player = Player(self.client.name, this_player_start_positions)
        other_players = []
        objects = [this_player, Block((500, 500), (100, 100), "wall", 0), Block((700, 500), (100, 100), "wall", 1), Block((1100, 500), (100, 100), "box", 2), Block((1300, 500), (100, 100), "box", 3), Powerup((1000, 1000), 'heal')]

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
                        # creates a bullet with the position and rotation of the player, and creates a bullet shoot event
                        objects.append(Bullet(this_player))
                        if not self.practice:
                            self.trigger_event("shoot")

            # game remains at 60 FPS
            clock.tick(60)
            # clears out the screen every game loop
            self.screen.fill((159, 168, 191))

            if not self.practice:
                # loop for handling server data
                for data in self.client.get_buffer_data():

                    # if the message starts with G, it is a player update
                    if data[0] == "G":
                        data = data.split('|')
                        # find right player
                        found = False
                        for player in other_players:
                            if player.name == data[1]:
                                found = True
                                # update player position and rotation
                                player.global_position = [float(data[2]), float(data[3])]
                                player.rotation = float(data[4])
                                break
                        # if player doesn't exist, check if they are a user in the lobby
                        if not found:
                            for i in range(2):
                                for player in self.client.user_list[i]:
                                    # if they're a user in the lobby, add them to the play list
                                    if player.name == data[1]:
                                        other_players.append(Player(player.name, [float(data[2]), float(data[3])], False))
                                        break

                    # if the message starts with L, it is a lobby update
                    elif data[0] == "L":
                        self.client.update_lobby(data)

                        # remove players the no longer exist (they left)
                        for player in other_players:
                            if player.name not in [a.name for a in self.client.user_list[0] + self.client.user_list[1]]:
                                other_players.remove(player)

                    # handle events
                    elif data[0] == 'E':
                        data = data.split("|")
                        # shooting
                        if data[1] == 's':
                            for p in other_players:
                                if p.name == data[2]:
                                    objects.append(Bullet(p))

                    else:
                        print(data)

                # send personal data to server
                self.client.send_player_status(f"{round(this_player.global_position[0], 2)}|{round(this_player.global_position[1], 2)}|{round(this_player.rotation, 2)}|")

            # handling objects
            for o in objects[1:] + other_players + [this_player]:  # the players are "pushed" to the end in order to draw them last

                # prevents the object from colliding with itself
                potential_collisions = list(objects + other_players)
                potential_collisions.remove(o)

                o.update(potential_collisions)

                # destroy object if needed by removing it from the objects list
                if o.to_destroy:
                    if o in objects:
                        objects.remove(o)
                    elif o in other_players:
                        other_players.remove(o)

                # draw object
                if o.in_screen():
                    o.draw_object()

            # update screen
            pygame.display.flip()

        if self.exit_code == 1 and not self.practice:
            # disconnect from udp server, if it opened
            self.client.disconnect_udp()
            self.client.stop_voice_client()
            # notify server about leaving the game
            self.client.send_data("main")

        # return exit code to the lobby when the main loop is over
        return self.exit_code

    def trigger_event(self, action):
        self.client.send_data(f"E|{action[0]}")


