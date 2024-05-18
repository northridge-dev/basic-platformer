from os.path import join
import pygame

pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_VEL = 5

pygame.display.set_caption("Legend of Ninja Frog")
window = pygame.display.set_mode((WIDTH, HEIGHT))


class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)

    def __init__(self, x, y, width, height):
        # initialize the super class
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(x, y, width, height)

        # decompose motion into x and y components
        self.x_vel = 0
        self.y_vel = 0

        self.direction = "left"
        self.animation_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        """Called on every game loop tick; moves the player"""
        self.move(self.x_vel, self.y_vel)

    def draw(self, window):
        pygame.draw.rect(window, self.COLOR, self.rect)


def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()

    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            top_left_corner = (i * width, j * height)
            tiles.append(top_left_corner)

    return tiles, image


def draw(window, background, bg_image, player):
    for tile in background:
        window.blit(bg_image, tile)

    player.draw(window)

    pygame.display.update()


def handle_move(player):
    # `keys` is a tuple of boolean values; each position corresponds to a key
    keys = pygame.key.get_pressed()

    # stop the player if no key is pressed
    player.x_vel = 0

    if keys[pygame.K_LEFT]:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT]:
        player.move_right(PLAYER_VEL)


def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")
    player = Player(100, 100, 50, 50)

    running = True
    while running:
        clock.tick(FPS)

        # check for game-level events; player-level events handled in `handle_move`
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

        handle_move(player)  # process player-level input
        player.loop(FPS)  # update player
        draw(window, background, bg_image, player)  # draw new frame

    pygame.quit()
    quit()


if __name__ == "__main__":
    main(window)
