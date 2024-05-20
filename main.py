from os import listdir
from os.path import isfile, join
import pygame

pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_VEL = 5

pygame.display.set_caption("Legend of Ninja Frog")
window = pygame.display.set_mode((WIDTH, HEIGHT))


def flip(sprites):
    # flip all spirtes in list around the y-axis
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    image_files = [f for f in listdir(path) if isfile(join(path, f))]

    sprites = {}

    for image_file in image_files:
        sprite_sheet = pygame.image.load(join(path, image_file)).convert_alpha()

        sprites_list = []

        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites_list.append(pygame.transform.scale2x(surface))

        if direction:
            sprites[image_file.replace(".png", "") + "_right"] = sprites_list
            sprites[image_file.replace(".png", "") + "_left"] = flip(sprites_list)
        else:
            sprites[image_file.replace(".png", "")] = sprites_list

    return sprites


def load_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    JUMP_MAGNITUDE = 8
    SPRITES = load_sprite_sheets("MainCharacters", "NinjaFrog", 32, 32, direction=True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        # initialize the super class
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)

        # decompose motion into x and y components
        self.x_vel = 0
        self.y_vel = 0

        self.direction = "left"
        self.animation_count = 0

        self.mask = None

        self.fall_count = 0
        self.jump_count = 0

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

    def jump(self):
        self.y_vel = -self.GRAVITY * self.JUMP_MAGNITUDE
        self.animation_count = 0

        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def loop(self, fps):
        """Called on every game loop tick; moves the player"""
        # apply gravity
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        self.fall_count += 1
        self.update_sprite()

    def update_sprite(self):
        sprite_sheet_base = "idle"

        # if moving, use "run" sprites
        if self.x_vel != 0:
            sprite_sheet_base = "run"

        # load direction-specific sprites
        sprite_sheet = sprite_sheet_base + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet]

        # rotate through sprites to animate
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1

        self.update_rect_and_mask()

    def update_rect_and_mask(self):
        # resize the rectangle to match the current sprite; keep same position
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        # set mask for more precise collision detection
        # see https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.collide_mask
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, window):
        window.blit(self.sprite, (self.rect.x, self.rect.y))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA, 32)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, window):
        window.blit(self.image, (self.rect.x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = load_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()

    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            top_left_corner = (i * width, j * height)
            tiles.append(top_left_corner)

    return tiles, image


def draw(window, background, bg_image, player, objects):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window)

    player.draw(window)

    pygame.display.update()


def handle_vertical_collision(player, objects, y_vel):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if y_vel > 0:  # falling
                player.rect.bottom = obj.rect.top
                player.landed()
            elif y_vel < 0:  # jumping
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects


def handle_move(player, objects):
    # `keys` is a tuple of boolean values; each position corresponds to a key
    keys = pygame.key.get_pressed()

    # stop the player if no key is pressed
    player.x_vel = 0

    if keys[pygame.K_LEFT]:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT]:
        player.move_right(PLAYER_VEL)

    handle_vertical_collision(player, objects, player.y_vel)


def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")

    block_size = 96

    player = Player(100, 100, 50, 50)

    # floor blocks extend 3x the width of the game window
    floor = [
        Block(i * block_size, HEIGHT - block_size, block_size)
        for i in range(-WIDTH // block_size, (WIDTH * 2) // block_size)
    ]

    # accumulate all objects to pass to draw function
    objects = floor

    running = True
    while running:
        clock.tick(FPS)

        # check for game-level events; player-level events handled in `handle_move`
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()

        # player.loop must preceed handle_move so mask is not None
        player.loop(FPS)  # update player
        handle_move(player, objects)  # process player-level input
        draw(window, background, bg_image, player, objects)  # draw new frame

    pygame.quit()
    quit()


if __name__ == "__main__":
    main(window)
