import pygame
from TankGame2.archive.client import Client


class Title:
    BACKGROUND_COLOR = (230, 230, 230)
    RS_DIRECTORY = "resources/"

    def __init__(self):
        self.error_code = 0

    def main(self):
        # load fonts
        font = pygame.font.Font(Title.RS_DIRECTORY + "fonts/font2.otf", 30)
        con_texture = pygame.image.load(Title.RS_DIRECTORY + "ui/confirm.png")
        can_texture = pygame.image.load(Title.RS_DIRECTORY + "ui/cancel.png")
        opt_texture = pygame.image.load(Title.RS_DIRECTORY + "ui/panel2.png")

        class Button:
            FONT = pygame.font.Font(Title.RS_DIRECTORY + "fonts/font2.otf", 50)

            def __init__(self, position, scale, text="", text_position=0, texture=pygame.image.load(Title.RS_DIRECTORY + "ui/button.png")):
                self.png = pygame.transform.smoothscale(texture, scale)
                self.position = position

                # true if the player's mouse is on the button
                self.hovered = False

                self.text = text
                self.text_position = text_position

            def draw_button(self, screen_):
                # change button attributes if they are hovered
                if self.hovered:
                    text_color = (148, 5, 0)
                    position = (self.position[0], self.position[1] + 5)
                else:
                    text_color = (4, 0, 87)
                    position = self.position

                # draw the button and its text with fixed positions
                screen_.blit(self.png, position)
                text_obj = button.FONT.render(self.text, False, text_color)
                screen_.blit(text_obj, (position[0] + self.text_position, position[1] + 12))

            # get the button's rect
            def get_rect(self):
                rect = self.png.get_rect()
                rect.x = self.position[0]
                rect.y = self.position[1]
                return rect

        class Window:
            Texts = {"Play": "Select Option:", "Account": "Coming Soon", "Quit": "Are you sure you want to quit?"}
            BUTTONS = {"Play": [Button((1150, 190), (400, 100), 'Online', 85, opt_texture), Button((1150, 300), (400, 100), 'LAN', 135, opt_texture), Button((1150, 410), (400, 100), 'PRACTICE', 48, opt_texture)], "Account": [], "Quit": [Button((1310.5, 170), (125, 125), texture=con_texture), (Button((1584.5, 170), (125, 125), texture=can_texture))]}

            def __init__(self, button_type):
                self.png = pygame.transform.smoothscale(pygame.image.load(Title.RS_DIRECTORY + "ui/window.png"), (820, 1080))
                self.position = (1100, 0)
                self.top_text = Window.Texts[button_type]

                self.buttons = Window.BUTTONS[button_type]

            def draw_window(self, screen_):
                screen_.blit(self.png, self.position)
                text = font.render(self.top_text, False, (0, 0, 0))
                screen_.blit(text, (1185, 100))

            def get_rect(self):
                rect = self.png.get_rect()
                rect.x = self.position[0]
                rect.y = self.position[1]
                return rect

        # initiate program
        pygame.init()
        pygame.display.set_caption('TANK GAME')

        # technical
        monitor_info = pygame.display.Info()
        screen = pygame.display.set_mode((int(monitor_info.current_w), int(monitor_info.current_h)))
        tank_game_font = pygame.font.Font(Title.RS_DIRECTORY + "fonts/font1.ttf", 90)

        # buttons and texts
        title_text = tank_game_font.render('TANK GAME', False, (0, 0, 0))
        title_alpha = 255

        play_button = Button((100, 400), (400, 100), 'Play', 115)
        account_button = Button((100, 600), (400, 100), 'Account', 60)
        quit_button = Button((100, 800), (400, 100), 'Quit', 125)
        cancel_queue_button = Button((1447.5, 900), (125, 125), texture=can_texture)

        cancel_text = font.render('Waiting for Opponent', False, (255, 102, 102))
        error1_test = font.render("Server is Offline", False, (128, 0, 0))

        # contains all visible buttons currently on the screen
        button_list = [play_button, account_button, quit_button]
        # contains all visual sprites (like tanks and bullets) for decoration purposes # TODO: add bullets and turrets
        decoration_sprites = [pygame.transform.scale(pygame.image.load(f"{title.RS_DIRECTORY}/objects/box.png"), (100, 100)),
                              pygame.transform.scale(pygame.image.load(f"{title.RS_DIRECTORY}/objects/tank_hull.png"), (48, 48)),
                              pygame.transform.scale(pygame.image.load(f"{title.RS_DIRECTORY}/objects/tank_hull.png"), (48, 48)),
                              pygame.transform.scale(pygame.image.load(f"{title.RS_DIRECTORY}/objects/box.png"), (100, 100)),
                              pygame.transform.scale(pygame.image.load(f"{title.RS_DIRECTORY}/objects/speed.png"), (32, 32))]
        decoration_sprites_positions = [(1300, 350), (1600, 150), (1100, 500), (1650, 570), (1500, 600)]


        activated_window = None
        client = None
        waiting = False
        running = True
        while running:
            # buttons, keys and mouse effects
            for event in pygame.event.get():
                # if user closes the window, stop the game from running.
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYUP:
                    # actions for when the player presses Escape
                    if event.key == pygame.K_ESCAPE:
                        # when there is no activated window, open the quit confirmation window
                        if activated_window is None:
                            activated_window = Window(quit_button.text)
                            button_list += activated_window.buttons
                            # fake quit button hovering
                            quit_button.hovered = True

                        # cancel queue
                        elif waiting:
                            waiting = False
                            client.force_stop_queueing = True

                        # when there is an activated window, close it
                        else:
                            activated_window = None
                            button_list = button_list[:3]
                            self.error_code = 0

                    # cancel debug holding
                    if event.key == pygame.K_b:
                        secret_debug_held = False

                if event.type == pygame.KEYDOWN:
                    # debug button held
                    if event.key == pygame.K_b and not waiting:
                        secret_debug_held = True

                # left click events
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:

                        # if the player is waiting, the only available button is the one canceling the queue
                        if waiting:
                            if cancel_queue_button.get_rect().collidepoint(mouse_x, mouse_y):
                                waiting = False
                                client.force_stop_queueing = True

                        # check if another window is open
                        elif activated_window is None:
                            # pressed a main button
                            for button in button_list:
                                # activate the window that belongs to the button
                                if button.get_rect().collidepoint(mouse_x, mouse_y):
                                    activated_window = Window(button.text)
                                    button_list += activated_window.buttons

                        # check if player pressed inside the new window
                        elif activated_window.get_rect().collidepoint(mouse_x, mouse_y):
                            for button in button_list[3:]:
                                # platform the button action
                                if button.get_rect().collidepoint(mouse_x, mouse_y):

                                    # play case
                                    if len(button_list) == 6:
                                        pass

                                    # quit case
                                    if len(button_list) == 5:
                                        # confirm quit
                                        if button_list.index(button) == 3:
                                            running = False
                                        # cancel quit
                                        else:
                                            activated_window = None
                                            button_list = button_list[:3]

                        # remove window if player clicked outside it
                        else:
                            activated_window = None
                            button_list = button_list[:3]
                            self.error_code = 0

                # set relevant button list
                if activated_window is None:
                    new_button_list = button_list
                elif waiting:
                    new_button_list = [cancel_queue_button]
                else:
                    new_button_list = button_list[3:]

                # update button hovering
                for button in new_button_list:
                    button.hovered = False
                    if button.get_rect().collidepoint(mouse_x, mouse_y):
                        button.hovered = True

            # background decoration
            screen.fill(Title.BACKGROUND_COLOR)
            for i in range(len(decoration_sprites)):
                screen.blit(decoration_sprites[i], decoration_sprites_positions[i])

            # title (TANK GAME)
            title_text.set_alpha(abs(title_alpha))
            screen.blit(title_text, (75, 75))
            if activated_window is None:
                # change title's transparency
                title_alpha -= 1
                # change transparency direction
                if title_alpha <= -255:
                    title_alpha = 255

            # side-window
            else:
                activated_window.draw_window(screen)

            # temp square at the corner
            sq = pygame.Rect((screen.get_width() - 10, screen.get_height() - 10), (10, 10))
            pygame.draw.rect(screen, (255, 0, 0), sq)

            # draw buttons
            for button in button_list:
                button.draw_button(screen)

            if waiting:
                # cancel button and message
                screen.blit(cancel_text, (1276, 830))
                cancel_queue_button.draw_button(screen)

            # handle error codes
            if self.error_code == 1:
                waiting = False
                screen.blit(error1_test, (1330, 830))


            pygame.display.flip()
        pygame.quit()


if __name__ == "__main__":
    pygame.init()
    title = Title()
    title.main()
