import pygame


class LobbyUI:  # TODO: LobbyUI will inherit UI class (there should be a GameUI as well)
    # fonts
    button_font = "resources/fonts/font2.otf"
    title_font = "resources/fonts/font1.ttf"

    # textures
    button_texture = "resources/ui/button.png"
    window_texture = "resources/ui/window.png"
    con_texture = "resources/ui/confirm.png"
    can_texture = "resources/ui/cancel.png"
    opt_texture = "resources/ui/panel2.png"

    background_color = (230, 230, 230)

    def __init__(self):
        # initiate program
        pygame.init()
        pygame.display.set_caption('TANK GAME')

        # screen
        self.monitor_info = pygame.display.Info()
        self.screen = pygame.display.set_mode((int(self.monitor_info.current_w), int(self.monitor_info.current_h)))

        # running process for current screen
        self.running = True
        self.error_code = 0
        self.activated_window = None

        # list of available buttons
        self.button_list = []

    def main(self, temp=0):
        if temp == 0:
            # run title screen
            self.title()

        if temp == 1:
            # run lobby screen
            self.lobby('WizardTNT')

    def title(self):
        Button = LobbyUI.Button
        Window = LobbyUI.Window

        # buttons and texts
        title_font = pygame.font.Font(LobbyUI.title_font, 80)
        title_text = title_font.render('TANK GAME', False, (0, 0, 0))
        title_alpha = 255
        button_texture = pygame.image.load(LobbyUI.button_texture)
        play_button = Button((100, 400), (400, 100), button_texture, 'Play', 115)
        account_button = Button((100, 600), (400, 100), button_texture, 'Account', 60)
        quit_button = Button((100, 800), (400, 100), button_texture, 'Quit', 125)

        # contains all visible buttons currently on the screen
        self.button_list = [play_button, account_button, quit_button]
        # TODO: have a screenshot from the game as a side-background (behind the window)

        self.activated_window = None
        self.running = True
        while self.running:
            self.event_handler()

            # background
            self.screen.fill(LobbyUI.background_color)

            # title (TANK GAME)
            title_text.set_alpha(abs(title_alpha))
            self.screen.blit(title_text, (75, 75))
            if self.activated_window is None:
                # change title's transparency
                title_alpha -= 1
                # change transparency direction
                if title_alpha <= -255:
                    title_alpha = 255

            # side-window
            else:
                self.activated_window.draw_window(self.screen)

            # temp square at the corner TODO: resolution testing
            sq = pygame.Rect((self.screen.get_width() - 10, self.screen.get_height() - 10), (10, 10))
            pygame.draw.rect(self.screen, (255, 0, 0), sq)

            # draw buttons
            for button in self.button_list:
                button.draw_button(self.screen)

            # handle error codes
            if self.error_code == 1:
                pass

            pygame.display.flip()

    def lobby(self, owner):
        Button = LobbyUI.Button
        Window = LobbyUI.Window

        # fonts and texts
        title_font = pygame.font.Font(LobbyUI.button_font, 60)
        title_test = title_font.render(f"{owner}'s Game", False, (0, 0, 0))

        # one constant side window
        side_window = Window("Lobby")

        # button list
        button_list = side_window.buttons

        self.running = True
        while self.running:
            for event in pygame.event.get():
                # if user closes the window, stop the game from running.
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

            # background
            self.screen.fill(LobbyUI.background_color)

            # lobby's name, side window
            self.screen.blit(title_test, (30, 55))
            side_window.draw_window(self.screen)

            # draw buttons
            for button in button_list:
                button.draw_button(self.screen)
            pygame.display.flip()

    # handles UI events that are similar in all screens
    def event_handler(self):
        for event in pygame.event.get():
            # if user closes the window, stop the game from running.
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYUP:
                # actions for when the player presses Escape
                if event.key == pygame.K_ESCAPE:
                    # when there is no activated window, open the quit confirmation window
                    if self.activated_window is None:
                        self.activated_window = LobbyUI.Window(self.button_list[2].text)
                        self.button_list += self.activated_window.buttons
                        # fake quit button hovering
                        self.button_list[2].hovered = True

                    # when there is an activated window, close it
                    else:
                        self.activated_window = None
                        self.button_list = self.button_list[:3]

            # left click events
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # check if another window is open
                    if self.activated_window is None:
                        # pressed a main button
                        for button in self.button_list:
                            # activate the window that belongs to the button
                            if button.get_rect().collidepoint(mouse_x, mouse_y):
                                self.activated_window = LobbyUI.Window(button.text)
                                self.button_list += self.activated_window.buttons

                    # check if player pressed inside the new window
                    elif self.activated_window.get_rect().collidepoint(mouse_x, mouse_y):
                        for button in self.button_list[3:]:
                            # platform the button action
                            if button.get_rect().collidepoint(mouse_x, mouse_y):

                                # play case
                                if len(self.button_list) == 6:
                                    # TODO: HOST, JOIN AND PRACTICE
                                    pass

                                # quit case
                                if len(self.button_list) == 5:
                                    # confirm quit
                                    if self.button_list.index(button) == 3:
                                        self.running = False
                                    # cancel quit
                                    else:
                                        self.activated_window = None
                                        self.button_list = self.button_list[:3]

                    # remove window if player clicked outside it
                    else:
                        self.activated_window = None
                        self.button_list = self.button_list[:3]

            # set relevant button list
            if self.activated_window is None:
                new_button_list = self.button_list
            else:
                new_button_list = self.button_list[3:]

            # update button hovering
            for button in new_button_list:
                button.hovered = False
                if button.get_rect().collidepoint(mouse_x, mouse_y):
                    button.hovered = True

    class Button:
        def __init__(self, position, scale, texture, text="", text_position=0):
            self.png = pygame.transform.smoothscale(texture, scale)
            self.font = pygame.font.Font(LobbyUI.button_font, 50)
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
            text_obj = self.font.render(self.text, False, text_color)
            screen_.blit(text_obj, (position[0] + self.text_position, position[1] + 23))

        # get the button's rect
        def get_rect(self):
            rect = self.png.get_rect()
            rect.x = self.position[0]
            rect.y = self.position[1]
            return rect

    class Window:
        Texts = {"Play": "Select Option:", "Account": "Coming Soon", "Quit": "Are you sure you want to quit?",
                 "Lobby": "Game Info"}
        BUTTONS = {"Play": [[(1150, 190), (400, 100), "opt", 'Host', 115],
                            [(1150, 300), (400, 100), "opt", 'Join', 125],
                            [(1150, 410), (400, 100), "opt", 'Practice', 48]],
                   "Account": [],
                   "Quit": [[(1310.5, 170), (125, 125), "con"],
                            [(1584.5, 170), (125, 125), "can"]],
                   "Lobby": [[(1750, 30), (125, 125), "can"]]}

        def __init__(self, button_type):
            window_texture = pygame.image.load(LobbyUI.window_texture)
            self.png = pygame.transform.smoothscale(window_texture, (820, 1080))
            self.position = (1100, 0)
            self.top_text = LobbyUI.Window.Texts[button_type]
            self.top_text_font = pygame.font.Font(LobbyUI.button_font, 30)

            self.buttons = []
            # TODO: I really don't like the way this code works. consider changing it in the future
            # get button attributes and set correct texture (this is required because static fonts can be initialized, due to the code structure)
            for button in LobbyUI.Window.BUTTONS[button_type]:
                if type(button[2]) == str:
                    exec(f"button[2] = pygame.image.load(LobbyUI.{button[2]}_texture)")
                if len(button) == 5:
                    self.buttons.append(LobbyUI.Button(button[0], button[1], button[2], button[3], button[4]))
                else:
                    self.buttons.append(LobbyUI.Button(button[0], button[1], button[2]))

        def draw_window(self, screen_):
            screen_.blit(self.png, self.position)
            text = self.top_text_font.render(self.top_text, False, (0, 0, 0))
            screen_.blit(text, (1185, 100))

        def get_rect(self):
            rect = self.png.get_rect()
            rect.x = self.position[0]
            rect.y = self.position[1]
            return rect


if __name__ == "__main__":
    lobby_ui = LobbyUI()
    lobby_ui.main(0)
