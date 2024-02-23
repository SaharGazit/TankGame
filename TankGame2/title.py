import pygame


class Title:
    BACKGROUND_COLOR = (50, 164, 168)

    def main(self):
        class Button:
            FONT = pygame.font.SysFont("None", 50)

            def __init__(self, position, scale, text, text_position):
                self.rect = pygame.Rect(position, scale)
                self.text = Button.FONT.render(text, False, (0, 0, 0))


                self.text_position = text_position

            def draw_button(self, screen_):
                pygame.draw.rect(screen_, (255, 255, 255), self.rect)
                screen_.blit(self.text, (self.rect.x + self.text_position, self.rect.y + 15))

            def get_rect(self):
                return self.rect

        class Window:
            pass

        # initiate program
        pygame.init()
        pygame.display.set_caption('TANK GAME')

        # technical
        monitor_info = pygame.display.Info()
        screen = pygame.display.set_mode((int(monitor_info.current_w), int(monitor_info.current_h)))
        title_font = pygame.font.Font("resources\\font1.ttf", 90)

        # buttons and texts
        title_text = title_font.render('TANK GAME', False, (0, 0, 0))

        play_button = Button((100, 400), (300, 70), 'Play', 115)
        online_button = Button((500, 400), (150, 70), 'online', 27)
        lan_button = Button((750, 400), (150, 70), 'LAN', 40)
        debug_button = Button((1000, 400), (150, 70), 'debug', 25)
        play_tab_open = False

        account_button = Button((100, 600), (300, 70), 'Account', 80)

        quit_button = Button((100, 800), (300, 70), 'Quit', 115)
        confirm_quit_button = Button((500, 800), (150, 70), 'sure?', 35)
        quit_tab_open = False

        button_list = [play_button, account_button, quit_button]

        running = True
        while running:
            for event in pygame.event.get():
                # if user closes the window, stop the game from running.
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_x, mouse_y = event.pos
                        # pressed play button
                        if play_button.get_rect().collidepoint(mouse_x, mouse_y):
                            if play_tab_open:
                                # remove buttons after pressing again
                                button_list.remove(online_button)
                                button_list.remove(lan_button)
                                button_list.remove(debug_button)
                            else:
                                # show game mode buttons
                                button_list.append(online_button)
                                button_list.append(lan_button)
                                button_list.append(debug_button)

                            # switch play tab mode
                            play_tab_open = not play_tab_open

                        # pressed quit button
                        elif quit_button.get_rect().collidepoint(mouse_x, mouse_y):
                            if quit_tab_open:
                                # remove button after pressing again
                                button_list.remove(confirm_quit_button)
                            else:
                                # show confirm button
                                button_list.append(confirm_quit_button)

                            # switch quit tab mode
                            quit_tab_open = not quit_tab_open

                        # pressed quit confirm button
                        elif confirm_quit_button.get_rect().collidepoint(mouse_x, mouse_y):
                            running = False

                        # pressed no button
                        else:
                            # reset buttons
                            button_list = [play_button, account_button, quit_button]
                            play_tab_open = False
                            quit_tab_open = False

            # background
            screen.fill(Title.BACKGROUND_COLOR)

            # title (TANK GAME)
            screen.blit(title_text, (75, 75))

            # static buttons
            for button in button_list:
                button.draw_button(screen)

            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    pygame.init()
    title = Title()
    title.main()
