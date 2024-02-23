import pygame


class Title:
    BACKGROUND_COLOR = (230, 230, 230)

    def main(self):
        class Button:
            FONT = pygame.font.Font("resources\\font2.otf", 50)
            TEXTURE = pygame.image.load("resources/button.png")

            def __init__(self, position, scale, text, text_position):
                self.png = pygame.transform.smoothscale(Button.TEXTURE, scale)
                self.position = position

                # true if the player's mouse is on the button
                self.hovered = False

                self.text = text
                self.text_position = text_position

            def draw_button(self, screen_):
                # change button attributes if they are hovered
                if self.hovered:
                    text_color = (181, 22, 7)
                    position = (self.position[0], self.position[1] + 5)
                else:
                    text_color = (4, 0, 87)
                    position = self.position

                # draw the button and its text with fixed positions
                screen_.blit(self.png, position)
                text_obj = Button.FONT.render(self.text, False, text_color)
                screen_.blit(text_obj, (position[0] + self.text_position, position[1] + 25))

            # get the button's rect
            def get_rect(self):
                rect = self.png.get_rect()
                rect.x = self.position[0]
                rect.y = self.position[1]
                return rect

        class Window:
            def __init__(self):
                self.png = pygame.transform.smoothscale(pygame.image.load("resources/panel.png"), (700, 700))
                self.position = (1100, 100)

            def draw_window(self, screen_):
                screen_.blit(self.png, self.position)


        # initiate program
        pygame.init()
        pygame.display.set_caption('TANK GAME')

        # technical
        monitor_info = pygame.display.Info()
        screen = pygame.display.set_mode((int(monitor_info.current_w), int(monitor_info.current_h)))
        title_font = pygame.font.Font("resources\\font1.ttf", 90)

        # buttons and texts
        title_text = title_font.render('TANK GAME', False, (0, 0, 0))

        play_button = Button((100, 400), (400, 100), 'Play', 115)
        account_button = Button((100, 600), (400, 100), 'Account', 60)
        quit_button = Button((100, 800), (400, 100), 'Quit', 125)
        quit_window = Window()

        button_list = [play_button, account_button, quit_button]
        activated_window = None

        running = True
        while running:
            for event in pygame.event.get():
                # if user closes the window, stop the game from running.
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                # left click events
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:

                        # check if another window is open
                        if activated_window is None:
                            # pressed play button
                            if play_button.get_rect().collidepoint(mouse_x, mouse_y):
                                activated_window = None

                            # pressed quit button
                            elif quit_button.get_rect().collidepoint(mouse_x, mouse_y):
                                activated_window = quit_window

                            # pressed no button
                            else:
                                # reset buttons
                                button_list = [play_button, account_button, quit_button]

                # update buttons hovering
                for button in button_list:
                    if activated_window is None:
                        button.hovered = False
                        if button.get_rect().collidepoint(mouse_x, mouse_y):
                            button.hovered = True

            # background
            screen.fill(Title.BACKGROUND_COLOR)

            # title (TANK GAME)
            screen.blit(title_text, (75, 75))

            # buttons
            for button in button_list:
                button.draw_button(screen)

            # side-window
            if activated_window is not None:
                activated_window.draw_window(screen)

            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    pygame.init()
    title = Title()
    title.main()
