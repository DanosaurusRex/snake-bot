import sys
import os
import random
from itertools import product
import pygame
from pygame.sprite import Sprite, Group
import neat

GRID_SIZE = 30
WIN_WIDTH = 1020
WIN_HEIGHT = 620
BG = 0, 0, 0
GEN = 0

class Walls():
    """Class to manage the walls."""
    def __init__(self, screen):
        """Initialise the game walls"""
        self.screen = screen
        self.rect = pygame.Rect(0, 0, 2+GRID_SIZE*20, 2+GRID_SIZE*20)
        self.rect.left = 9
        self.rect.top = 9
        self.color = 0, 255, 0

    def draw_walls(self):
        """Draw walls to screen."""
        pygame.draw.rect(self.screen, self.color, self.rect, 1)
    
    def collision(self, snake):
        in_area = self.rect.contains(snake.head.rect)
        if not in_area:
            return True
        return False


class Segment(Sprite):
    """Class to manage each segment of the snake."""
    def __init__(self, screen, x, y, color):
        super().__init__()
        self.screen = screen
        self.rect = pygame.Rect(0, 0, 20, 20)
        self.x = x
        self.y = y
        self.xdir = 0
        self.ydir = 0
        self.color = color

        self.rect.left = 10 + self.x * 20
        self.rect.top = 10 + self.y * 20

    def update(self):
        """Set the segment's coordinates and move them to position."""
        self.x = self.x + self.xdir
        self.y = self.y + self.ydir
        self.rect.left = 10 + self.x * 20
        self.rect.top = 10 + self.y * 20

    def draw_segment(self):
        """Draw the segment to the screen."""
        pygame.draw.rect(self.screen, self.color, self.rect)


class Snake():
    """Class to manage the snake."""
    def __init__(self, screen, x, y, color=(0,255,0), length=5):
        self.screen = screen
        self.xdir = 1
        self.ydir = 0
        self.direction = 2 # 1U, 2R, 3D, 4L
        self.body = []
        self.color = color
        for i in range(length):
            self.body.append(Segment(self.screen, x-i, y, self.color))
        self.head = self.body[0]
        self.tail = Group(self.body[1:])
        self.score = 0
        self.foods = Group()
        self.life = 200

    def __iter__(self):
        for segment in self.body:
            yield segment
    
    def __len__(self):
        return len(self.body)

    def update(self):
        """Enumerate backwards through segments.
        Set position of each segment from tail to head.
        Then update each segment.
        """
        for i, segment in enumerate(self.body[::-1], 1):
            pos = len(self) - i
            if pos == 0:
                segment.xdir = self.xdir
                segment.ydir = self.ydir
            else:
                segment.x = self.body[pos-1].x
                segment.y = self.body[pos-1].y
            segment.update()

    def move_left(self):
        if self.direction == 1:
            self.xdir = -1
            self.ydir = 0
            self.direction = 4
        elif self.direction == 4:
            self.xdir = 0
            self.ydir = 1
            self.direction = 3
        elif self.direction == 3:
            self.xdir = 1
            self.ydir = 0
            self.direction = 2
        elif self.direction == 2:
            self.xdir = 0
            self.ydir = -1
            self.direction = 1

    def move_right(self):
        if self.direction == 1:
            self.xdir = 1
            self.ydir = 0
            self.direction = 2
        elif self.direction == 2:
            self.xdir = 0
            self.ydir = 1
            self.direction = 3
        elif self.direction == 3:
            self.xdir = -1
            self.ydir = 0
            self.direction = 4
        elif self.direction == 4:
            self.xdir = 0
            self.ydir = -1
            self.direction = 1

    def grow(self):
        new = Segment(self.screen, self.body[-1].x, self.body[-1].y, self.color)
        self.body.append(new)
        self.tail.add(new)
        self.score += 1

    def draw_snake(self):
        """Draw segments of the snake."""
        for segment in self:
            segment.draw_segment()

    def spawn_food(self, coords):
        """Spawn food in an empty location if no food exists"""
        if not len(self.foods):
            snake_pos = set((segment.x, segment.y) for segment in self)
            food_locs = list(coords - snake_pos)
            x, y = random.choice(food_locs)
            self.foods.add(Food(self.screen, x, y, self.color))
    
    def self_collision(self):
        hit_tail = pygame.sprite.spritecollide(self.head, self.tail, False)
        if hit_tail:
            return True
        return False
    
    def food_position(self):
        for food in self.foods:
            return food.x, food.y

class Food(Sprite):
    def __init__(self, screen, x, y, color):
        super().__init__()
        self.screen = screen
        self.x = x
        self.y = y
        self.color = color
        self.rect = pygame.Rect(0, 0, 20, 20)
        self.rect.left = 10 + self.x * 20
        self.rect.top = 10 + self.y * 20

    def draw_food(self):
        pygame.draw.rect(self.screen, self.color, self.rect)


def check_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()


def update_screen(screen, snakes, walls):
    screen.fill(BG)
    walls.draw_walls()
    for snake in snakes:
        snake.draw_snake()
        for food in snake.foods:
            food.draw_food()
    pygame.display.update()


def food_eaten(snake):
    """Check snake-food collisions"""
    eaten = pygame.sprite.spritecollide(snake.head, snake.foods, True)
    if eaten:
        return True
    return False


def fitness(genomes, config):
    global GEN
    GEN += 1
    nets = []
    ge = []
    snakes = []

    screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pygame.display.set_caption('Snake')
    clock = pygame.time.Clock()
    coords = set(product(range(30), repeat=2))
    walls = Walls(screen)

    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        color = (random.randint(1,255), random.randint(1,255), random.randint(1,255))
        snakes.append(Snake(screen, 14, 14, color))
        g.fitness = 0
        ge.append(g)

    while True:
        clock.tick(20)
        check_events()

        for i, snake in enumerate(snakes):
            snake.spawn_food(coords)
            snake.update()
            snake.life -= 1

            headx, heady = snake.head.x, snake.head.y
            foodx, foody = snake.food_position()
            distancex = headx - foodx
            distancey = heady - foody
            direction = snake.direction
            output = nets[i].activate((headx, heady, distancex, distancey, len(snake), direction))
            # 

            if output[0] > 0.5:
                snake.move_left()
            if output[1] > 0.5:
                snake.move_right()


            if food_eaten(snake):
                snake.grow()
                ge[i].fitness += 5
                snake.life += 100

            if snake.self_collision() or walls.collision(snake) or snake.life <= 0:
                snakes.pop(i)
                ge.pop(i)
                nets.pop(i)

        if not snakes:
            break

        update_screen(screen, snakes, walls)


def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
        neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(fitness, 100)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)