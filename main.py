import pygame
import pygame.freetype
from pygame.sprite import Sprite
from pygame.rect import Rect
from enum import Enum
from math import cos, sin, pi, atan2

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BACKGROUND = (64, 64, 64)
SPRITE_BACKGROUND = (206, 229, 241)

textures = {
    '1': pygame.image.load('wallFinal1.png'),
    '2': pygame.image.load('wallFinal2.png'),
    '3': pygame.image.load('wallFinal3.png'),
    '4': pygame.image.load('wallFinal4.png'),
    '5': pygame.image.load('wallFinal5.png')
}

enemies = [
    {
        "x": 100,
        "y": 200,
        "texture": pygame.image.load('enemy1.png')
    },

    {
        "x": 270,
        "y": 200,
        "texture": pygame.image.load('enemy2.png')
    },

    {
        "x": 320,
        "y": 420,
        "texture": pygame.image.load('enemy2.png')
    },

    {
        "x": 102,
        "y": 200,
        "texture": pygame.image.load('enemy1.png')
    },

    {
        "x": 200,
        "y": 300,
        "texture": pygame.image.load('enemy3.png')
    }
]

background = pygame.image.load('bg1.png')
walk = pygame.image.load('wolf.png')

walk = pygame.transform.scale(walk, (150, 150))


class RayCaster(object):
    def __init__(self, screen):
        self.screen = screen
        _, _, self.width, self.height = screen.get_rect()

        self.map = []
        self.block_size = 50
        self.wallHeight = 50
        self.z_buffer = [-float('inf') for z in range(int(self.width / 2))]

        self.step_size = 5

        self.player = {
            "x": 75,
            "y": 175,
            "angle": 0,
            "fov": 60
        }

    def load_map(self, filename):
        with open(filename) as f:
            for line in f.readlines():
                self.map.append(list(line))

    def play_step(self):
        pygame.mixer.music.load('sound.mp3')
        pygame.mixer.music.play(0)

    def draw_rect(self, x, y, texture):
        texture = pygame.transform.scale(texture, (self.block_size, self.block_size))
        rect = texture.get_rect()
        rect = rect.move((x, y))
        self.screen.blit(texture, rect)

    def draw_player_icon(self, color):
        rect = (self.player['x'] - 2, self.player['y'] - 2, 5, 5)
        self.screen.fill(color, rect)

    def draw_sprite(self, sprite, size):
        # Pitagoras
        sprite_dist = ((self.player['x'] - sprite['x']) ** 2 + (self.player['y'] - sprite['y']) ** 2) ** 0.5

        # Angulo entre el personaje y el sprite, arco tangente 2
        sprite_angle = atan2(sprite['y'] - self.player['y'], sprite['x'] - self.player['x'])

        aspect_ratio = sprite["texture"].get_width() / sprite["texture"].get_height()
        sprite_height = (self.height / sprite_dist) * size
        sprite_width = sprite_height * aspect_ratio

        # Convertir a radianes
        angle_rads = self.player['angle'] * pi / 180
        fov_rads = self.player['fov'] * pi / 180

        # Buscamos el punto inicial para dibujar el sprite
        start_x = (self.width * 3 / 4) + (sprite_angle - angle_rads) * (self.width / 2) / fov_rads - (sprite_width / 2)
        start_y = (self.height / 2) - (sprite_height / 2)
        start_x = int(start_x)
        start_y = int(start_y)

        for x in range(start_x, int(start_x + sprite_width)):
            for y in range(start_y, int(start_y + sprite_height)):
                if (self.width / 2) < x < self.width:
                    if self.z_buffer[x - int(self.width / 2)] >= sprite_dist:
                        tx = int((x - start_x) * sprite["texture"].get_width() / sprite_width)
                        ty = int((y - start_y) * sprite["texture"].get_height() / sprite_height)
                        tex_color = sprite["texture"].get_at((tx, ty))
                        if tex_color[3] > 128 and tex_color != SPRITE_BACKGROUND:
                            self.screen.set_at((x, y), tex_color)
                            self.z_buffer[x - int(self.width / 2)] = sprite_dist

    def cast_ray(self, a):
        rads = a * pi / 180
        dist = 0
        while True:
            x = int(self.player['x'] + dist * cos(rads))
            y = int(self.player['y'] + dist * sin(rads))

            i = int(x / self.block_size)
            j = int(y / self.block_size)

            if self.map[j][i] != ' ':
                hit_x = x - i * self.block_size
                hit_y = y - j * self.block_size

                if 1 < hit_x < self.block_size - 1:
                    max_hit = hit_x
                else:
                    max_hit = hit_y

                tx = max_hit / self.block_size

                return dist, self.map[j][i], tx

            self.screen.set_at((x, y), WHITE)

            dist += 5

    def render(self):

        half_width = int(self.width / 2)
        half_height = int(self.height / 2)

        for x in range(0, half_width, self.block_size):
            for y in range(0, self.height, self.block_size):

                i = int(x / self.block_size)
                j = int(y / self.block_size)

                if self.map[j][i] != ' ':
                    self.draw_rect(x, y, textures[self.map[j][i]])

        self.draw_player_icon(BLACK)

        for i in range(half_width):
            angle = self.player['angle'] - self.player['fov'] / 2 + self.player['fov'] * i / half_width
            dist, wall_type, tx = self.cast_ray(angle)
            self.z_buffer[i] = dist
            x = half_width + i

            # perceivedHeight = screenHeight / (distance * cos( rayAngle - viewAngle) * wallHeight ----- Formula para el alto de las paredes
            h = self.height / (dist * cos((angle - self.player['angle']) * pi / 180)) * self.wallHeight

            start = int(half_height - h / 2)
            end = int(half_height + h / 2)
            # carga de imagenes para los bloques
            img = textures[wall_type]
            tx = int(tx * img.get_width())

            for y in range(start, end):
                ty = (y - start) / (end - start)
                ty = int(ty * img.get_height())
                tex_color = img.get_at((tx, ty))
                self.screen.set_at((x, y), tex_color)

        for enemy in enemies:
            self.screen.fill(pygame.Color("black"), (enemy['x'], enemy['y'], 3, 3))
            self.draw_sprite(enemy, 30)

        for i in range(self.height):
            self.screen.set_at((half_width, i), BLACK)
            self.screen.set_at((half_width + 1, i), BLACK)
            self.screen.set_at((half_width - 1, i), BLACK)


def create_surface_with_text(text, font_size, text_rgb, bg_rgb):
    """ Returns surface with text written on """
    font = pygame.freetype.SysFont("Arial", font_size, bold=True)
    surface, _ = font.render(text=text, fgcolor=text_rgb, bgcolor=bg_rgb)
    return surface.convert_alpha()


class ElementUI(Sprite):
    def __init__(self, position, text, font_size, background_color, text_color, action=None):
        self.mouse_over = False  # true if the mouse over the text

        # create the default title, normal size
        default_image = create_surface_with_text(
            text=text, font_size=font_size, text_rgb=text_color, bg_rgb=background_color
        )

        # creates title 1.2 time bigger when mouse over it
        highlighted_image = create_surface_with_text(
            text=text, font_size=font_size * 1.2, text_rgb=text_color, bg_rgb=background_color
        )

        # add both images and their rects to lists
        self.images = [default_image, highlighted_image]
        self.rects = [
            default_image.get_rect(center=position),
            highlighted_image.get_rect(center=position),
        ]

        self.action = action  # the actions called when clicked

        # calls the init method of the parent sprite class
        super().__init__()

    @property
    def image(self):
        return self.images[1] if self.mouse_over else self.images[0]

    @property
    def rect(self):
        return self.rects[1] if self.mouse_over else self.rects[0]

    # can tell if mouse is over or clicked
    def update(self, mouse_pos, mouse_up):
        if self.rect.collidepoint(mouse_pos):
            self.mouse_over = True
            if mouse_up:
                return self.action
        else:
            self.mouse_over = False

    def draw(self, surface):
        # title into screen
        surface.blit(self.image, self.rect)


class GameState(Enum):
    QUIT = -1
    TITLE = 0
    NEWGAME = 1


def main():
    pygame.init()

    screen = pygame.display.set_mode((1000, 500))
    game_state = GameState.TITLE

    while True:
        if game_state == GameState.TITLE:
            game_state = title_screen(screen)
        if game_state == GameState.NEWGAME:
            game_state = play_level(screen)
        if game_state == GameState.QUIT:
            pygame.quit()
            return


def title_screen(screen):
    # title
    game_btn = ElementUI(
        position=(500, 200),
        font_size=50,
        background_color=BLACK,
        text_color=WHITE,
        text="CASTLEVANIA",
    )
    # start button
    start_btn = ElementUI(
        position=(500, 300),
        font_size=30,
        background_color=BLACK,
        text_color=WHITE,
        text="Start",
        action=GameState.NEWGAME,
    )
    # quit button
    quit_btn = ElementUI(
        position=(500, 400),
        font_size=30,
        background_color=BLACK,
        text_color=WHITE,
        text="Quit",
        action=GameState.QUIT,
    )

    buttons = [start_btn, quit_btn, game_btn]

    while True:
        mouse_up = False
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_up = True

        screen.blit(background, (-600, -550))
        screen.blit(walk, (600, 250))

        for button in buttons:
            ui_action = button.update(pygame.mouse.get_pos(), mouse_up)
            if ui_action is not None:
                return ui_action
            button.draw(screen)

        pygame.display.flip()


def play_level(screen):
    return_btn = ElementUI(
        position=(870, 450),
        font_size=20,
        background_color=BLACK,
        text_color=WHITE,
        text="Back to main menu",
        action=GameState.TITLE,
    )
    pygame.init()
    screen = pygame.display.set_mode((1000, 500), pygame.DOUBLEBUF | pygame.HWACCEL)  # , pygame.FULLSCREEN)
    screen.set_alpha(None)
    pygame.display.set_caption('Proyecto')
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 30)

    def update_fps():
        fps = str(int(clock.get_fps()))
        fps = font.render(fps, 1, pygame.Color("white"))
        return fps

    r = RayCaster(screen)
    r.load_map('map2.txt')
    is_running = True

    while is_running:
        mouse_up = False
        return_btn.draw(screen)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                is_running = False
            if ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                mouse_up = True

            ui_action = return_btn.update(pygame.mouse.get_pos(), mouse_up)
            if ui_action is not None:
                return ui_action

            pygame.display.flip()
            # to substitute below values
            new_x = r.player['x']
            new_y = r.player['y']
            # programación de los in

            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    is_running = False
                elif ev.key == pygame.K_w:
                    new_x += cos(r.player['angle'] * pi / 180) * r.step_size
                    new_y += sin(r.player['angle'] * pi / 180) * r.step_size
                    r.play_step()
                elif ev.key == pygame.K_s:
                    new_x -= cos(r.player['angle'] * pi / 180) * r.step_size
                    new_y -= sin(r.player['angle'] * pi / 180) * r.step_size
                    r.play_step()
                elif ev.key == pygame.K_a:
                    new_x -= cos((r.player['angle'] + 90) * pi / 180) * r.step_size
                    new_y -= sin((r.player['angle'] + 90) * pi / 180) * r.step_size
                    r.play_step()
                elif ev.key == pygame.K_d:
                    new_x += cos((r.player['angle'] + 90) * pi / 180) * r.step_size
                    new_y += sin((r.player['angle'] + 90) * pi / 180) * r.step_size
                    r.play_step()
                elif ev.key == pygame.K_q:
                    r.player['angle'] -= 5
                elif ev.key == pygame.K_e:
                    r.player['angle'] += 5

                i = int(new_x / r.block_size)
                j = int(new_y / r.block_size)

                if r.map[j][i] == ' ':
                    r.player['x'] = new_x
                    r.player['y'] = new_y
            if ev.type == pygame.MOUSEBUTTONDOWN or ev.type == pygame.MOUSEBUTTONUP:
                if ev.button == 4:
                    r.player['angle'] -= 5
                if ev.button == 5:
                    r.player['angle'] += 5

        screen.fill(pygame.Color("grey"))  # Fondo

        # Techo
        screen.fill(pygame.Color("black"), (int(r.width / 2), 0, int(r.width / 2), int(r.height / 2)))

        # Piso
        screen.fill(pygame.Color("grey"), (int(r.width / 2), int(r.height / 2), int(r.width / 2), int(r.height / 2)))
        r.render()
        # FPS
        screen.fill(pygame.Color("black"), (0, 0, 30, 30))
        screen.blit(update_fps(), (0, 0))
        clock.tick(30)
        pygame.display.update()
    pygame.quit()


if __name__ == "__main__":
    main()
