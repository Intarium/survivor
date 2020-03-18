import contextlib

with contextlib.redirect_stdout(None):
    import pygame
from client import Network


pygame.font.init()

# Constants
PLAYER_RADIUS = 10
START_VEL = 5
WALK_COUNT = 0
animCount = 0
W, H = 1024, 600
gravity = 5
isJump = False
jumpCount = 10

idleright = [pygame.image.load('assets/right1.png')]
idleleft = [pygame.image.load('assets/left1.png')]
right = [pygame.image.load('assets/right1.png'), pygame.image.load('assets/right2.png'), pygame.image.load('assets/right3.png'), pygame.image.load('assets/right4.png'), pygame.image.load('assets/right5.png'), pygame.image.load('assets/right6.png')]
left = [pygame.image.load('assets/left1.png'), pygame.image.load('assets/left2.png'), pygame.image.load('assets/left3.png'), pygame.image.load('assets/left4.png'), pygame.image.load('assets/left5.png'), pygame.image.load('assets/left6.png')]
NAME_FONT = pygame.font.SysFont("comicsans", 20)
TIME_FONT = pygame.font.SysFont("comicsans", 30)
SCORE_FONT = pygame.font.SysFont("comicsans", 26)

COLORS = [(255, 0, 0), (255, 128, 0), (255, 255, 0), (128, 255, 0), (0, 255, 0), (0, 255, 128), (0, 255, 255),
          (0, 128, 255), (0, 0, 255), (0, 0, 255), (128, 0, 255), (255, 0, 255), (255, 0, 128), (128, 128, 128),
          (0, 0, 0)]

players = {}
maps = [[[200, 300, 200, 100], [500, 200, 300, 100]], [[800, 300, 500, 100], [500, 200, 300, 100]]]

def convert_time(t):
    if type(t) == str:
        return t

    if int(t) < 60:
        return str(t) + "s"
    else:
        minutes = str(t // 60)
        seconds = str(t % 60)

        if int(seconds) < 10:
            seconds = "0" + seconds

        return minutes + ":" + seconds


def redraw_window(players, game_time, score, map, WIN):
    global animCount
    anim = [0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,3,3,3,3,3,3,3,3,3,3,4,4,4,4,4,4,4,4,4,4,5,5,5,5,5,5,5,5,5,5]
    WIN.fill((255, 255, 255))
    #for i in map:
    #   pygame.draw.rect(WIN, (255, 0, 0), (i[0], i[1], i[2], i[3]))
    pygame.draw.rect(WIN, (255, 0, 0), (0, 400, 1024, 75), 2)
    for player in sorted(players, key=lambda x: players[x]["score"]):
        p = players[player]
        if p["left"] == 'True' and p["right"] == 'False':
            WIN.blit(left[anim[animCount]], (p["x"], p["y"]))
        elif p["right"] == 'True' and p["left"] == 'False':
            WIN.blit(right[anim[animCount]], (p["x"] , p["y"]))
        else:
            if p["lastkey"] == 'left':
                WIN.blit(idleleft[0], (p["x"], p["y"]))
            elif p["lastkey"] == 'right':
                WIN.blit(idleright[0], (p["x"], p["y"]))
        pygame.draw.rect(WIN, (255, 0, 0), (p["x"], p["y"], p["w"], p["h"]), 2)
        nickrect = pygame.Rect((p["x"] - 35, p["y"] - 30, 100, 14))
        text = NAME_FONT.render(p["name"], 1, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.centerx = nickrect.centerx
        text_rect.centery = nickrect.centery
        WIN.blit(text, text_rect)
        pygame.draw.rect(WIN, (0,0,0), nickrect, -1)

    sort_players = list(reversed(sorted(players, key=lambda x: players[x]["score"])))
    title = TIME_FONT.render("Scoreboard", 1, (0, 0, 0))
    start_y = 25
    x = W - title.get_width() - 10
    WIN.blit(title, (x, 5))

    ran = min(len(players), 3)
    for count, i in enumerate(sort_players[:ran]):
        text = SCORE_FONT.render(str(count + 1) + ". " + str(players[i]["name"]), 1, (0, 0, 0))
        WIN.blit(text, (x, start_y + count * 20))

    # draw time
    text = TIME_FONT.render("Time: " + convert_time(game_time), 1, (0, 0, 0))
    WIN.blit(text, (10, 10))
    # draw score
    text = TIME_FONT.render("Score: " + str(round(score)), 1, (0, 0, 0))
    WIN.blit(text, (10, 15 + text.get_height()))
    animCount += 1
    if animCount >= 59:
        animCount = 0

def main(name):
    WIN = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Survivor")
    global players, WALK_COUNT, isJump, jumpCount
    # start by connecting to the network
    server = Network()
    current_id = server.connect(name)
    players, game_time = server.send("get")

    # setup the clock, limit to 30fps
    clock = pygame.time.Clock()

    run = True
    while run:
        clock.tick(60)
        player = players[current_id]
        vel = START_VEL
        if vel <= 1:
            vel = 1
        keys = pygame.key.get_pressed()
        lastkey = ''
        data = "map "
        map = server.send(data)

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player["x"] = player["x"] - vel
            player["left"] = True
            player["right"] = False

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player["x"] = player["x"] + vel
            player["right"] = True
            player["left"] = False


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    player["right"] = False
                    player["left"] = False
                    lastkey = 'left'
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    player["right"] = False
                    player["left"] = False
                    lastkey = 'right'

        data = "move " + str(player["x"]) + " " + str(player["y"]) + " " + str(player["left"]) + " " + str(player["right"]) + " " + str(lastkey)

        players, game_time = server.send(data)

        redraw_window(players, game_time, player["score"], map, WIN)
        pygame.display.update()

    server.disconnect()
    pygame.quit()
    quit()



