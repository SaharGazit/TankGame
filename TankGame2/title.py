import pygame
import main
import time
from client import Client


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
    reconnect_texture = "resources/ui/reconnect.png"

    background_color = (230, 230, 230)
    design_resolution = (1920, 1080)
    scale_factor = (1, 1)
    screen_divider = 1

    def __init__(self):
        # initiate program
        pygame.init()
        pygame.display.set_caption('TANK GAME')

        # screen
        self.monitor_info = pygame.display.Info()
        user_screen_size = (int(self.monitor_info.current_w / LobbyUI.screen_divider), int(self.monitor_info.current_h / LobbyUI.screen_divider))
        self.screen = pygame.display.set_mode(user_screen_size)
        LobbyUI.scale_factor = (user_screen_size[0] / LobbyUI.design_resolution[0], user_screen_size[1] / LobbyUI.design_resolution[1])

        self.screen_name = "title"  # determines which screen to print and interact with
        self.shift_held = False
        self.clock = pygame.time.Clock()

        # running process for current screen
        self.activated_window = LobbyUI.Window("None")
        self.exit_code = 0  # equals 0 while the program is running. after the program finishes, it determines what to do next

        # list of available buttons and fields
        self.button_list = []
        self.field_list = []

        # client
        self.client = Client()

    def main(self):
        # connect to the server
        self.client.connect_tcp()

        running = True
        reconnect = False
        arguments = ""
        while running:
            # executes the current screen function
            exec(f"self.{self.screen_name}({arguments})")
            arguments = ""

            # case -3: restart program
            if self.exit_code == -3:
                running = False
                reconnect = True
            # case -2: restart page
            elif self.exit_code == -2:
                pass
            # case -1: shut down program immediately
            elif self.exit_code == -1:
                running = False
            # case 0: program running. not supposed to reach this point with code 0
            elif self.exit_code == 0:
                raise Exception("Screen closed with exit code 0")
            # case 1: quit the screen, go back
            elif self.exit_code == 1:
                # quitting the title screens quits the game
                if self.screen_name == "title":
                    running = False
                else:
                    # go back to title screen
                    self.screen_name = "title"
            # case 2: move to lobby screen (after hosting or joining a server)
            elif self.exit_code == 2:
                self.screen_name = "lobby"
            # case 3: move to lobby browser screen (before joining a server)
            elif self.exit_code == 3:
                self.screen_name = "lobby_browser"
            # case 4: move to game screen (after a lobby starts or after pressing practice)
            elif self.exit_code == 4:
                self.screen_name = "game"
            # case login/signup: move to account screen
            else:
                arguments = f"'{self.exit_code}'"
                self.screen_name = "account"

            # reset exit code
            self.exit_code = 0

        print("Tank Game closed")
        pygame.quit()
        return reconnect

    def title(self):
        Button = LobbyUI.Button
        scale_factor = LobbyUI.scale_factor

        # title
        title_font = pygame.font.Font(LobbyUI.title_font, int(80 * scale_factor[0]))
        title_text = title_font.render('TANK GAME', False, (0, 0, 0))
        title_alpha = 255

        # main buttons
        button_texture = pygame.image.load(LobbyUI.button1_texture)
        button_font = pygame.font.Font(LobbyUI.button_font, int(20 * scale_factor[0]))
        play_button = Button('Play', (100, 400), (400, 100), button_texture, True, True)
        name_text = button_font.render(f'Logged as   "{self.client.name}"', False, (0, 0, 0))
        account_button = Button('Account', (100, 600), (400, 100), button_texture, True, True)
        quit_button = Button('Quit', (100, 800), (400, 100), button_texture, True, True)
        offline_text = button_font.render(f'(offline mode)', False, (155, 155, 155))
        reconnect_texture = pygame.image.load(LobbyUI.reconnect_texture)
        reconnect_button = Button('Reconnect', (390, 565), (30, 30), reconnect_texture, False, True)

        # default window is title screen is None
        self.activated_window = LobbyUI.Window("None")
        self.button_list = [play_button, account_button, quit_button]
        if self.client.offline_mode:
            self.button_list.append(reconnect_button)
            self.button_list[1].disabled = True

        # main program loop
        while self.exit_code == 0:
            # handles pygame events
            self.event_handler()

            # background
            self.screen.fill(LobbyUI.background_color)

            # title (TANK GAME)
            title_text.set_alpha(abs(title_alpha))
            self.screen.blit(title_text, (75 * scale_factor[0], 75 * scale_factor[1]))
            if self.activated_window.window_type == "None":
                title_alpha = self.get_new_alpha_value(title_alpha)

            # side-window
            else:
                self.activated_window.draw_window(self.screen)

            # draw buttons
            for button in self.button_list:
                button.draw_button(self.screen)

            # player's name at the button, and an offline mode disclaimer
            if self.client.offline_mode:
                self.screen.blit(offline_text, (170 * scale_factor[0], 575 * scale_factor[1]))
            else:
                self.screen.blit(name_text, (155 * scale_factor[0], 575 * scale_factor[1]))

            pygame.display.flip()

    def lobby(self):
        Button = LobbyUI.Button
        scale_factor = LobbyUI.scale_factor
        Countdown = 5

        # title
        title_font = pygame.font.Font(LobbyUI.title_font, int(80 * scale_factor[0]))
        title_text = title_font.render(f"GET READY", False, (0, 0, 0))
        title_alpha = 255

        # quit button
        can_texture = pygame.image.load(LobbyUI.cancel_texture)
        quit_button = Button('Quit', (950, 22.5), (125, 125), can_texture, False, True)

        # player list
        nam_texture1 = pygame.image.load(LobbyUI.nametag_texture1)
        nam_texture2 = pygame.image.load(LobbyUI.nametag_texture2)
        player_tags = [(Button("Nametag", (30, 400), (100, 100), nam_texture1, False, True), Button("Nametag", (30, 550), (100, 100), nam_texture1, False, True), Button("Nametag", (30, 700), (100, 100), nam_texture1, False, True), Button("Nametag", (30, 850), (100, 100), nam_texture1, False, True)),
                       (Button("Nametag", (520, 400), (100, 100), nam_texture2, False, True), Button("Nametag", (520, 550), (100, 100), nam_texture2, False, True), Button("Nametag", (520, 700), (100, 100), nam_texture2, False, True), Button("Nametag", (520, 850), (100, 100), nam_texture2, False, True))]
        subtitle_font = pygame.font.Font(LobbyUI.button_font, int(30 * scale_factor[0]))
        blue_text = subtitle_font.render("Blue Team", False, (0, 0, 230))
        red_text = subtitle_font.render("Red Team", False, (230, 0, 0))

        # cancel button
        cancel_button = LobbyUI.Button('Cancel', (1300, 900), (400, 100), pygame.image.load(LobbyUI.button2_texture), True)

        # default window in the lobby is a lobby window
        self.switch_to_lobby_window()
        self.button_list = [quit_button] + self.activated_window.buttons

        # timer
        og_time = None

        # main program loop
        while self.exit_code == 0:
            # handles pygame events
            self.event_handler()

            # handle server data
            datas = self.client.get_buffer_data()
            for data in datas:
                if data == "start":
                    # start timer
                    og_time = time.perf_counter()

                elif data == "cancel":
                    # reset timer
                    og_time = None

                    # reset window
                    if self.activated_window.window_type == "Lobby":
                        self.switch_to_lobby_window()
                        self.button_list = [quit_button] + self.activated_window.buttons

                elif data == "kick":
                    self.exit_code = 1

                else:
                    try:
                        # lobby list update
                        if data[0] == 'L':
                            self.client.update_lobby(data)

                            # set player tags
                            for li in range(2):
                                for u in range(4):
                                    if u < len(self.client.user_list[li]):
                                        name = self.client.user_list[li][u].name
                                        # add "(You)" if this name matches client name
                                        if name == self.client.name:
                                            name += " (You)"
                                        player_tags[li][u].text = name

                                    else:
                                        player_tags[li][u].text = ""

                            # reset lobby window
                            if self.activated_window.window_type == "Lobby":
                                self.switch_to_lobby_window()
                                self.button_list = [b for b in self.button_list if b.static] + self.activated_window.buttons

                    except IndexError:
                        continue

            # background
            self.screen.fill(LobbyUI.background_color)

            title_text.set_alpha(abs(title_alpha))
            self.screen.blit(title_text, (50 * scale_factor[0], 50 * scale_factor[1]))
            title_alpha = self.get_new_alpha_value(title_alpha)

            # teams
            self.screen.blit(blue_text, (60 * scale_factor[0], 345 * scale_factor[1]))
            self.screen.blit(red_text, (550 * scale_factor[0], 345 * scale_factor[1]))
            for player_tag in player_tags[0] + player_tags[1]:
                if player_tag.text != '':
                    player_tag.draw_button(self.screen)

            # side window
            self.activated_window.draw_window(self.screen)

            if og_time is not None:
                # update and draw timer
                seconds = Countdown - int((time.perf_counter() - og_time))
                time_text = subtitle_font.render(f"Game Starts in {seconds}s", False, (0, 0, 0))
                self.screen.blit(time_text, (1310 * scale_factor[0], 850 * scale_factor[1]))
                # start game when timer reaches 0
                if seconds == 0:
                    self.client.connect_udp()
                    self.exit_code = 4

                # replace start button with cancel button
                for b in self.button_list:
                    if b.button_type == "Start" and not b.disabled:
                        self.button_list.remove(b)
                        self.button_list.append(cancel_button)
                        break

            # draw buttons
            for button in self.button_list:
                button.draw_button(self.screen)

            pygame.display.flip()

        if self.exit_code == 1:
            # disconnect from udp server, if it opened
            self.client.disconnect_udp()
            # notify server about leaving the lobby
            self.client.send_data("main")

    def lobby_browser(self):
        Button = LobbyUI.Button
        Window = LobbyUI.Window
        scale_factor = LobbyUI.scale_factor

        # title
        title_font = pygame.font.Font(LobbyUI.title_font, int(80 * self.scale_factor[0]))
        title_text = title_font.render(f"SELECT GAME", False, (0, 0, 0))
        title_alpha = 255

        # this screen's buttons are technically static, but they function like a non-static button
        # back (quit) button
        can_texture = pygame.image.load(LobbyUI.cancel_texture)
        back_button = Button('Back', (1770, 22.5), (125, 125), can_texture)
        # refresh button
        button_texture = pygame.image.load(LobbyUI.button2_texture)
        refresh_button = Button("Refresh", (1350, 30), (400, 100), button_texture, True)

        # lobby tags
        lobby_tags = []
        subtitle_font = pygame.font.Font(LobbyUI.button_font, int(30 * scale_factor[0]))
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
                            self.button_list.append(Button(f"Lobby{str(lobby_info[0])}", (1215, y), (125, 125), right_arrow_texture))
                            y += 130

                except IndexError:
                    continue

            # background
            self.screen.fill(LobbyUI.background_color)

            # title
            title_text.set_alpha(abs(title_alpha))
            self.screen.blit(title_text, (50 * scale_factor[0], 50 * scale_factor[1]))
            title_alpha = self.get_new_alpha_value(title_alpha)

            # lobby tags
            if len(lobby_tags) == 0:
                self.screen.blit(no_lobby_text, (70 * scale_factor[0], 200 * scale_factor[1]))
            else:
                tag_pos = 170
                for tag in lobby_tags:
                    tag.draw_tag(self.screen, (20, tag_pos))
                    tag_pos += 130

            # draw buttons
            for button in self.button_list:
                button.draw_button(self.screen)

            pygame.display.flip()

    def account(self, screen_type):
        Button = LobbyUI.Button
        Window = LobbyUI.Window
        Field = LobbyUI.InputField
        scale_factor = LobbyUI.scale_factor

        # title
        title_font = pygame.font.Font(LobbyUI.title_font, int(80 * self.scale_factor[0]))
        title_text = title_font.render(screen_type.upper(), False, (0, 0, 0))
        title_alpha = 255

        # text input headers
        header_font = pygame.font.Font(LobbyUI.button_font, int(30 * scale_factor[0]))
        username_header = header_font.render("Username", False, (0, 0, 0))
        password_header = header_font.render("Password", False, (0, 0, 0))
        password_header2 = header_font.render("Confirm Password", False, (0, 0, 0))

        # error text
        error_font = pygame.font.Font(LobbyUI.button_font, int(20 * scale_factor[0]))
        error = ""

        # input fields
        field_font = pygame.font.Font(LobbyUI.button_font, int(20 * scale_factor[0]))
        username = Field((675, 300), field_font)
        password = Field((675, 560), field_font, True)
        con_password = Field((675, 820), field_font, True)

        # buttons
        can_texture = pygame.image.load(LobbyUI.cancel_texture)
        button_texture = pygame.image.load(LobbyUI.button2_texture)
        back_button = Button('Back', (1770, 22.5), (125, 125), can_texture)
        ok_button = Button('Done', (1200, 280), (400, 100), button_texture, True)

        # no windows in lobby browser screen
        self.activated_window = Window("None")
        self.button_list = [back_button, ok_button]
        self.field_list = [username, password]
        if screen_type == "Signup":
            self.field_list.append(con_password)

        while self.exit_code == 0:
            self.event_handler()

            # handle server data
            datas = self.client.get_buffer_data()
            for data in datas:
                try:
                    data = data.split("|")
                    # update error message
                    if data[0] == "invalid":
                        if data[1] == "1":
                            error = "username already exists"
                        elif data[1] == "2":
                            error = "incorrect username/password"
                        elif data[1] == "3":
                            error = "account already online"
                        else:
                            error = data[1]
                    elif data[0] == "success":
                        if screen_type == "Signup":
                            self.exit_code = "Login"
                        else:
                            self.exit_code = 1
                            self.client.login(username.text)

                except IndexError:
                    continue

            # background
            self.screen.fill(LobbyUI.background_color)

            # title
            title_text.set_alpha(abs(title_alpha))
            self.screen.blit(title_text, (700 * scale_factor[0], 50 * scale_factor[1]))
            title_alpha = self.get_new_alpha_value(title_alpha)

            # headers
            self.screen.blit(username_header, (790 * self.scale_factor[0], 200 * self.scale_factor[1]))
            self.screen.blit(password_header, (790 * self.scale_factor[0], 460 * self.scale_factor[1]))
            if screen_type == "Signup":
                self.screen.blit(password_header2, (705 * self.scale_factor[0], 720 * self.scale_factor[1]))

            # error text
            error_text = error_font.render(error, False, (200, 0, 0))
            self.screen.blit(error_text, (1210, 400))

            # input fields
            for field in self.field_list:
                field.draw_field(self.screen)

            # buttons
            for button in self.button_list:
                button.draw_button(self.screen)

            # update screen
            pygame.display.flip()

        self.field_list = []

    # switches window to lobby window
    def switch_to_lobby_window(self):
        self.activated_window = LobbyUI.Window("Lobby", data=[self.client.lobby_id, len(self.client.user_list[0] + self.client.user_list[1]), self.client.get_owner(), self.client.can_start()])

    def remove_window(self, fd=False):
        if self.screen_name == "lobby":
            self.switch_to_lobby_window()

            # remove all window buttons except lobby window buttons
            self.button_list = [b for b in self.button_list if b.static]
            if not fd:
                self.button_list += self.activated_window.buttons

        # in the lobby screen, the side window can't be removed
        else:
            # remove the activated window
            self.activated_window = LobbyUI.Window("None")

            # remove all window buttons
            self.button_list = [b for b in self.button_list if b.static]

    def game(self):
        game = main.Game(self.screen, self.client)
        self.exit_code = game.main()

    # handles UI events that are similar in all screens
    def event_handler(self):
        # 60 dps
        self.clock.tick(60)

        mouse_x, mouse_y = pygame.mouse.get_pos()
        for event in pygame.event.get():
            # if user closes the window, stop the game from running.
            if event.type == pygame.QUIT:
                self.exit_code = -1

            # triggered when the user stops holding a key
            if event.type == pygame.KEYUP:
                # pressing escape
                if event.key == pygame.K_ESCAPE:
                    # quit window immediately. if the current screen is the lobby browser
                    if self.screen_name == "lobby_browser" or self.screen_name == "account":
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
                        self.remove_window()

                # cancel shift
                elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    self.shift_held = False

            # triggered when the user presses down a key
            if event.type == pygame.KEYDOWN:
                # get key name
                key_name = pygame.key.name(event.key)
                # set shift status
                if key_name == "left shift" or key_name == "right shift":
                    self.shift_held = True

                extra_symbols = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')']
                # check for selected input fields
                found_selected = False
                for i in range(len(self.field_list)):
                    field = self.field_list[i]
                    if field.selected and not found_selected:
                        # move to next field
                        if key_name == "tab":
                            if i != len(self.field_list) - 1:
                                field.selected = False
                                self.field_list[i + 1].selected = True
                        elif self.shift_held:
                            # add shifted letter
                            if key_name.isnumeric():
                                field.text = field.text + extra_symbols[int(key_name) - 1]
                        else:
                            # add clicked letter to the text
                            if len(key_name) == 1 and (key_name.isnumeric() or key_name.isalpha()):
                                field.text = field.text + key_name
                            # delete last letter from the text, the text is not empty
                            elif key_name == "backspace" and len(field.text) > 0:
                                field.text = field.text[:-1]
                        found_selected = True
                if not found_selected and key_name == "tab":
                    # select first field
                    self.field_list[0].selected = True


            # left click events
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # check if player pressed inside the new window (non-static buttons) or a lobby browser/account button since they function the same way
                    if self.activated_window.get_rect().collidepoint(mouse_x, mouse_y) or self.screen_name == "lobby_browser" or self.screen_name == "account":
                        # check button
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
                                    self.remove_window()
                                # lobby case: join a selected lobby
                                elif button.button_type[:-1] == "Lobby":
                                    self.client.send_data(f"join{button.button_type[-1]}")
                                    self.exit_code = 2
                                # start case: start a game
                                elif button.button_type == "Start":
                                    self.client.send_data("start")
                                # cancel case: cancel the game countdown
                                elif button.button_type == "Cancel":
                                    self.client.send_data("cancel")
                                # login/signup case: go to account screen
                                elif button.button_type == "Login" or button.button_type == "Signup":
                                    self.exit_code = button.button_type
                                # logout case: user logged out
                                elif button.button_type == "Logout":
                                    self.client.logged = False
                                    self.client.name = "guest"
                                    self.client.send_data("logout")
                                    self.exit_code = -2
                                # logged in / signed up (pressed the done button)
                                elif button.button_type == "Done":
                                    accepted = True
                                    action = "login"
                                    # check password confirmation
                                    length = len(self.field_list)
                                    if length == 3:
                                        action = "signup"
                                        # check if password equals to confirm password
                                        if self.field_list[2].text != self.field_list[1].text:
                                            accepted = False
                                            self.client.buffer.append(f"invalid|passwords don't match")
                                        # ignore confirm password in the next segment
                                        length = 2

                                    # handle each field
                                    for i in range(length * accepted):
                                        status = self.field_list[i].valid_input()
                                        # input is invalid, update error message
                                        if status != "accepted":
                                            accepted = False
                                            # get field name
                                            if self.field_list[i].hidden:
                                                f_name = "password"
                                            else:
                                                f_name = "username"

                                            self.client.buffer.append(f"invalid|{f_name} {status}")
                                            break

                                    if accepted:
                                        # send request to server
                                        self.client.send_data(f"{action}|{self.field_list[0].text}|{self.field_list[1].text}")
                                break
                        # check input fields
                        for field in self.field_list:
                            # get which field the player is pressing on
                            if field.rect.collidepoint(mouse_x, mouse_y):
                                field.selected = not field.selected
                            # unselect the field if the player clicked elsewhere
                            else:
                                field.selected = False

                    # remove the window, and check for main button interactions (static buttons)
                    else:
                        prev_type = self.activated_window.window_type
                        self.remove_window(True)
                        # pressed a main button
                        for button in [a for a in self.button_list if a.static]:
                            # find the interacted button
                            if button.get_rect().collidepoint(mouse_x, mouse_y):
                                # restart game on pressing reconnect
                                if button.button_type == "Reconnect":
                                    self.exit_code = -3
                                # activate the window that belongs to the button
                                elif button.button_type != prev_type:
                                    self.activated_window = LobbyUI.Window(button.button_type, self.client.offline_mode, [self.client.logged])
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
        def __init__(self, name, position, scale, texture, has_text=False, static=False):
            self.button_type = name
            self.scale_factor = LobbyUI.scale_factor
            self.scale = (int(scale[0] * self.scale_factor[0]), int(scale[1] * self.scale_factor[1]))
            self.png = pygame.transform.smoothscale(texture, self.scale)
            self.position = (position[0] * self.scale_factor[0], position[1] * self.scale_factor[1])

            # true if the player's mouse is on the button
            self.hovered = False
            # true if the button doesn't depend on the window
            self.static = static
            # gray and can't be interacted with when true
            self.disabled = False

            self.centered = True
            if has_text:
                self.text = name
                self.font = pygame.font.Font(LobbyUI.button_font, int(50 * self.scale_factor[0]))
            else:
                self.text = ""
                self.font = pygame.font.Font(LobbyUI.button_font, int(25 * self.scale_factor[0]))
                self.centered = False

        def draw_button(self, screen_, ):
            # change button attributes depending on them being hovered or disabled
            text_color = (4, 0, 87)
            position = self.position

            if self.disabled:
                self.png.set_alpha(100)
            else:
                self.png.set_alpha(255)
            if self.hovered:
                text_color = (148, 5, 0)
                position = (position[0], (self.position[1] + 5 * self.scale_factor[1]))

            # draw the button
            screen_.blit(self.png, position)

            # get text position related to the button
            x, y = self.font.size(self.text)  # txt being whatever str you're rendering
            if self.centered:
                x = (self.scale[0] - x) / 2
            else:
                x = 105 * self.scale_factor[0]
            y = (self.scale[1] - y) / 2

            # set text
            text_obj = self.font.render(self.text, False, text_color)
            text_obj.set_alpha(self.png.get_alpha())
            screen_.blit(text_obj, (position[0] + x, position[1] + y))

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
                 "Account": "[(self.text_font.render('Manage Account:', False, (0, 0, 0)), (1185, 90))]",
                 "Quit": "[(self.text_font.render('Are you sure you want to quit?', False, (0, 0, 0)), (1185, 90))]",
                 "Lobby": "[(self.text_font.render('Game Info:', False, (0, 0, 0)), (1185, 90)), "
                          "(self.text_font.render('Lobby ID:   ' + str(data[0]) + '#', False, (0, 0, 0)), (1185, 200)), "
                          "(self.text_font.render('Player Count:   ' + str(data[1]), False, (0, 0, 0)), (1185, 260)), "
                          "(self.text_font.render('Host:   ' + str(data[2]), False, (0, 0, 0)), (1185, 320))]",
                 }

        BUTTONS = {"None": "[]",
                   "Play": "[LobbyUI.Button('Host', (1150, 170), (400, 100), pygame.image.load(LobbyUI.button2_texture), True), "
                           "LobbyUI.Button('Join', (1150, 280), (400, 100), pygame.image.load(LobbyUI.button2_texture), True), "
                           "LobbyUI.Button('Practice', (1150, 390), (400, 100), pygame.image.load(LobbyUI.button2_texture), True)]",
                   "Account": "[LobbyUI.Button('Login', (1150, 170), (400, 100), pygame.image.load(LobbyUI.button2_texture), True), "
                              "LobbyUI.Button('Signup', (1150, 280), (400, 100), pygame.image.load(LobbyUI.button2_texture), True), "
                              "LobbyUI.Button('Logout', (1150, 390), (400, 100), pygame.image.load(LobbyUI.button2_texture), True)]",
                   "Quit": "[LobbyUI.Button('ConfirmQuit', (1310.5, 170), (125, 125), pygame.image.load(LobbyUI.confirm_texture)), "
                           "LobbyUI.Button('CancelQuit', (1584.5, 170), (125, 125), pygame.image.load(LobbyUI.cancel_texture))]",
                   "Lobby": "[LobbyUI.Button('Start', (1300, 900), (400, 100), pygame.image.load(LobbyUI.button2_texture), True)]"
                   }

        def __init__(self, window_type, offline=False, data=None):
            if data is None:
                data = [None, None, None, None]
            self.scale_factor = LobbyUI.scale_factor

            self.window_type = window_type
            window_texture = pygame.image.load(LobbyUI.window_texture)
            self.png = pygame.transform.smoothscale(window_texture, (int(820 * self.scale_factor[0]), int(1080 * self.scale_factor[1])))
            self.position = (1100 * self.scale_factor[0], 0)
            self.text_font = pygame.font.Font(LobbyUI.button_font, int(30 * self.scale_factor[0]))

            self.texts = []
            exec(f"self.texts = {LobbyUI.Window.TEXTS[self.window_type]}")

            self.buttons = []
            exec(f"self.buttons = {LobbyUI.Window.BUTTONS[self.window_type]}")
            # disable buttons with conditions
            if window_type == "Play":
                if offline or not data[0]:
                    self.buttons[0].disabled = True
                    self.buttons[1].disabled = True
            elif window_type == "Account":
                if data[0]:
                    self.buttons[0].disabled = True
                    self.buttons[1].disabled = True
                else:
                    self.buttons[2].disabled = True
                    pass
            elif window_type == "Lobby":
                for button in self.buttons:
                    if not data[3] and button.button_type == "Start":
                        button.disabled = True

        # incase the button type is None, these functions wouldn't run in the first place. (view event_handler)
        # prints the window on the screen
        def draw_window(self, screen_):
            screen_.blit(self.png, self.position)
            for text, pos in self.texts:
                screen_.blit(text, (pos[0] * self.scale_factor[0], pos[1] * self.scale_factor[1]))

        # returns the Rect of the window object
        def get_rect(self):
            rect = self.png.get_rect()
            rect.x = self.position[0]
            rect.y = self.position[1]
            return rect

    class LobbyTag:
        def __init__(self, id_, owner_name, player_count):
            self.scale_factor = LobbyUI.scale_factor
            tag_texture = pygame.image.load(LobbyUI.lobby_tag_texture)
            self.png = pygame.transform.smoothscale(tag_texture, (int(1200 * self.scale_factor[0]), int(240 * self.scale_factor[1])))
            self.text_font = pygame.font.Font(LobbyUI.button_font, int(45 * self.scale_factor[0]))

            self.id = self.text_font.render(f"{id_}#", False, (0, 0, 0))
            self.owner_name = self.text_font.render(f"{owner_name}'s Game", False, (0, 0, 0))
            self.player_count = self.text_font.render(f"{player_count}/8", False, (0, 0, 0))

        def draw_tag(self, screen_, position):
            position = (position[0] * self.scale_factor[0], position[1] * self.scale_factor[1])
            screen_.blit(self.png, position)
            screen_.blit(self.id, (position[0] + 68 * self.scale_factor[0], position[1] + 98 * self.scale_factor[1]))
            screen_.blit(self.owner_name, (position[0] + 230 * self.scale_factor[0], position[1] + 98 * self.scale_factor[1]))
            screen_.blit(self.player_count, (position[0] + 1010 * self.scale_factor[0], position[1] + 98 * self.scale_factor[1]))

    class InputField:
        UNSELECTED_COLOR = (255, 255, 255)
        SELECTED_COLOR = (200, 200, 200)
        TEXT_COLOR = (140, 140, 140)

        def __init__(self, position, font, hidden=False):
            self.scale_factor = LobbyUI.scale_factor
            self.position = (position[0] * self.scale_factor[0], position[1] * self.scale_factor[1])
            self.scale = (450 * self.scale_factor[0], 60 * self.scale_factor[1])
            self.rect = pygame.Rect(self.position, self.scale)

            self.text = ""
            self.font = font

            self.selected = False
            self.hidden = hidden

        def draw_field(self, screen_):
            if self.selected:
                pygame.draw.rect(screen_, LobbyUI.InputField.SELECTED_COLOR, self.rect)
            else:
                pygame.draw.rect(screen_, LobbyUI.InputField.UNSELECTED_COLOR, self.rect)


            if self.hidden:
                text = "•" * len(self.text)
            else:
                text = self.text

            field_text = self.font.render(text, False, LobbyUI.InputField.TEXT_COLOR)
            screen_.blit(field_text, (self.position[0] + 5 * self.scale_factor[0], self.position[1] + 22 * self.scale_factor[1]))

        def valid_input(self):
            if self.hidden:
                # password needs to be 8 or more character long
                if len(self.text) < 6:
                    return "is too short (minimum 6)"
                # password needs to contain letters and numbers
                elif not any(letter.isdigit() for letter in self.text) or not any(letter.isalpha() for letter in self.text):
                    return "needs to contain both letters and digits"
                else:
                    return "accepted"

                # username needs to be 3 or more character long
            elif len(self.text) < 3:
                return "is too short (minimum 3)"
            else:
                return "accepted"
