import pygame


class Title:
    angle = 0
    image = pygame.image.load("resources/tankbody.png")

    @staticmethod
    def main():
        # initiate program
        pygame.init()
        pygame.display.set_caption('TANK GAME')

        monitor_info = pygame.display.Info()
        screen = pygame.display.set_mode((int(monitor_info.current_w), int(monitor_info.current_h)))

        running = True
        while running:
            for event in pygame.event.get():
                # if user closes the window, stop the game from running.
                if event.type == pygame.QUIT:
                    running = False

            screen.fill((159, 168, 191))

            Title.rotate(screen, 100)
            pygame.display.flip()

        pygame.quit()


    @staticmethod
    def rotate(surf, top_left):
        rotated_image = pygame.transform.rotate(Title.image, Title.angle)
        new_rect = rotated_image.get_rect(center=Title.image.get_rect(topleft=top_left).center)

        surf.blit(rotated_image, new_rect)


Title.main()
