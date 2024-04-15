import pygame
import main
from testing.client import Client


class LobbyUI:
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
        self.screen_name = "title" # determines which screen to print and interact with

        # running process for current screen
        self.activated_window = LobbyUI.Window("None")
        self.exit_code = 0  # equals 0 while the program is running. after the program finishes, it determines what to do next

        # list of available buttons
        self.button_list = []

        # client
        self.client = Client()
        self.name = "Guest"

    def main(self):
        # connect to the server
        self.client.connect()

        # get account data
        if self.client.offline_mode:
            self.name = "guest"
        else:
            self.name = self.client.get_buffer_data(False)[0]

        arguments = ""
        running = True
        while running:
            # executes the current screen function
            exec(f"self.{self.screen_name}({arguments})")

            # code -1: shut down program immediately
            if self.exit_code == -1:
                running = False
            # code 0: program running. not supposed to reach this point with code 0
            elif self.exit_code == 0:
                raise Exception("Screen closed with exit code 0")
            # code 1: quit the screen, go back
            elif self.exit_code == 1:
                # quitting the title screens quits the game
                if self.screen_name == "title":
                    running = False
                else:
                    # go back to title screen
                    self.screen_name = "title"
            # code 2: move to lobby screen (after hosting or joining a server)
            elif self.exit_code == 2:
                self.screen_name = "lobby"
            # code 3: move to lobby list screen (before joining a server)
            elif self.exit_code == 3:
                pass
            # code 4: move to game screen (after a lobby starts or after pressing practice)
            elif self.exit_code == 4:
                self.screen_name = "game"

            # reset exit code
            self.exit_code = 0

        print("Tank Game closed")
        pygame.quit()

    def title(self):
        Button = LobbyUI.Button

        # buttons and texts
        title_font = pygame.font.Font(LobbyUI.title_font, 80)
        title_text = title_font.render('TANK GAME', False, (0, 0, 0))
        title_alpha = 255
        button_texture = pygame.image.load(LobbyUI.button_texture)
        play_button = Button('Play', (100, 400), (400, 100), button_texture, True, 115, True)
        button_font = pygame.font.Font(LobbyUI.button_font, 20)
        name_text = button_font.render(f'Logged as   "{self.name}"', False, (0, 0, 0))
        offline_text = button_font.render(f'(offline mode)', False, (155, 155, 155))
        account_button = Button('Account', (100, 600), (400, 100), button_texture, True, 60, True)
        quit_button = Button('Quit', (100, 800), (400, 100), button_texture, True, 125, True)


        # contains all visible buttons currently on the screen
        self.button_list = [play_button, account_button, quit_button]

        self.activated_window = LobbyUI.Window("None")
        # main program loop
        while self.exit_code == 0:
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

            # temp square at the corner
            sq = pygame.Rect((self.screen.get_width() - 10, self.screen.get_height() - 10), (10, 10))
            pygame.draw.rect(self.screen, (255, 0, 0), sq)

            # draw buttons
            for button in self.button_list:
                button.draw_button(self.screen)

            # player's name at the button, and an offline mode disclaimer
            if self.client.offline_mode:
                self.screen.blit(offline_text, (195, 575))
            else:
                self.screen.blit(name_text, (155, 575))

            pygame.display.flip()

    def lobby(self):
        Button = LobbyUI.Button
        Window = LobbyUI.Window

        # lobby
        user_list = []
        lobby_id = None

        # buttons and texts
        can_texture = pygame.image.load(LobbyUI.can_texture)
        title_font = pygame.font.Font(LobbyUI.button_font, 60)
        title_text = title_font.render(f"WizardTNT's Game", False, (0, 0, 0))
        quit_button = Button('Quit', (950, 22.5), (125, 125), can_texture, static=True)

        # default window in the lobby is a lobby window
        self.activated_window = Window("Lobby")

        # button list
        self.button_list = [quit_button] + self.activated_window.buttons

        # main program loop
        while self.exit_code == 0:
            self.event_handler()

            # handle server data
            datas = self.client.get_buffer_data()
            for data in datas:
                if len(data) > 3:
                    try:
                        # lobby list update
                        if data[0] == 'L':
                            data = data.split("|")
                            lobby_id = data[0][1]
                            user_list = data[1:]
                    except IndexError:
                        pass



            # background
            self.screen.fill(LobbyUI.background_color)

            # lobby's name, side window
            self.screen.blit(title_text, (30, 55))
            self.activated_window.draw_window(self.screen)

            # draw buttons
            for button in self.button_list:
                button.draw_button(self.screen)
            pygame.display.flip()

    def lobby_browser(self):
        pass

    def game(self):
        game = main.Game(self.screen)
        self.exit_code = game.main()

    # handles UI events that are similar in all screens
    def event_handler(self):
        def remove_window():
            if self.screen_name == "lobby":
                self.activated_window = LobbyUI.Window("Lobby")

                # remove all window buttons except lobby window buttons
                self.button_list = [b for b in self.button_list if b.static] + self.activated_window.buttons

            # in the lobby screen, the side window can't be removed
            else:
                # remove the activated window
                self.activated_window = LobbyUI.Window("None")

                # remove all window buttons
                self.button_list = [b for b in self.button_list if b.static]

        mouse_x, mouse_y = pygame.mouse.get_pos()
        for event in pygame.event.get():
            # if user closes the window, stop the game from running.
            if event.type == pygame.QUIT:
                self.exit_code = -1

            if event.type == pygame.KEYUP:
                # actions for when the player presses Escape
                if event.key == pygame.K_ESCAPE:
                    # when there is no activated window, or the current window is the lobby window, open the quit confirmation window
                    if self.activated_window.window_type == "None" or self.activated_window.window_type == "Lobby":
                        self.activated_window = LobbyUI.Window("Quit")
                        self.button_list += self.activated_window.buttons
                        # fake quit button hovering
                        for button in self.button_list:
                            if button.button_type == "Quit":
                                button.hovered = True

                    # when there is an activated window, close it
                    else:
                        remove_window()

            # left click events
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # check if player pressed inside the new window
                    if self.activated_window.get_rect().collidepoint(mouse_x, mouse_y):
                        for button in [a for a in self.button_list if not a.static]:
                            # get which button the player is clicking on, and activate it
                            if button.get_rect().collidepoint(mouse_x, mouse_y):

                                # host case: open a lobby server
                                if button.button_type == "Host":
                                    self.client.send_data("host")
                                    self.exit_code = 2
                                # join case: open the lobby searching screen
                                if button.button_type == "Join":
                                    pass
                                # practice case: start the offline practice game
                                if button.button_type == "Practice":
                                    self.exit_code = 4

                                # confirm quit case: stop running the program
                                if button.button_type == "ConfirmQuit":
                                    self.exit_code = 1
                                # cancel quit case: remove the quit window
                                elif button.button_type == "CancelQuit":
                                    remove_window()

                                # can only press one button at once
                                break

                    # remove the window, and check for main button interactions
                    else:
                        prev_type = self.activated_window.window_type
                        remove_window()
                        # pressed a main button
                        for button in [a for a in self.button_list if a.static]:
                            # find the interacted button
                            if button.get_rect().collidepoint(mouse_x, mouse_y):
                                # close the window, if the player pressed on its button twice
                                if button.button_type == prev_type:
                                    remove_window()
                                # activate the window that belongs to the button
                                else:
                                    self.activated_window = LobbyUI.Window(button.button_type, self.client.offline_mode)
                                    self.button_list += self.activated_window.buttons

        # update button hovering
        for button in self.button_list:
            # requirements for a button to be hovered: 1.
            button.hovered = self.activated_window.window_type == button.button_type or button.get_rect().collidepoint(mouse_x, mouse_y) and (not button.static or self.activated_window.window_type == "None" or self.screen_name == "lobby")

        # handle data from the client
        if not self.client.offline_mode:
            self.client_data_handler()

    def client_data_handler(self):
        pass


    class Button:
        def __init__(self, name, position, scale, texture, has_text=False, text_position=0, static=False):
            self.button_type = name
            self.png = pygame.transform.smoothscale(texture, scale)
            self.font = pygame.font.Font(LobbyUI.button_font, 50)
            self.position = position

            # true if the player's mouse is on the button
            self.hovered = False
            # true if the button doesn't depend on the window
            self.static = static
            # gray and can't be interacted with when true
            self.disabled = False

            # set text
            if has_text:
                self.text = name
            else:
                self.text = ""
            # TODO: replace this with text anchoring
            self.text_position = text_position

        def draw_button(self, screen_):
            # change button attributes depending on them being hovered or disabled
            text_color = (4, 0, 87)
            position = (self.position[0], self.position[1])
            if self.disabled:
                self.png.set_alpha(100)
            else:
                self.png.set_alpha(255)
            if self.hovered:
                text_color = (148, 5, 0)
                position = (self.position[0], self.position[1] + 5)

            # draw the button and its text with fixed positions
            screen_.blit(self.png, position)
            text_obj = self.font.render(self.text, False, text_color)
            text_obj.set_alpha(self.png.get_alpha())
            screen_.blit(text_obj, (position[0] + self.text_position, position[1] + 23))

        # get the button's rect
        def get_rect(self):
            # button can't be pressed or hovered while disabled
            if self.disabled:
                return pygame.Rect(-10, -10, 0, 0)
            rect = self.png.get_rect()
            rect.x = self.position[0]
            rect.y = self.position[1]
            return rect

    class Window:
        Texts = {"Play": "Select Option:", "Account": "Coming Soon", "Quit": "Are you sure you want to quit?",
                 "Lobby": "Game Info", "None": "None"}
        BUTTONS = {"Play": [['Host', (1150, 170), (400, 100), "opt", 115],
                            ['Join', (1150, 280), (400, 100), "opt", 125],
                            ['Practice', (1150, 390), (400, 100), "opt", 48]],
                   "Account": [],
                   "Quit": [['ConfirmQuit', (1310.5, 170), (125, 125), "con"],
                            ['CancelQuit', (1584.5, 170), (125, 125), "can"]],
                   "Lobby": [],
                   "None": []}

        def __init__(self, button_type, offline=False):
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
                if offline and (button[0] == "Host" or button[0] == "Join"):
                    self.buttons[-1].disabled = True

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
    lobby_ui.main()
