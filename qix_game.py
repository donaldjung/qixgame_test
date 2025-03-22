import pygame
import sys
import random
from pygame.locals import *

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Qix Game")

# Colors
BLACK = (0, 0, 0)      # Unclaimed area
WHITE = (255, 255, 255) # Drawing path
BLUE = (0, 0, 255)     # Claimed area
RED = (255, 0, 0)      # Player
GREEN = (0, 255, 0)    # Qix

# Playfield surface
playfield = pygame.Surface((WIDTH, HEIGHT))
playfield.fill(BLACK)  # Initially unclaimed

# Claim the border (2 pixels wide for clarity)
BORDER_WIDTH = 2
playfield.fill(BLUE, (0, 0, WIDTH, BORDER_WIDTH))          # Top
playfield.fill(BLUE, (0, HEIGHT-BORDER_WIDTH, WIDTH, BORDER_WIDTH))  # Bottom
playfield.fill(BLUE, (0, 0, BORDER_WIDTH, HEIGHT))         # Left
playfield.fill(BLUE, (WIDTH-BORDER_WIDTH, 0, BORDER_WIDTH, HEIGHT))  # Right

# Unclaimed mask
unclaimed_mask = pygame.Mask((WIDTH, HEIGHT))
unclaimed_mask.fill()  # All pixels set to 1
for x in range(WIDTH):
    for y in range(BORDER_WIDTH):
        unclaimed_mask.set_at((x, y), 0)  # Top
        unclaimed_mask.set_at((x, HEIGHT-1-y), 0)  # Bottom
for y in range(HEIGHT):
    for x in range(BORDER_WIDTH):
        unclaimed_mask.set_at((x, y), 0)  # Left
        unclaimed_mask.set_at((WIDTH-1-x, y), 0)  # Right

# Player variables
player_pos = [BORDER_WIDTH, BORDER_WIDTH]  # Start on top-left corner of unclaimed area next to border
is_drawing = False
path = []
current_direction = None

# Qix variables
qix_pos = [WIDTH // 2, HEIGHT // 2]
qix_speed = 2
qix_direction = [1, 0]

# Path surface
path_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
path_surface.fill((0, 0, 0, 0))

# Check if position is on the edge or border
def is_on_edge(pos):
    x, y = pos
    # Allow movement on claimed border or unclaimed pixels next to it
    if playfield.get_at((x, y)) == BLUE:
        return True
    if playfield.get_at((x, y)) != BLACK:
        return False
    # Check adjacency to claimed area
    for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < WIDTH and 0 <= ny < HEIGHT and playfield.get_at((nx, ny)) == BLUE:
            return True
    return False

# Main game loop
clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # Handle player movement
    keys = pygame.key.get_pressed()
    dx, dy = 0, 0
    if keys[K_LEFT]:
        dx = -1
    elif keys[K_RIGHT]:
        dx = 1
    elif keys[K_UP]:
        dy = -1
    elif keys[K_DOWN]:
        dy = 1

    if dx != 0 or dy != 0:
        new_pos = [player_pos[0] + dx, player_pos[1] + dy]
        if 0 <= new_pos[0] < WIDTH and 0 <= new_pos[1] < HEIGHT:
            if not is_drawing:
                if is_on_edge(new_pos):
                    player_pos = new_pos
                else:
                    is_drawing = True
                    path = [player_pos.copy()]
                    current_direction = (dx, dy)
                    player_pos = new_pos
            else:
                if playfield.get_at(new_pos) == BLACK:
                    new_direction = (dx, dy)
                    if new_direction != current_direction:
                        path.append(player_pos.copy())
                        current_direction = new_direction
                    player_pos = new_pos
                    if is_on_edge(player_pos):
                        path.append(player_pos.copy())
                        path_surface.fill((0, 0, 0, 0))
                        if len(path) > 1:
                            pygame.draw.lines(path_surface, WHITE, False, path, 1)
                        path_mask = pygame.mask.from_surface(path_surface, threshold=1)
                        temp_mask = unclaimed_mask.copy()
                        temp_mask.erase(path_mask, (0, 0))
                        if len(path) >= 2:
                            p0, p1 = path[0], path[1]
                            if p0[0] == p1[0]:
                                seed1 = (max(0, p0[0] - 1), p0[1])
                                seed2 = (min(WIDTH-1, p0[0] + 1), p0[1])
                            else:
                                seed1 = (p0[0], max(0, p0[1] - 1))
                                seed2 = (p0[0], min(HEIGHT-1, p0[1] + 1))
                            if temp_mask.get_at(seed1):
                                connected_area = temp_mask.connected_component(seed1)
                                if not connected_area.get_at(qix_pos):
                                    for x in range(WIDTH):
                                        for y in range(HEIGHT):
                                            if connected_area.get_at((x, y)):
                                                playfield.set_at((x, y), BLUE)
                                                unclaimed_mask.set_at((x, y), 0)
                                else:
                                    if temp_mask.get_at(seed2):
                                        connected_area = temp_mask.connected_component(seed2)
                                        if not connected_area.get_at(qix_pos):
                                            for x in range(WIDTH):
                                                for y in range(HEIGHT):
                                                    if connected_area.get_at((x, y)):
                                                        playfield.set_at((x, y), BLUE)
                                                        unclaimed_mask.set_at((x, y), 0)
                        is_drawing = False
                        path = []

    # Move Qix
    new_qix_pos = [qix_pos[0] + qix_direction[0] * qix_speed, qix_pos[1] + qix_direction[1] * qix_speed]
    if (0 <= new_qix_pos[0] < WIDTH and 0 <= new_pos[1] < HEIGHT and 
        playfield.get_at(new_qix_pos) == BLACK and path_surface.get_at(new_qix_pos) == (0, 0, 0, 0)):
        qix_pos = new_qix_pos
    else:
        qix_direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])

    # Check collision
    if is_drawing and path_surface.get_at(qix_pos) != (0, 0, 0, 0):
        print("Collision! Player loses.")
        player_pos = [BORDER_WIDTH, BORDER_WIDTH]
        is_drawing = False
        path = []
        path_surface.fill((0, 0, 0, 0))

    # Render
    screen.fill(BLACK)
    screen.blit(playfield, (0, 0))
    if is_drawing:
        path_surface.fill((0, 0, 0, 0))
        if len(path) > 1:
            pygame.draw.lines(path_surface, WHITE, False, path + [player_pos], 1)
        elif len(path) == 1:
            pygame.draw.line(path_surface, WHITE, path[0], player_pos, 1)
        screen.blit(path_surface, (0, 0))
    pygame.draw.circle(screen, RED, player_pos, 5)    # Player
    pygame.draw.circle(screen, GREEN, qix_pos, 5)     # Qix
    pygame.display.flip()
    clock.tick(60)
