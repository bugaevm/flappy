from tkinter import *
import time
import random
import math

root = Tk()

Width = 1200
Height = 600
text_size = 9

canv = Canvas(root, width=Width, height=Height + 3 * text_size, bg='white')
canv.pack(fill=BOTH,expand=1)

fps = 1 / 60
bgnd = canv.create_rectangle(0, 0, Width, Height, fill='white', outline='white')

canv.create_rectangle(
    0, Height, Width, Height + 3 * text_size, fill='#DDDDDD', outline='#DDDDDD'
)

class Bird:
    def __init__(self):
        self.size = 20
        self.x = self.size * 4
        self.y = (Height - self.size) // 2
        self.v0 = -7
        self.v = self.v0
        self.g = 0.25
        self.col = '#e528b8'
        self.object = None
bird = None

class Obstacle:
    def __init__(self):
        level = score[1] + 1

        self.size = int(bird.size * 3)
        # self.hole_size = int(max(
        #     bird.size * 10 - 0.3 * score[1], bird.size * 2.5
        # ) + 0.5)
        self.hole_size = int(bird.size * (3 + 8 / (level ** (1 / 5))))
        self.v = -4

        self.w = (
            (min(level, 36) - 1) / 100
        ) ** 4 * (-1) ** random.choice(range(2))

        self.p = random.choice(range(
            -Height, Height
        )) / Height * math.pi

        self.col = '#777777'

        self.x = Width
        # self.hole = random.choice(
        #     range(bird.size, Height - self.hole_size - 2 * bird.size)
        # )

        self.objects = set()

        obstacles.add(self)

obstacle_period = 1.5
obstacles = set()
score = (None, 0)

def new_game():
    global bird, obstacles, game_is_running

    game_is_running = True
    canv.delete(bgnd)

    if bird is not None:
        canv.delete(bird.object)
    bird = Bird()

    for obstacle in obstacles:
        for obj in obstacle.objects:
            canv.delete(obj)

    obstacles = set()

    show_score(new=True)


def move_bird():
    bird.y += bird.v + bird.g / 2
    bird.v += bird.g

    if bird.object is not None:
        canv.delete(bird.object)

    bird.object = canv.create_oval(
        bird.x, bird.y, bird.x + bird.size, bird.y + bird.size, fill=bird.col
    )

    if bird.y + bird.size >= Height:
        bird.y = Height - bird.size
        bird.g = 0
        bird.v = 0

        game_over()

    root.after(int(1000 * fps), move_bird)

def move_obstacles():
    global obstacles

    deleting = set()
    for obst in obstacles:
        obst.x += obst.v
        obst.p += obst.w
        hole = bird.size + (
            Height - obst.hole_size - 2 * bird.size
        ) * (1 + math.sin(obst.p)) / 2

        for obj in obst.objects:
            canv.delete(obj)

        if bird.x + bird.size >= obst.x and bird.x <= obst.x + obst.size:
            if (bird.y <= hole
            or bird.y + bird.size >= hole + obst.hole_size):
                obst.col = '#b30b02'
                game_over()

            if bird.y + bird.size >= hole + obst.hole_size:
                if obst.x <= bird.x + bird.size / 2 <= obst.x + obst.size:
                    # bird.g = 0
                    bird.v = 0
                    bird.y = hole + obst.hole_size - bird.size

                elif bird.x <= obst.x and bird.x + bird.size > obst.x:
                    for obst2 in obstacles:
                        obst2.x += 1

                elif (bird.x <= obst.x + obst.size
                and bird.x + bird.size > obst.x + obst.size):
                    for obst2 in obstacles:
                        obst2.x -= 1

        if obst.x >= -obst.size:
            rect1 = canv.create_rectangle(
                obst.x, 0, obst.x + obst.size, hole,
                fill=obst.col, outline=obst.col
            )

            rect2 = canv.create_rectangle(
                obst.x, hole + obst.hole_size, obst.x + obst.size, Height,
                fill=obst.col, outline=obst.col
            )

            obst.objects = {rect1, rect2}

        else:
            deleting.add(obst)

        if int(bird.x) == int(obst.x + obst.size) and game_is_running:
            show_score(plus=True)
            obst.col = '#1ad747'


    obstacles -= deleting


    root.after(int(1000 * fps), move_obstacles)

def create_new_obstacle():
    if game_is_running:
        Obstacle()

    root.after(int(1000 * obstacle_period), create_new_obstacle)

def click(event):
    global bird

    if game_is_running:
        bird.v = bird.v0
    else:
        new_game()

def show_score(new=False, plus=False):
    global score

    obj, var = score
    var += plus
    if new:
        var = 0
    if obj is not None:
        canv.delete(obj)

    n_obj = canv.create_text(text_size, Height + text_size,
        text=f'SCORE: {var}', anchor=NW, font=f'Cantarel {text_size}'
    )

    score = (n_obj, var)

def game_over():
    global game_is_running, bgnd

    if not game_is_running:
        return 0

    bgnd = canv.create_rectangle(
        0, 0, Width, Height, fill='#FFA0A0', outline='#FFA0A0'
    )

    for obst in obstacles:
        obst.v = 0

    bird.v = max(bird.v, 0)
    bird.col = '#670003'
    game_is_running = False

new_game()
create_new_obstacle()
move_obstacles()
move_bird()
canv.bind('<Button-1>', click)
canv.bind('<Button-3>', click)
root.bind('<space>', click)
root.bind('<Return>', click)
root.bind('<Up>', click)
root.mainloop()
