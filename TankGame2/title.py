import pygame


class Title:
    BACKGROUND_COLOR = (50, 164, 168)

    def main(self):
        class Button:
            FONT = pygame.font.SysFont("None", 50)

            def __init__(self, position, scale, text, mini=False):
                self.rect = pygame.Rect(position, scale)
                self.text = Button.FONT.render(text, False, (0, 0, 0))

                if mini:
                    pass
                else:
                    self.text_position = 115 - 10 * (len(text) - 4)

            def draw_button(self, screen):
                pygame.draw.rect(screen, (255, 255, 255), self.rect)
                screen.blit(self.text, (self.rect.x + self.text_position, self.rect.y + 15))

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
        play_button = Button((100, 400), (300, 70), 'Play')
        debug_button = Button((500, 400), (50, 50), 'debug')
        account_button = Button((100, 600), (300, 70), 'Account')
        quit_button = Button((100, 800), (300, 70), 'Quit')
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
                            # TODO: lan/online/debug
                            button_list.append(debug_button)

                        # pressed quit button
                        if quit_button.get_rect().collidepoint(mouse_x, mouse_y):
                            running = False

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
