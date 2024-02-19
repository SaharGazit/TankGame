import pygame


class Title:

    @staticmethod
    def main():
        # initiate program
        pygame.init()
        pygame.display.set_caption('TANK GAME')

        # technical
        monitor_info = pygame.display.Info()
        screen = pygame.display.set_mode((int(monitor_info.current_w), int(monitor_info.current_h)))
        title_font = pygame.font.Font("resources\\font1.ttf", 90)
        button_text_font = pygame.font.SysFont("None", 50)

        # buttons and texts
        title_text = title_font.render('TANK GAME', False, (0, 0, 0))
        quit_button_text = button_text_font.render('Quit', False, (0, 0, 0))
        quit_button = pygame.Rect((100, 800), (300, 70))

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
                        if quit_button.collidepoint(mouse_x, mouse_y):
                            running = False


            screen.fill((153, 230, 255))
            screen.blit(title_text, (75, 75))
            pygame.draw.rect(screen, (255, 255, 255), quit_button)
            screen.blit(quit_button_text, (215, 815))
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    Title.main()
