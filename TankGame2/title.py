import pygame


class Title:
    BACKGROUND_COLOR = (50, 164, 168)

    def main(self):
        class Button:
            FONT = pygame.font.SysFont("None", 50)

            def __init__(self, position, scale, text):
                self.rect = pygame.Rect(position, scale)
                self.text = Button.FONT.render(text, False, (0, 0, 0))

            def draw_button(self, screen):
                pygame.draw.rect(screen, (255, 255, 255), self.rect)
                screen.blit(self.text, (self.rect.x + 115, self.rect.y + 15))

            def get_rect(self):
                return self.rect

        # initiate program
        pygame.init()
        pygame.display.set_caption('TANK GAME')

        # technical
        monitor_info = pygame.display.Info()
        screen = pygame.display.set_mode((int(monitor_info.current_w), int(monitor_info.current_h)))
        title_font = pygame.font.Font("resources\\font1.ttf", 90)

        # buttons and texts
        title_text = title_font.render('TANK GAME', False, (0, 0, 0))
        quit_button = Button((100, 800), (300, 70), 'Quit')

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
                        if quit_button.get_rect().collidepoint(mouse_x, mouse_y):
                            running = False

            # background
            screen.fill(Title.BACKGROUND_COLOR)

            # title (TANK GAME)
            screen.blit(title_text, (75, 75))

            # quit button
            quit_button.draw_button(screen)

            pygame.display.flip()

        pygame.quit()






if __name__ == "__main__":
    pygame.init()
    title = Title()
    title.main()
