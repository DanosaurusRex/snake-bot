import sys
import random
from itertools import product
import pygame
from pygame.sprite import Sprite, Group

GRID_SIZE = 30
WIN_WIDTH = 1020
WIN_HEIGHT = 620
BG = 0, 0, 0

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


class Segment(Sprite):
    """Class to manage each segment of the snake."""
    def __init__(self, screen, x, y):
        super().__init__()
        self.screen = screen
        self.rect = pygame.Rect(0, 0, 20, 20)
        self.x = x
        self.y = y
        self.xdir = 0
        self.ydir = 0
        self.color = 0, 255, 0

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
    def __init__(self, screen, x, y, length=3):
        self.screen = screen
        self.xdir = 1
        self.ydir = 0
        self.body = []
        for i in range(length):
            self.body.append(Segment(self.screen, x-i, y))
        self.head = self.body[0]
        self.tail = Group(self.body[1:])
        self.score = 0

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

    def move(self, dir):
        if dir == 'left' and not self.xdir:
            self.xdir = -1
            self.ydir = 0
        if dir == 'right' and not self.xdir:
            self.xdir = 1
            self.ydir = 0
        if dir == 'up' and not self.ydir:
            self.xdir = 0
            self.ydir = -1
        if dir == 'down' and not self.ydir:
            self.xdir = 0
            self.ydir = 1

    def grow(self):
        new = Segment(self.screen, self.body[-1].x, self.body[-1].y)
        self.body.append(new)
        self.tail.add(new)
        self.score += 1

    def draw_snake(self):
        """Draw segments of the snake."""
        for segment in self:
            segment.draw_segment()


class Food(Sprite):
    def __init__(self, screen, x, y):
        super().__init__()
        self.screen = screen
        self.x = x
        self.y = y
        self.color = 255, 0, 0
        self.rect = pygame.Rect(0, 0, 20, 20)
        self.rect.left = 10 + self.x * 20
        self.rect.top = 10 + self.y * 20

    def draw_food(self):
        pygame.draw.rect(self.screen, self.color, self.rect)


def check_events(screen, snake, game_active):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                snake.move('left')
            if event.key == pygame.K_RIGHT:
                snake.move('right')
            if event.key == pygame.K_UP:
                snake.move('up')
            if event.key == pygame.K_DOWN:
                snake.move('down')



def update_screen(screen, snake, foods, walls):
    screen.fill(BG)
    for food in foods:
        food.draw_food()
    walls.draw_walls()
    snake.draw_snake()
    pygame.display.update()


def check_food_eaten(snake, foods):
    """Check snake-food collisions"""
    eaten = pygame.sprite.spritecollide(snake.head, foods, True)
    if eaten:
        snake.grow()


def spawn_food(screen, snake, foods, coords):
    """Spawn food in an empty location if no food exists"""
    if not len(foods):
        snake_pos = set((segment.x, segment.y) for segment in snake)
        food_locs = list(coords - snake_pos)
        x, y = random.choice(food_locs)
        foods.add(Food(screen, x, y))


def main():
    screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pygame.display.set_caption('Snake')
    clock = pygame.time.Clock()
    coords = set(product(range(30), repeat=2))

    walls = Walls(screen)
    snake = Snake(screen, 14, 14)
    foods = Group()

    game_active = True
    while True:
        clock.tick(10)
        check_events(screen, snake, game_active)

        if game_active:
            snake.update()
            check_food_eaten(snake, foods)
            spawn_food(screen, snake, foods, coords)

            # Check tail collisions
            hit_tail = pygame.sprite.spritecollide(snake.head, snake.tail, False)
            if hit_tail:
                game_active = False

            # Check snake is inside field
            in_area = walls.rect.contains(snake.head.rect)
            if not in_area:
                game_active = False
        
        update_screen(screen, snake, foods, walls)



if __name__ == '__main__':
    main()