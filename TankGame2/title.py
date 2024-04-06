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
        self.screen_number = 1

        # running process for current screen
        self.running = True
        self.error_code = 0
        self.activated_window = LobbyUI.Window("None")

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

        # buttons and texts
        title_font = pygame.font.Font(LobbyUI.title_font, 80)
        title_text = title_font.render('TANK GAME', False, (0, 0, 0))
        title_alpha = 255
        button_texture = pygame.image.load(LobbyUI.button_texture)
        play_button = Button('Play', (100, 400), (400, 100), button_texture, True, 115, True)
        account_button = Button('Account', (100, 600), (400, 100), button_texture, True, 60, True)
        quit_button = Button('Quit', (100, 800), (400, 100), button_texture, True, 125, True)

        # contains all visible buttons currently on the screen
        self.button_list = [play_button, account_button, quit_button]
        # TODO: have a screenshot from the game as a side-background (behind the window)

        self.activated_window = LobbyUI.Window("None")
        self.running = True
        while self.running:
            # handles pygame events
            self.event_handler()

            # background
            self.screen.fill(LobbyUI.background_color)

            # title (TANK GAME)
            title_text.set_alpha(abs(title_alpha))
            self.screen.blit(title_text, (75, 75))
            if self.activated_window.window_type == "None":
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

        # default window in the lobby is a lobby window
        self.activated_window = Window("Lobby")

        # button list
        self.button_list = self.activated_window.buttons

        self.running = True
        while self.running:
            self.event_handler()

            # background
            self.screen.fill(LobbyUI.background_color)

            # lobby's name, side window
            self.screen.blit(title_test, (30, 55))
            self.activated_window.draw_window(self.screen)

            # draw buttons
            for button in self.button_list:
                button.draw_button(self.screen)
            pygame.display.flip()

    # handles UI events that are similar in all screens
    def event_handler(self):
        def remove_window():
            if self.screen_number == 1:
                # remove the activated window
                self.activated_window = LobbyUI.Window("None")

                # remove all window buttons
                self.button_list = [b for b in self.button_list if b.static]

            # in the lobby screen, the side window can't be removed
            elif self.screen_number == 2:
                self.activated_window = LobbyUI.Window("Lobby")
                print("aaa")
                # remove all window buttons except lobby window buttons
                self.button_list = [b for b in self.button_list if b.static] + self.activated_window.buttons

        for event in pygame.event.get():
            # if user closes the window, stop the game from running.
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYUP:
                # actions for when the player presses Escape
                if event.key == pygame.K_ESCAPE:
                    # when there is no activated window, or the current window is the lobby window, open the quit confirmation window
                    if self.activated_window.window_type == "None" or self.activated_window.window_type == "Lobby":
                        self.activated_window = LobbyUI.Window(self.button_list[2].text)
                        self.button_list += self.activated_window.buttons
                        # fake quit button hovering
                        self.button_list[2].hovered = True

                    # when there is an activated window, close it
                    else:
                        remove_window()

            # left click events
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # check if player pressed inside the new window
                    if self.activated_window.get_rect().collidepoint(mouse_x, mouse_y):
                        for button in [a for a in self.button_list if not a.static]:
                            # get which button the player is clicking on, and activate it
                            if button.get_rect().collidepoint(mouse_x, mouse_y):

                                # host case: open a lobby server
                                if button.button_type == "Host":
                                    pass
                                # join case: open the lobby searching screen
                                if button.button_type == "Join":
                                    pass
                                # practice case: start the offline practice game
                                if button.button_type == "Practice":
                                    pass

                                # confirm quit case: stop running the program
                                if button.button_type == "ConfirmQuit":
                                    self.running = False
                                # cancel quit case: remove the quit window
                                elif button.button_type == "CancelQuit":
                                    remove_window()

                                # can only press one button at once
                                break

                    # remove the window, and check for main button interactions
                    else:
                        remove_window()

                        # pressed a main button
                        for button in [a for a in self.button_list if a.static]:
                            # activate the window that belongs to the button
                            if button.get_rect().collidepoint(mouse_x, mouse_y):
                                self.activated_window = LobbyUI.Window(button.text)
                                self.button_list += self.activated_window.buttons

            # update button hovering
            for button in [a for a in self.button_list if (not a.static or self.activated_window.window_type == "None")]:
                button.hovered = False
                if button.get_rect().collidepoint(mouse_x, mouse_y):
                    button.hovered = True

    class Button:
        def __init__(self, name, position, scale, texture, has_text=False, text_position=0, static=False):
            self.button_type = name
            self.png = pygame.transform.smoothscale(texture, scale)
            self.font = pygame.font.Font(LobbyUI.button_font, 50)
            self.position = position

            # true if the player's mouse is on the button
            self.hovered = False
            # true if the button doesn't depend on
            self.static = static

            # set text
            if has_text:
                self.text = name
            else:
                self.text = ""
            # TODO: replace this with text anchoring
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
                 "Lobby": "Game Info", "None": "None"}
        BUTTONS = {"Play": [['Host', (1150, 190), (400, 100), "opt", 115],
                            ['Join', (1150, 300), (400, 100), "opt", 125],
                            ['Practice', (1150, 410), (400, 100), "opt", 48]],
                   "Account": [],
                   "Quit": [['ConfirmQuit', (1310.5, 170), (125, 125), "con"],
                            ['CancelQuit', (1584.5, 170), (125, 125), "can"]],
                   "Lobby": [['Leave', (1750, 30), (125, 125), "can"]],
                   "None": []}

        def __init__(self, button_type):
            window_texture = pygame.image.load(LobbyUI.window_texture)
            self.window_type = button_type

            self.png = pygame.transform.smoothscale(window_texture, (820, 1080))
            self.position = (1100, 0)
            self.top_text = LobbyUI.Window.Texts[button_type]
            self.top_text_font = pygame.font.Font(LobbyUI.button_font, 30)

            self.buttons = []
            # TODO: I really don't like the way this code works. consider changing it in the future
            # get button attributes and set correct texture (this is required because static fonts can be initialized, due to the code structure)
            for button in LobbyUI.Window.BUTTONS[button_type]:
                if type(button[3]) == str:
                    exec(f"button[3] = pygame.image.load(LobbyUI.{button[3]}_texture)")
                if len(button) == 5:
                    self.buttons.append(LobbyUI.Button(button[0], button[1], button[2], button[3], True, button[4]))
                else:
                    self.buttons.append(LobbyUI.Button(button[0], button[1], button[2], button[3]))

        # incase the button type is None, these functions wouldn't run in the first place. (view event_handler)
        # prints the window on the screen
        def draw_window(self, screen_):
            screen_.blit(self.png, self.position)
            text = self.top_text_font.render(self.top_text, False, (0, 0, 0))
            screen_.blit(text, (1185, 90))

        # returns the Rect of the window object
        def get_rect(self):
            rect = self.png.get_rect()
            rect.x = self.position[0]
            rect.y = self.position[1]
            return rect


if __name__ == "__main__":
    lobby_ui = LobbyUI()
    lobby_ui.main(0)
