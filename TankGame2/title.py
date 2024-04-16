import pygame
import main
from testing.client import Client


class LobbyUI:
    # fonts
    button_font = "resources/fonts/font2.otf"
    title_font = "resources/fonts/font1.ttf"

    # textures
    window_texture = "resources/ui/window.png"
    button1_texture = "resources/ui/button1.png"
    button2_texture = "resources/ui/button2.png"
    confirm_texture = "resources/ui/confirm.png"
    cancel_texture = "resources/ui/cancel.png"

    background_color = (230, 230, 230)

    def __init__(self):
        # initiate program
        pygame.init()
        pygame.display.set_caption('TANK GAME')

        # screen
        self.monitor_info = pygame.display.Info()
        self.screen = pygame.display.set_mode((int(self.monitor_info.current_w), int(self.monitor_info.current_h)))
        self.screen_name = "title"  # determines which screen to print and interact with

        # running process for current screen
        self.activated_window = LobbyUI.Window("None")
        self.exit_code = 0  # equals 0 while the program is running. after the program finishes, it determines what to do next

        # list of available buttons
        self.button_list = []

        # client
        self.client = Client()
        # owner of current lobby
        self.owner = ""

    def main(self):
        # connect to the server
        self.client.connect()

        # get account data
        if not self.client.offline_mode:
            self.client.name = self.client.get_buffer_data(False)[0]

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
        button_texture = pygame.image.load(LobbyUI.button1_texture)
        play_button = Button('Play', (100, 400), (400, 100), button_texture, True, 115, True)
        button_font = pygame.font.Font(LobbyUI.button_font, 20)
        name_text = button_font.render(f'Logged as   "{self.client.name}"', False, (0, 0, 0))
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

        # buttons and texts
        can_texture = pygame.image.load(LobbyUI.cancel_texture)
        title_font = pygame.font.Font(LobbyUI.button_font, 60)
        title_text = title_font.render(f"WizardTNT's Game", False, (0, 0, 0))
        quit_button = Button('Quit', (950, 22.5), (125, 125), can_texture, static=True)

        # default window in the lobby is a lobby window
        self.switch_to_lobby_window()

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
                            self.client.lobby_id = data[0][1]
                            self.client.name_list = data[1:]

                            # reset lobby window
                            if self.activated_window.window_type == "Lobby":
                                self.switch_to_lobby_window()

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

        # notify server about leaving the lobby
        if self.exit_code == 1:
            self.client.send_data("main")

    def switch_to_lobby_window(self):
        self.activated_window = LobbyUI.Window("Lobby", data=[self.client.lobby_id, len(self.client.name_list), self.client.get_owner()])

    def lobby_browser(self):
        pass

    def game(self):
        game = main.Game(self.screen)
        self.exit_code = game.main()

    # handles UI events that are similar in all screens
    def event_handler(self):
        def remove_window():
            if self.screen_name == "lobby":
                self.switch_to_lobby_window()

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
            button.hovered = self.activated_window.window_type == button.button_type or button.get_rect().collidepoint(
                mouse_x, mouse_y) and (not button.static or self.activated_window.window_type == "None" or self.screen_name == "lobby")

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
        TEXTS = {"None": "[]",
                 "Play": "[(self.text_font.render('Select Option:', False, (0, 0, 0)), (1185, 90))]",
                 "Account": "[(self.text_font.render('Coming Soon', False, (0, 0, 0)), (1185, 90))]",
                 "Quit": "[(self.text_font.render('Are you sure you want to quit?', False, (0, 0, 0)), (1185, 90))]",
                 "Lobby": "[(self.text_font.render('Game Info:', False, (0, 0, 0)), (1185, 90)), "
                          "(self.text_font.render('Lobby ID                                          ' + str(data[0]) + '#', False, (0, 0, 0)), (1185, 200)), "
                          "(self.text_font.render('Player Count                           ' + str(data[1]), False, (0, 0, 0)), (1185, 260)), "
                          "(self.text_font.render('Game Host                            ' + str(data[2]), False, (0, 0, 0)), (1185, 320))]",
                 }

        BUTTONS = {"None": "[]",
                   "Play": "[LobbyUI.Button('Host', (1150, 170), (400, 100), pygame.image.load(LobbyUI.button2_texture), True, 115), "
                           "LobbyUI.Button('Join', (1150, 280), (400, 100), pygame.image.load(LobbyUI.button2_texture), True, 125), "
                           "LobbyUI.Button('Practice', (1150, 390), (400, 100), pygame.image.load(LobbyUI.button2_texture), True, 48)]",
                   "Account": "[]",
                   "Quit": "[LobbyUI.Button('ConfirmQuit', (1310.5, 170), (125, 125), pygame.image.load(LobbyUI.confirm_texture)), "
                           "LobbyUI.Button('CancelQuit', (1584.5, 170), (125, 125), pygame.image.load(LobbyUI.cancel_texture))]",
                   "Lobby": "[]"
                   }

        def __init__(self, button_type, offline=False, data=None):
            window_texture = pygame.image.load(LobbyUI.window_texture)
            self.window_type = button_type

            self.png = pygame.transform.smoothscale(window_texture, (820, 1080))
            self.position = (1100, 0)
            self.text_font = pygame.font.Font(LobbyUI.button_font, 30)

            self.texts = []
            exec(f"self.texts = {LobbyUI.Window.TEXTS[self.window_type]}")

            self.buttons = []
            exec(f"self.buttons = {LobbyUI.Window.BUTTONS[self.window_type]}")
            # disable Host and Join buttons if offline mode is activated
            if offline:
                for button in self.buttons:
                    if button.button_type == "Host" or button.button_type == "Join":
                        button.disabled = True

        # incase the button type is None, these functions wouldn't run in the first place. (view event_handler)
        # prints the window on the screen
        def draw_window(self, screen_):
            screen_.blit(self.png, self.position)
            for text, pos in self.texts:
                screen_.blit(text, pos)

        # returns the Rect of the window object
        def get_rect(self):
            rect = self.png.get_rect()
            rect.x = self.position[0]
            rect.y = self.position[1]
            return rect


if __name__ == "__main__":
    lobby_ui = LobbyUI()
    lobby_ui.main()
