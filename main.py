import pygame

from math import cos, sin, pi

# Si estan en C++, pueden utilizar SDL

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BACKGROUND = (64, 64, 64)

colors = {
    '1': (255, 0, 0),
    '2': (0, 255, 0),
    '3': (0, 0, 255)
}


class RayCaster(object):
    def __init__(self, screen):
        self.screen = screen
        _, _, self.width, self.height = screen.get_rect()

        self.map = []
        self.block_size = 50
        self.wallHeight = 50

        self.stepSize = 5

        self.set_color(WHITE)

        self.player = {
            "x": 75,
            "y": 175,
            "angle": 0,
            "fov": 60
        }

    def set_color(self, color):
        self.block_color = color

    def load_map(self, filename):
        with open(filename) as f:
            for line in f.readlines():
                self.map.append(list(line))

    def draw_rect(self, x, y, color=WHITE):
        rect = (x, y, self.block_size, self.block_size)
        self.screen.fill(color, rect)

    def draw_player_icon(self, color):
        rect = (self.player['x'] - 2, self.player['y'] - 2, 5, 5)
        self.screen.fill(color, rect)

    def cast_ray(self, a):
        rads = a * pi / 180
        dist = 0
        while True:
            x = int(self.player['x'] + dist * cos(rads))
            y = int(self.player['y'] + dist * sin(rads))

            i = int(x / self.block_size)
            j = int(y / self.block_size)

            if self.map[j][i] != ' ':
                return dist, self.map[j][i]

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
                    self.draw_rect(x, y, colors[self.map[j][i]])

        self.draw_player_icon(BLACK)

        for i in range(half_width):
            angle = self.player['angle'] - self.player['fov'] / 2 + self.player['fov'] * i / half_width
            dist, c = self.cast_ray(angle)

            x = half_width + i

            # perceivedHeight = screenHeight / (distance * cos( rayAngle - viewAngle) * wallHeight
            h = self.height / (dist * cos((angle - self.player['angle']) * pi / 180)) * self.wallHeight

            start = int(half_height - h / 2)
            end = int(half_height + h / 2)

            for y in range(start, end):
                self.screen.set_at((x, y), colors[c])

        for i in range(self.height):
            self.screen.set_at((half_width, i), BLACK)
            self.screen.set_at((half_width + 1, i), BLACK)
            self.screen.set_at((half_width - 1, i), BLACK)


pygame.init()
screen = pygame.display.set_mode((1000, 500))  # , pygame.FULLSCREEN)

r = RayCaster(screen)

r.set_color((128, 0, 0))
r.load_map('map.txt')

isRunning = True

while isRunning:

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            isRunning = False

        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                isRunning = False
            elif ev.key == pygame.K_w:
                r.player['x'] += cos(r.player['angle'] * pi / 180) * r.stepSize
                r.player['y'] += sin(r.player['angle'] * pi / 180) * r.stepSize
            elif ev.key == pygame.K_s:
                r.player['x'] -= cos(r.player['angle'] * pi / 180) * r.stepSize
                r.player['y'] -= sin(r.player['angle'] * pi / 180) * r.stepSize
            elif ev.key == pygame.K_a:
                r.player['x'] -= cos((r.player['angle'] + 90) * pi / 180) * r.stepSize
                r.player['y'] -= sin((r.player['angle'] + 90) * pi / 180) * r.stepSize
            elif ev.key == pygame.K_d:
                r.player['x'] += cos((r.player['angle'] + 90) * pi / 180) * r.stepSize
                r.player['y'] += sin((r.player['angle'] + 90) * pi / 180) * r.stepSize
            elif ev.key == pygame.K_q:
                r.player['angle'] -= 5
            elif ev.key == pygame.K_e:
                r.player['angle'] += 5

    screen.fill(BACKGROUND)
    r.render()

    pygame.display.flip()

pygame.quit()
