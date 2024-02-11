import pygame


class Title:

    @staticmethod
    def main():
        # initiate program
        pygame.init()
        pygame.display.set_caption('TANK GAME')
        title_font = pygame.font.SysFont("None", 30)
        title_text = title_font.render('TANK GAME', False, (0, 0, 0))

        monitor_info = pygame.display.Info()
        screen = pygame.display.set_mode((int(monitor_info.current_w), int(monitor_info.current_h)))

        running = True
        while running:
            for event in pygame.event.get():
                # if user closes the window, stop the game from running.
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            screen.fill((159, 168, 191))
            screen.blit(title_text, (100, 100))
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    Title.main()
