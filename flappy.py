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

hard_score = 45  # with this score the game become much harder
class Obstacle:
    def __init__(self):
        level = score[1] + 1

        self.size = int(bird.size * 3)
        # self.hole_size = int(max(
        #     bird.size * 10 - 0.3 * score[1], bird.size * 2.5
        # ) + 0.5)
        self.hole_size = int(bird.size * (3 + 15 / (level ** (1 / 5))))
        self.v = -4

        self.w = (
            (min(level, 38) - 1) / 100
        ) ** 4 * (-1) ** random.choice(range(2))

        self.p = random.choice(range(
            -Height, Height
        )) / Height * math.pi

        self.col = None
        self.cond = None
        self.score = score[1]
        self.disappearing = (self.score >= hard_score)


        self.x = Width
        # self.hole = random.choice(
        #     range(bird.size, Height - self.hole_size - 2 * bird.size)
        # )

        self.objects = set()

        obstacles.add(self)

obstacle_period = 1.5
obstacles = set()
score = (None, 0)
highscore = (None, None)

def grey(num):
    s = ('0' + hex(num)[2:])[-2:]
    return '#' + s * 3

def new_game():
    global bird, obstacles, game_is_running, highscore

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

    try:
        highscore_file = open('highscore')
    except FileNotFoundError:
        highscore = (None, None)
    else:
        highscore = (highscore[0], int(highscore_file.read()))
        highscore_file.close()

    show_highscore()

testing_mode = False
def enable_testing_mode(event):
    global testing_mode

    canv.create_rectangle(0, 0, Width, Height, fill='#ccffcc', outline='#ccffcc')
    testing_mode = True

def move_bird():
    bird.y += bird.v + bird.g / 2
    bird.v += bird.g

    if bird.object is not None:
        canv.delete(bird.object)

    bird.object = canv.create_oval(
        bird.x, bird.y, bird.x + bird.size, bird.y + bird.size,
        fill=bird.col, outline = bird.col
    )

    if bird.y + bird.size >= Height:
        bird.y = Height - bird.size
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

        obst.col = color(obst)

        for obj in obst.objects:
            canv.delete(obj)

        if bird.x + bird.size >= obst.x and bird.x <= obst.x + obst.size:
            if (bird.y <= hole
            or bird.y + bird.size >= hole + obst.hole_size):
                obst.cond = 'bumped'
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

            elif bird.y < hole and bird.v < 0:
                bird.y = hole
                bird.v *= -1

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
            obst.cond = 'passed'


    obstacles -= deleting


    root.after(int(1000 * fps), move_obstacles)

def color(obst):
    if obst.cond == 'passed':
        return '#1ad747'
    if obst.cond == 'bumped':
        return '#b30b02'

    if game_is_running and obst.x <= Width / 2 and obst.disappearing:
        lp = bird.x + bird.size * 2
        rp = Width / 2 - bird.size * 3
        cp = rp - (rp - lp) / ((obst.score - hard_score + 1) ** (1 / 5))

        a = Width / 2 - obst.x
        b = obst.x - cp

        return grey(min(int((119 * b + 255 * a) / (a + b) + 0.5), 255))

    return grey(119)


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

def show_highscore():
    global highscore

    obj, var = highscore

    if var is None:
        return 0

    canv.delete(obj)

    n_obj = canv.create_text(Width - text_size, Height + text_size,
        text=f'HIGHSCORE: {var}', anchor=NE, font=f'Cantarel {text_size}'
    )

    highscore = (n_obj, var)

def game_over():
    global game_is_running, bgnd

    if testing_mode:
        return 0

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

    if highscore[1] is None or score[1] > highscore[1]:
        highscore_file = open('highscore', 'w')
        highscore_file.write(str(score[1]))
        highscore_file.close()

new_game()
create_new_obstacle()
move_obstacles()
move_bird()

canv.bind('<Button-1>', click)
canv.bind('<Button-3>', click)
root.bind('<space>', click)
root.bind('<Return>', click)
root.bind('<Up>', click)
root.bind('t', enable_testing_mode)

root.mainloop()
