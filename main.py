import pygame

pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_VEL = 5

pygame.display.set_caption("Legend of Ninja Frog")
window = pygame.display.set_mode((WIDTH, HEIGHT))


def main(window):
    clock = pygame.time.Clock()

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

    pygame.quit()
    quit()


if __name__ == "__main__":
    main(window)
