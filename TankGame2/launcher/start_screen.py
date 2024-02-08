import pygame


class Title:
    SCREEN_DIVIDER = 1

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("TANK GAME by Sahar Gazit")
        monitor_info = pygame.display.Info()
        screen = pygame.display.set_mode((int(monitor_info.current_w / Title.SCREEN_DIVIDER), int(monitor_info.current_h / Title.SCREEN_DIVIDER)))

        running = True
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

        pygame.quit()


if __name__ == "main":
    title = Title()
