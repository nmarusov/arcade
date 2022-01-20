import os
from random import randint, random, choice
import secrets
import pygame as pg
from pygame.event import clear
from pygame.locals import *

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 30


class MovingObject:
    def __init__(self, x, y, width, height) -> None:
        self.surf = pg.Surface((int(width), int(height)))
        self.rect = Rect(int(x), int(y), int(width), int(height))
        self.vx = 0
        self.vy = 0

    def update(self):
        self.rect.left += self.vx / FPS
        self.rect.top += self.vy / FPS

    def draw(self, screen):
        screen.blit(self.surf, self.rect.topleft)


class Player(MovingObject):
    WIDTH = 150
    HEIGHT = 30
    COLOR = pg.Color(200, 100, 0)

    def __init__(self, x) -> None:
        super().__init__(
            x - self.WIDTH / 2, SCREEN_HEIGHT - self.HEIGHT, self.WIDTH, self.HEIGHT
        )

    def update(self):
        super().update()

        if self.vx > 0:
            self.vx -= 10
        elif self.vx < 0:
            self.vx += 10

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

    def draw(self, screen):
        self.surf.fill(self.COLOR)
        pg.draw.circle(
            self.surf, pg.Color(0, 0, 0), self.surf.get_rect().center, self.HEIGHT / 3
        )
        super().draw(screen)

    def move_left(self):
        if self.rect.left > 0:
            self.vx = -300

    def move_right(self):
        if self.rect.right < SCREEN_WIDTH:
            self.vx = 300


class Brick:
    HEIGHT = 30
    COLOR = pg.Color(150, 150, 0)

    def __init__(
        self, state: bool, x: int, y: int, width: int, secret: int = 0
    ) -> None:
        """[summary]

        Args:
            state (bool): Кирпич присутствует, если True
            x (int): Координата x левого вернего угла кирпича
            y (int): Координата y левого вернего угла кирпича
            width (int): Ширина кирпича
            secret (int, optional): 0 - обычный кирпич, 1 - бонус, 2 - враг. Defaults to 0.
        """
        self.surf = pg.Surface((int(width), int(self.HEIGHT)))
        self.rect = Rect(int(x), int(y), int(width), int(self.HEIGHT))
        self.secret = secret
        self.state = state

    def draw(self, screen):
        if self.state:
            if self.secret == 1:
                self.surf.fill(pg.Color(255, 255, 255))
            elif self.secret == 2:
                self.surf.fill(pg.Color(30, 30, 30))
            else:
                self.surf.fill(self.COLOR)

            pg.draw.rect(
                self.surf,
                pg.Color(0, 0, 0),
                pg.Rect(0, 0, self.rect.width, self.rect.height),
                2,
            )
            screen.blit(self.surf, self.rect.topleft)

    def destroy(self):
        self.state = False


class Wall:
    def __init__(self, map_file) -> None:
        self.bricks = []
        path = os.path.join("maps", map_file)
        secrets = {" ": 0, ".": 0, "+": 1, "-": 2}  # map

        with open(path, "r") as f:
            for r, line in enumerate(f):
                pattern = line.strip("\n")
                n = len(pattern)
                w = SCREEN_WIDTH / n
                row = [
                    Brick(p != " ", i * w, r * Brick.HEIGHT, w, secret=secrets[p])
                    for i, p in enumerate(pattern)
                ]

                self.bricks.extend(row)

    def draw(self, screen):
        for brick in self.bricks:
            brick.draw(screen)


class Bonus(MovingObject):
    HEIGHT = 30
    WIDTH = 30
    COLOR = pg.Color(255, 255, 255)

    def __init__(self, x, y) -> None:
        super().__init__(
            x - self.WIDTH // 2, y - self.HEIGHT // 2, self.WIDTH, self.HEIGHT
        )
        self.vx = 0
        self.vy = 100

    def draw(self, screen):
        self.surf.fill(self.COLOR)
        super().draw(screen)


class Enemy(MovingObject):
    HEIGHT = 30
    WIDTH = 30
    COLOR = pg.Color(30, 30, 30)

    def __init__(self, x, y) -> None:
        super().__init__(
            x - self.WIDTH // 2, y - self.HEIGHT // 2, self.WIDTH, self.HEIGHT
        )
        self.vx = 0
        self.vy = 100

    def draw(self, screen):
        self.surf.fill(self.COLOR)
        super().draw(screen)


class Ball(MovingObject):
    TOLERANCE = 10

    def __init__(self, x, y) -> None:
        image = pg.image.load("ball.png")
        rect = image.get_rect()
        super().__init__(x, y, rect.width, rect.height)
        self.surf = image

        self.vx = 0
        self.vy = 0

    def update(self, p: Player, w: Wall, bonuses: list[Bonus], enemies: list[Enemy]):
        super().update()

        if self.rect.right >= SCREEN_WIDTH and self.vx > 0:
            self.vx = -self.vx
        elif self.rect.left <= 0 and self.vx < 0:
            self.vx = -self.vx
        if self.rect.top <= 0 and self.vy < 0:
            self.vy = -self.vy

        if self.rect.colliderect(p):
            if abs(self.rect.bottom - p.rect.top) < self.TOLERANCE and self.vy > 0:
                self.vy = -self.vy
            elif abs(self.rect.right - p.rect.left) < self.TOLERANCE and self.vx > 0:
                self.vx = -self.vx
            elif abs(self.rect.left - p.rect.right) < self.TOLERANCE and self.vx < 0:
                self.vx = -self.vx

        for brick in w.bricks:
            if not brick.state:
                continue

            if self.rect.colliderect(brick.rect):
                if (
                    abs(self.rect.bottom - brick.rect.top) < self.TOLERANCE
                    and self.vy > 0
                ):
                    self.vy = -self.vy
                elif (
                    abs(self.rect.top - brick.rect.bottom) < self.TOLERANCE
                    and self.vy < 0
                ):
                    self.vy = -self.vy
                elif (
                    abs(self.rect.right - brick.rect.left) < self.TOLERANCE
                    and self.vx > 0
                ):
                    self.vx = -self.vx
                elif (
                    abs(self.rect.left - brick.rect.right) < self.TOLERANCE
                    and self.vx < 0
                ):
                    self.vx = -self.vx

                brick.destroy()
                if brick.secret == 1:
                    bonuses.append(Bonus(brick.rect.centerx, brick.rect.centery))
                elif brick.secret == 2:
                    bonuses.append(Enemy(brick.rect.centerx, brick.rect.centery))

                break

    def move_to(self, x, y):
        """Поместить мяч в заданное место.

        Args:
            x (int): x
            y (int): y
        """
        self.rect.left = x
        self.rect.top = y


class Game:
    BACKGROUND_COLOR = pg.Color(30, 70, 30)

    def __init__(self) -> None:
        pg.init()
        self.clock = pg.time.Clock()
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        self.wall = Wall("01.lvl")
        self.player = Player(SCREEN_WIDTH / 2)
        self.ball = Ball(SCREEN_WIDTH / 2, SCREEN_HEIGHT - Player.HEIGHT)

        self.bonuses = []
        self.enemies = []

        self.started = False

    def update(self):
        if not self.started:
            self.ball.move_to(
                self.player.rect.centerx - self.ball.rect.width / 2,
                SCREEN_HEIGHT - Player.HEIGHT - self.ball.rect.height,
            )

        self.player.update()
        self.ball.update(self.player, self.wall, self.bonuses, self.enemies)

        for bonus in self.bonuses:
            bonus.update()

        for enemy in self.enemies:
            enemy.update()

    def draw(self):
        self.clear()

        self.player.draw(self.screen)
        self.ball.draw(self.screen)
        self.wall.draw(self.screen)

        for bonus in self.bonuses:
            bonus.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        pg.display.flip()

    def clear(self):
        self.screen.fill(self.BACKGROUND_COLOR)

    def tick(self):
        self.clock.tick(FPS)

    def loop(self):
        done = False

        while not done:
            for event in pg.event.get():
                if event.type == QUIT:
                    done = True
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        self.ball.vx = randint(100, 200) * choice([1, -1])
                        self.ball.vy = randint(-150, -100)
                        self.started = True

            keys = pg.key.get_pressed()

            if keys[pg.K_LEFT]:
                self.player.move_left()
            elif keys[pg.K_RIGHT]:
                self.player.move_right()

            self.update()
            self.draw()
            self.tick()


def main():
    game = Game()
    game.loop()


if __name__ == "__main__":
    main()
