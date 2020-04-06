import pygame
import neat
import os
import random
pygame.font.init()

# GAME RES
WIDTH = 500
HEIGHT = 800


# GAME IMG
BIRD_IMG = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
GROUND_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
FONT = pygame.font.SysFont("Arial", 40)


# THE BIRD
class Bird:
    IMGS = BIRD_IMG
    # MAXIMUM ROTATION FOR PNG
    ROTATION = 20
    # ROTATION VELOCITY
    R_VEL = 20
    # FRAME
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1

        # DISPLACEMENT
        # When tick count = 1, d = 1*-10.5 + 1.5*1**2 = -10.5 + 1.5 = -9 = 9 px up from Origin
        # When tick count = 2, d = 2*-10.5 + 1.5*2**2 = -21 + 6 = -15 = 15 pix up from Origin
        d = self.tick_count * self.vel + 1.5*self.tick_count**2

        if d >= 16:
            d = 16

        if d < 0:
            d -= 2

        self.y += d

        # CHG THE DIRECTION OF THE BIRD

        # tilt 20 degree upwards
        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.ROTATION:
                self.tilt = self.ROTATION

        # slowly tilt till 90 degree downwards
        else:
            if self.tilt > -90:
                self.tilt -= self.R_VEL

    def draw(self, win):
        self.img_count += 1

        # DRAW BIRD + ANIMATION

        # MOVING UPWARDS
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        # MOVING DOWNWARDS
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            # from img 2 to 3 so that it does not skip
            self.img_count = self.ANIMATION_TIME * 2

        # ROTATE IMG AT CENTER
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    # same as mask in PS
    def get_mask(self):
        return pygame.mask.from_surface(self.img)


# THE PIPE
class Pipe:
    GAP = 160
    VEL = 7

    def __init__(self, x):
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BTM = PIPE_IMG

        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BTM, (self.x, self.bottom))

    # MASK COLLISION -> READ IT ON PYGAME.MASK IF U WANT TO
    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        btm_mask = pygame.mask.from_surface(self.PIPE_BTM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        btm_offset = (self.x - bird.x, self.bottom - round(bird.y))

        # COLLISION OCCURS
        b_point = bird_mask.overlap(btm_mask, btm_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        # COLLIDED
        if t_point or b_point:
            return True

        return False


# THE GROUND
class Ground:
    VEL = 7
    G_WIDTH = GROUND_IMG.get_width()
    IMG = GROUND_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.G_WIDTH

    def move(self):
        # 2 IMGS placed side by side
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        # When first img is out from screen, place it bhind the 2nd one
        if self.x1 + self.G_WIDTH < 0:
            self.x1 = self.x2 + self.G_WIDTH

        if self.x2 + self.G_WIDTH < 0:
            self.x2 = self.x1 + self.G_WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


# DRAW THE GAME
def draw_window(win, birds  , pipes, ground, score):
    # DRAW BACKGROUND
    win.blit(BG_IMG, (0, 0))

    # DRAW PIPE
    for pipe in pipes:
        pipe.draw(win)

    # FONT
    text = FONT.render("Score : " + str(score), 1, (255, 255, 255))
    win.blit(text, (WIDTH - 10 - text.get_width(), 10))

    # DRAW GROUND
    ground.draw(win)

    # DRAW BIRD
    for bird in birds:
        bird.draw(win)
    pygame.display.update()


# GAME
def main(genomes, config):
    nets = []
    ge = []
    birds = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(240, 360))
        g.fitness = 0
        ge.append(g)

    ground = Ground(720)
    pipes = [Pipe(590)]
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    rate = pygame.time.Clock()
    score = 0

    run = True
    while run:
        rate.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        pipe_index = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_index = 1
        else:
            run = False
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 1

            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_index].height), abs(bird.y - pipes[pipe_index].bottom)))

            if output[0] > 0.5:
                bird.jump()

        add_pipe = False
        remove = []
        for pipe in pipes:
            for x, bird in enumerate(birds):

                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                remove.append(pipe)

            pipe.move()

        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(590))

        for rem in remove:
            pipes.remove(rem)

        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        ground.move()
        draw_window(win, birds, pipes, ground, score)


def run(path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, path)

    population = neat.Population(config)

    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    sucessor = population.run(main, 50)


if __name__ == "__main__":
    directory = os.path.dirname(__file__)
    path = os.path.join(directory, "Neat.txt")
    run(path)


