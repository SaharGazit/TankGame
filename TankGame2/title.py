import pygame
import main
from networking.client import Client


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
    nametag_texture1 = "resources/ui/settings1.png"
    nametag_texture2 = "resources/ui/settings2.png"
    lobby_tag_texture = "resources/ui/lobby_tag.png"
    arrow_right_texture = "resources/ui/right_arrow.png"

    background_color = (230, 230, 230)

    def __init__(self):
        # initiate program
        pygame.init()
        pygame.display.set_caption('TANK GAME')

        # screen
        self.monitor_info = pygame.display.Info()
        self.screen = pygame.display.set_mode((int(self.monitor_info.current_w), int(self.monitor_info.current_h)))
        self.screen_name = "title"  # determines which screen to print and interact with
        self.clock = pygame.time.Clock()

        # running process for current screen
        self.activated_window = LobbyUI.Window("None")
        self.exit_code = 0  # equals 0 while the program is running. after the program finishes, it determines what to do next

        # list of available buttons
        self.button_list = []

        # client
        self.client = Client()

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
            # code 3: move to lobby browser screen (before joining a server)
            elif self.exit_code == 3:
                self.screen_name = "lobby_browser"
            # code 4: move to game screen (after a lobby starts or after pressing practice)
            elif self.exit_code == 4:
                self.screen_name = "game"

            # reset exit code
            self.exit_code = 0

        print("Tank Game closed")
        pygame.quit()

    def title(self):
        Button = LobbyUI.Button

        # title
        title_font = pygame.font.Font(LobbyUI.title_font, 80)
        title_text = title_font.render('TANK GAME', False, (0, 0, 0))
        title_alpha = 255

        # main buttons
        button_texture = pygame.image.load(LobbyUI.button1_texture)
        button_font = pygame.font.Font(LobbyUI.button_font, 20)
        play_button = Button('Play', (100, 400), (400, 100), button_texture, True, 115, True)
        name_text = button_font.render(f'Logged as   "{self.client.name}"', False, (0, 0, 0))
        offline_text = button_font.render(f'(offline mode)', False, (155, 155, 155))
        account_button = Button('Account', (100, 600), (400, 100), button_texture, True, 60, True)
        quit_button = Button('Quit', (100, 800), (400, 100), button_texture, True, 125, True)

        # default window is title screen is None
        self.activated_window = LobbyUI.Window("None")
        self.button_list = [play_button, account_button, quit_button]

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
                title_alpha = self.get_new_alpha_value(title_alpha)

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

        # title
        title_font = pygame.font.Font(LobbyUI.title_font, 80)
        title_text = title_font.render(f"GET READY", False, (0, 0, 0))
        title_alpha = 255

        # quit button
        can_texture = pygame.image.load(LobbyUI.cancel_texture)
        quit_button = Button('Quit', (950, 22.5), (125, 125), can_texture, static=True)

        # player list
        owner = False
        nam_texture1 = pygame.image.load(LobbyUI.nametag_texture1)
        nam_texture2 = pygame.image.load(LobbyUI.nametag_texture2)
        player_tags = [(Button("Nametag", (30, 400), (100, 100), nam_texture1, False, 105, True), Button("Nametag", (30, 550), (100, 100), nam_texture1, False, 105, True), Button("Nametag", (30, 700), (100, 100), nam_texture1, False, 105, True), Button("Nametag", (30, 850), (100, 100), nam_texture1, False, 105, True)),
                       (Button("Nametag", (520, 400), (100, 100), nam_texture2, False, 105, True), Button("Nametag", (520, 550), (100, 100), nam_texture2, False, 105, True), Button("Nametag", (520, 700), (100, 100), nam_texture2, False, 105, True), Button("Nametag", (520, 850), (100, 100), nam_texture2, False, 105, True))]
        subtitle_font = pygame.font.Font(LobbyUI.button_font, 30)
        blue_text = subtitle_font.render("Blue Team", False, (0, 0, 0))
        red_text = subtitle_font.render("Red Team", False, (0, 0, 0))

        # default window in the lobby is a lobby window
        self.switch_to_lobby_window()
        self.button_list = [quit_button] + self.activated_window.buttons

        # main program loop
        while self.exit_code == 0:
            # handles pygame events
            self.event_handler()

            # handle server data
            datas = self.client.get_buffer_data()
            for data in datas:
                if len(data) > 3:
                    try:
                        # lobby list update
                        if data[0] == 'L':
                            self.client.update_lobby(data)

                            for li in range(2):
                                for u in range(4):
                                    if u < len(self.client.user_list[li]):
                                        player_tags[li][u].text = self.client.user_list[li][u].name
                                    else:
                                        player_tags[li][u].text = ""
                            owner = self.client.name == self.client.get_owner()

                            # reset lobby window
                            if self.activated_window.window_type == "Lobby":
                                self.switch_to_lobby_window()
                                self.button_list = [b for b in self.button_list if b.static] + self.activated_window.buttons

                    except IndexError:
                        continue

            # background
            self.screen.fill(LobbyUI.background_color)

            # title
            title_text.set_alpha(abs(title_alpha))
            self.screen.blit(title_text, (50, 50))
            title_alpha = self.get_new_alpha_value(title_alpha)

            # teams
            self.screen.blit(blue_text, (60, 345))
            self.screen.blit(red_text, (550, 345))
            for player_tag in player_tags[0] + player_tags[1]:
                if player_tag.text != '':
                    player_tag.draw_button(self.screen)

            # side window
            self.activated_window.draw_window(self.screen)

            # draw buttons
            for button in self.button_list:
                button.draw_button(self.screen)

            pygame.display.flip()

        # notify server about leaving the lobby
        if self.exit_code == 1:
            self.client.send_data("main")

    def lobby_browser(self):
        Button = LobbyUI.Button
        Window = LobbyUI.Window

        # title
        title_font = pygame.font.Font(LobbyUI.title_font, 80)
        title_text = title_font.render(f"SELECT GAME", False, (0, 0, 0))
        title_alpha = 255

        # this screen's buttons are technically static, but they function like a non-static button
        # back (quit) button
        can_texture = pygame.image.load(LobbyUI.cancel_texture)
        back_button = Button('Back', (1770, 22.5), (125, 125), can_texture)
        # refresh button
        button_texture = pygame.image.load(LobbyUI.button2_texture)
        refresh_button = Button("Refresh", (1350, 30), (400, 100), button_texture, True, 52)

        # lobby tags
        lobby_tags = []
        subtitle_font = pygame.font.Font(LobbyUI.button_font, 30)
        no_lobby_text = subtitle_font.render("No Available Lobbies", False, (155, 155, 155))

        # no windows in lobby browser screen
        self.activated_window = Window("None")
        self.button_list = [back_button, refresh_button]
        right_arrow_texture = pygame.image.load(LobbyUI.arrow_right_texture)

        while self.exit_code == 0:
            self.event_handler()

            # handle server data
            datas = self.client.get_buffer_data()
            for data in datas:
                try:
                    # reset lobby tags and buttons
                    lobby_tags = []
                    self.button_list = [back_button, refresh_button]
                    y = 225
                    for lobby_info in data.split("||"):
                        lobby_info = lobby_info.split("|")
                        if len(lobby_info) == 3:
                            # update lobby tags
                            lobby_tags.append(LobbyUI.LobbyTag(lobby_info[0], lobby_info[1], lobby_info[2]))
                            self.button_list.append(Button(f"Lobby{str(lobby_info[0])}", (1250, y), (125, 125), right_arrow_texture))
                            y += 130

                except IndexError:
                    continue

            # background
            self.screen.fill(LobbyUI.background_color)

            # title
            title_text.set_alpha(abs(title_alpha))
            self.screen.blit(title_text, (50, 50))
            title_alpha = self.get_new_alpha_value(title_alpha)

            # lobby tags
            if len(lobby_tags) == 0:
                self.screen.blit(no_lobby_text, (70, 200))
            else:
                tag_pos = 170
                for tag in lobby_tags:
                    tag.draw_tag(self.screen, (20, tag_pos))
                    tag_pos += 130

            # draw buttons
            for button in self.button_list:
                button.draw_button(self.screen)

            pygame.display.flip()

    # switches window to lobby window
    def switch_to_lobby_window(self):
        self.activated_window = LobbyUI.Window("Lobby", data=[self.client.lobby_id, len(self.client.user_list[0] + self.client.user_list[1]), self.client.get_owner(), self.client.name == self.client.get_owner()])

    def game(self):
        game = main.Game(self.screen)
        self.exit_code = game.main()

    # handles UI events that are similar in all screens
    def event_handler(self):
        # 60 dps
        self.clock.tick(60)

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
                    # quit window immediately. if the current screen is the lobby browser
                    if self.screen_name == "lobby_browser":
                        self.exit_code = 1

                    # when there is no activated window, or the current window is the lobby window, open the quit confirmation window
                    elif self.activated_window.window_type == "None" or self.activated_window.window_type == "Lobby":
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
                    # check if player pressed inside the new window (non-static buttons) or a lobby browser button since they function the same way
                    if self.activated_window.get_rect().collidepoint(mouse_x, mouse_y) or self.screen_name == "lobby_browser":
                        for button in [a for a in self.button_list if not a.static]:
                            # get which button the player is clicking on, and activate it
                            if button.get_rect().collidepoint(mouse_x, mouse_y):

                                # host case: open a lobby server
                                if button.button_type == "Host":
                                    self.client.send_data("host")
                                    self.exit_code = 2
                                # join/refresh case: open the lobby searching screen
                                elif button.button_type == "Join" or button.button_type == "Refresh":
                                    self.client.send_data("list")
                                    self.exit_code = 3
                                # practice case: start the offline practice game
                                elif button.button_type == "Practice":
                                    self.exit_code = 4
                                # confirm quit/back case: exit the current window
                                elif button.button_type == "ConfirmQuit" or button.button_type == "Back":
                                    self.exit_code = 1
                                # cancel quit case: remove the quit window
                                elif button.button_type == "CancelQuit":
                                    remove_window()
                                # lobby case: join a selected lobby
                                elif button.button_type[:-1] == "Lobby":
                                    self.client.send_data(f"join{button.button_type[-1]}")
                                    self.exit_code = 2

                                # can only press one button at once
                                break

                    # remove the window, and check for main button interactions (static buttons)
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
            # requirements for a button to be hovered:
            # 1. button's window is activated (forced hover)
            # 2. Mouse colliders with button, if the window is not static, or if the window is None or Lobby
            button.hovered = self.activated_window.window_type == button.button_type or button.get_rect().collidepoint(
                mouse_x, mouse_y) and (not button.static or self.activated_window.window_type == "None" or self.screen_name == "lobby")

    @staticmethod
    def get_new_alpha_value(a):
        if a <= -255:
            return 255
        else:
            return a - 4

    class Button:
        def __init__(self, name, position, scale, texture, has_text=False, text_position=0, static=False):
            self.button_type = name
            self.png = pygame.transform.smoothscale(texture, scale)
            self.position = position

            # true if the player's mouse is on the button
            self.hovered = False
            # true if the button doesn't depend on the window
            self.static = static
            # gray and can't be interacted with when true
            self.disabled = False

            if has_text:
                self.text = name
                self.font = pygame.font.Font(LobbyUI.button_font, 50)
                y = 23
            else:
                self.text = ""
                self.font = pygame.font.Font(LobbyUI.button_font, 25)
                y = 38

            # TODO: replace this with text anchoring
            self.text_position = [text_position, y]

        def draw_button(self, screen_, ):
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
            screen_.blit(text_obj, (position[0] + self.text_position[0], position[1] + self.text_position[1]))

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
                          "(self.text_font.render('Lobby ID:   ' + str(data[0]) + '#', False, (0, 0, 0)), (1185, 200)), "
                          "(self.text_font.render('Player Count:   ' + str(data[1]), False, (0, 0, 0)), (1185, 260)), "
                          "(self.text_font.render('Host:   ' + str(data[2]), False, (0, 0, 0)), (1185, 320))]",
                 }

        BUTTONS = {"None": "[]",
                   "Play": "[LobbyUI.Button('Host', (1150, 170), (400, 100), pygame.image.load(LobbyUI.button2_texture), True, 115), "
                           "LobbyUI.Button('Join', (1150, 280), (400, 100), pygame.image.load(LobbyUI.button2_texture), True, 125), "
                           "LobbyUI.Button('Practice', (1150, 390), (400, 100), pygame.image.load(LobbyUI.button2_texture), True, 48)]",
                   "Account": "[]",
                   "Quit": "[LobbyUI.Button('ConfirmQuit', (1310.5, 170), (125, 125), pygame.image.load(LobbyUI.confirm_texture)), "
                           "LobbyUI.Button('CancelQuit', (1584.5, 170), (125, 125), pygame.image.load(LobbyUI.cancel_texture))]",
                   "Lobby": "[LobbyUI.Button('Start', (1300, 900), (400, 100), pygame.image.load(LobbyUI.button2_texture), True, 95)]"
                   }

        def __init__(self, window_type, offline=False, data=None):
            if data is None:
                data = [None, None, None, None]

            self.window_type = window_type
            window_texture = pygame.image.load(LobbyUI.window_texture)
            self.png = pygame.transform.smoothscale(window_texture, (820, 1080))
            self.position = (1100, 0)
            self.text_font = pygame.font.Font(LobbyUI.button_font, 30)

            self.texts = []
            exec(f"self.texts = {LobbyUI.Window.TEXTS[self.window_type]}")

            self.buttons = []
            exec(f"self.buttons = {LobbyUI.Window.BUTTONS[self.window_type]}")
            # disable buttons with conditions
            if window_type == "Play":
                for button in self.buttons:
                    if offline and (button.button_type == "Host" or button.button_type == "Join"):
                        button.disabled = True
            if window_type == "Lobby":
                for button in self.buttons:
                    if not data[3] and button.button_type == "Start":
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

    class LobbyTag:
        def __init__(self, id_, owner_name, player_count):

            tag_texture = pygame.image.load(LobbyUI.lobby_tag_texture)
            self.png = pygame.transform.smoothscale(tag_texture, (1200, 240))
            self.text_font = pygame.font.Font(LobbyUI.button_font, 45)

            self.id = self.text_font.render(f"{id_}#", False, (0, 0, 0))
            self.owner_name = self.text_font.render(f"{owner_name}'s Game", False, (0, 0, 0))
            self.player_count = self.text_font.render(f"{player_count}/8", False, (0, 0, 0))

        def draw_tag(self, screen_, position):
            screen_.blit(self.png, position)
            screen_.blit(self.id, (position[0] + 68, position[1] + 98))
            screen_.blit(self.owner_name, (position[0] + 230, position[1] + 98))
            screen_.blit(self.player_count, (position[0] + 1010, position[1] + 98))


if __name__ == "__main__":
    lobby_ui = LobbyUI()
    lobby_ui.main()
