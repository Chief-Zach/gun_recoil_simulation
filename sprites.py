import pygame
WHITE = (255, 255, 255)
class MyRect(pygame.sprite.Sprite):
    def __init__(self, aspect, image, length):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load(image).convert_alpha()
        # self.image.set_colorkey((0, 0, 0))  # Set black as the transparent color
        # Resize if width and height are provided
        width = 500 * length / 100
        self.image = pygame.transform.scale(self.image, (width, width/aspect))

        self.rect = self.image.get_rect()
        self.picked = False


    def set_pos(self, pos):
        self.rect.x = pos[0] - self.rect.width // 2
        self.rect.y = pos[1] - self.rect.height // 2

    def update(self):
        pass

class MyText():
    def __init__(self, color, background=WHITE, antialias=True, fontname="comicsansms", fontsize=16):
        pygame.font.init()
        self.font = pygame.font.SysFont(fontname, fontsize)
        self.color = color
        self.background = background
        self.antialias = antialias

    def draw(self, str1, screen, pos):
        text = self.font.render(str1, self.antialias, self.color, self.background)
        screen.blit(text, pos)

def to_screen(x, y, win_width, win_height):
    return win_width // 2 + x, win_height // 2 - y


def from_screen(x, y, win_width, win_height):
    return x - win_width // 2, win_height // 2 - y
