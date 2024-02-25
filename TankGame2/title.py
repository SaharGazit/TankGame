import pygame


class Title:
    BACKGROUND_COLOR = (230, 230, 230)

    def main(self):
        class Button:
            FONT = pygame.font.Font("resources\\fonts\\font2.otf", 50)

            def __init__(self, position, scale, text="", text_position=0, texture=pygame.image.load("resources\\ui\\button.png")):
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
                screen_.blit(text_obj, (position[0] + self.text_position, position[1] + 25))

            # get the button's rect
            def get_rect(self):
                rect = self.png.get_rect()
                rect.x = self.position[0]
                rect.y = self.position[1]
                return rect

        class Window:
            FONT = pygame.font.Font("resources\\fonts\\font2.otf", 30)
            CON_TEXTURE = pygame.image.load("resources\\ui\\confirm.png")
            CAN_TEXTURE = pygame.image.load("resources\\ui\\cancel.png")
            OPT_TEXTURE = pygame.image.load("resources\\ui\\panel2.png")

            Texts = {"Play": "Select Mode:", "Account": "Coming Soon", "Quit": "Are you sure you want to quit?"}
            BUTTONS = {"Play": [Button((1150, 190), (400, 100), 'Online', 85, OPT_TEXTURE), Button((1150, 300), (400, 100), 'LAN', 135, OPT_TEXTURE), Button((1150, 410), (400, 100), 'DEBUG', 95, OPT_TEXTURE)], "Account": [], "Quit": [Button((1310.5, 170), (125, 125), texture=CON_TEXTURE), (Button((1584.5, 170), (125, 125), texture=CAN_TEXTURE))]}

            def __init__(self, button_type):
                self.png = pygame.transform.smoothscale(pygame.image.load("resources\\ui\\window.png"), (820, 1080))
                self.position = (1100, 0)
                self.top_text = Window.Texts[button_type]

                self.buttons = Window.BUTTONS[button_type]

            def draw_window(self, screen_):
                screen_.blit(self.png, self.position)
                text = Window.FONT.render(self.top_text, False, (0, 0, 0))
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
        title_font = pygame.font.Font("resources\\fonts\\font1.ttf", 90)

        # buttons and texts
        title_text = title_font.render('TANK GAME', False, (0, 0, 0))
        title_alpha = 255
        title_alpha_up = False

        play_button = Button((100, 400), (400, 100), 'Play', 115)
        secret_debug_held = False
        account_button = Button((100, 600), (400, 100), 'Account', 60)
        quit_button = Button((100, 800), (400, 100), 'Quit', 125)

        button_list = [play_button, account_button, quit_button]
        activated_window = None

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

                        # when there is an activated window, close it
                        else:
                            activated_window = None
                            button_list = button_list[:3]

                    # cancel debug holding
                    if event.key == pygame.K_b:
                        secret_debug_held = False

                if event.type == pygame.KEYDOWN:
                    # debug button held
                    if event.key == pygame.K_b:
                        secret_debug_held = True

                # left click events
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:

                        # check if another window is open
                        if activated_window is None:
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

                                    # quit case
                                    if len(button_list[3:]) == 2:
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

                if activated_window is None:
                    new_button_list = button_list
                else:
                    new_button_list = button_list[3:]
                # update buttons hovering
                for button in new_button_list:
                    button.hovered = False
                    if button.get_rect().collidepoint(mouse_x, mouse_y):
                        button.hovered = True

            # background
            screen.fill(Title.BACKGROUND_COLOR)

            # title (TANK GAME)
            title_text.set_alpha(title_alpha)
            screen.blit(title_text, (75, 75))
            if activated_window is None:
                # change title's alpha
                if title_alpha_up:
                    title_alpha += 1
                else:
                    title_alpha -= 1
                # change alpha direction
                if title_alpha <= 0 or title_alpha >= 255:
                    title_alpha_up = not title_alpha_up

            # side-window
            else:
                activated_window.draw_window(screen)

            # buttons
            for button in button_list[:-1]:
                button.draw_button(screen)
            # handle last button (may not appear)
            if not(len(button_list) == 6 and not secret_debug_held):
                button_list[-1].draw_button(screen)

            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    pygame.init()
    title = Title()
    title.main()
