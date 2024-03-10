import pygame
import sys
import math
from pygame.locals import *

# Initialize Pygame
pygame.init()

# Set up the window
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Mouse Rotation')

# Set up colors
BLACK = (0, 0, 0)

# Load the sprite
hull = pygame.image.load('../resources/tank_hull.png')
sprite_image = pygame.image.load('../resources/tank_turret.png').convert_alpha()
sprite_rect = sprite_image.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

# Main loop
running = False
while running:
    window.fill(BLACK)

    # Handle events
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    # Get the position of the mouse
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Calculate the angle between the sprite and the mouse position
    dx = mouse_x - sprite_rect.centerx
    dy = mouse_y - sprite_rect.centery
    angle = math.atan2(dy, dx)
    angle_degrees = math.degrees(angle) + 90

    # Rotate the sprite
    rotated_sprite = pygame.transform.rotate(sprite_image, -angle_degrees)
    rotated_rect = rotated_sprite.get_rect(center=sprite_rect.center)

    # draw hull
    window.blit(hull, hull.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)))

    # Draw the rotated sprite onto the window
    window.blit(rotated_sprite, rotated_rect)

    # Update the display
    pygame.display.flip()
