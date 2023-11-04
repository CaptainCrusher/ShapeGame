import pygame, math, sys
from pygame.locals import *

WINDOWWIDTH = 1200
WINDOWHEIGHT = 800
TEXTCOLOR = (0, 0, 0)
BACKGROUNDCOLOR = (200, 200, 200)
MOUSEUP = 6
MOUSEDOWN = 5
scene = "game"
mousePressed = False
mouseX = 0
mouseY = 0
FPS = 30
pygame.init()
mainClock = pygame.time.Clock()
windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
pygame.display.set_caption('collision test')

keys = []
for i in range(100000):
 keys.append(False)

SPACE = 32
BACKSPACE = 8
ENTER = 13
PERIOD = 46
COMMA = 44
QUESTION = 47
EXCLAMATION = 49
LSHIFT = 304
RSHIFT = 303
QUOTE = 39
NUMPAD_LEFT = 260
NUMPAD_RIGHT = 262
NUMPAD_UP = 264
frameCount = 0

points = [[100,100],[200,100],[150,50],[150,150]]
points = [[50,50],[100,100],[100,300],[400,300],[400,100],[300,100],[300,200],[200,200],[200,100],[100,100]]
pointHolding = -1


def drawText(text, font, col, surface, x, y, **kwargs):
    angle = kwargs.get("angle", 0)
    textobj = pygame.transform.rotate(font.render(text, 1, col), angle)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)
def drawTextCorner(text, font, col, surface, x, y, **kwargs):
    angle = kwargs.get("angle", 0)
    textobj = pygame.transform.rotate(font.render(text, 1, col), angle)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)
def fontSize(size):
    return pygame.font.SysFont(None, size)

def keyListener():
    global mouseX
    global mouseY
    global keys
    global mousePressed
    global pointHolding
    global points
    event = pygame.event.get()
    if len(event) > 0:
        for i in range(len(event)):
            if event[i].type == KEYDOWN:
                #print(event[i].key)
                keys[event[i].key] = True
            elif event[i].type == KEYUP:
                keys[event[i].key] = False
            elif event[i].type == MOUSEDOWN:
                mousePressed = True
                for i in range(len(points)):
                    if math.dist(points[i], (mouseX, mouseY)) < 10:
                        pointHolding = i
            elif event[i].type == MOUSEUP:
                mousePressed = False
                pointHolding = -1
            elif event[i].type == MOUSEMOTION:
                mouseX = event[i].pos[0]
                mouseY = event[i].pos[1]
                for i in range(len(points)):
                    if i == pointHolding:
                        points[i][0] = mouseX
                        points[i][1] = mouseY
            elif event[i].type == QUIT:
                pygame.quit()
                sys.exit()

def line2line(l1, l2):
    if l1[2] > l1[0]:
        line1 = l1
    else:
        line1 = [l1[2],l1[3],l1[0],l1[1]]
    if l2[2] > l2[0]:
        line2 = l2
    else:
        line2 = [l2[2],l2[3],l2[0],l2[1]]
    if line1[0] == line1[2]:
        if line2[0] == line2[2]:
            return False
        elif line2[0] < line1[0] and line2[2] > line1[0]:
            slope = (line2[3]-line2[1])/(line2[2]-line2[0])
            b = line2[1]-slope*line2[0]
            y = slope*line1[0]+b
            return (y > line1[1] and y < line1[3]) or (y < line1[1] and y > line1[3])
        return False
    if line2[0] == line2[2]:
        if line1[0] == line1[2]:
            return False
        elif line1[0] < line2[0] and line1[2] > line2[0]:
            slope = (line1[3]-line1[1])/(line1[2]-line1[0])
            b = line1[1]-slope*line1[0]
            y = slope*line2[0]+b
            return (y > line2[1] and y < line2[3]) or (y < line2[1] and y > line2[3])
        return False
    m1 = (line1[3]-line1[1])/(line1[2]-line1[0])
    m2 = (line2[3]-line2[1])/(line2[2]-line2[0])
    if m1 == m2:
        return False
    b1 = line1[1]-m1*line1[0]
    b2 = line2[1]-m2*line2[0]
    x = (b2-b1)/(m1-m2)
    return x > line1[0] and x < line1[2] and x > line2[0] and x < line2[2]

def pointToPoly(point, poly):
    colNum = 0
    for i in range(len(poly)):
        if i == len(poly)-1:
            if line2line([point[0], point[1], point[0]+10000, point[1]], [poly[i][0], poly[i][1], poly[0][0], poly[0][1]]):
                colNum += 1
        else:
            if line2line([point[0], point[1], point[0]+10000, point[1]], [poly[i][0], poly[i][1], poly[i+1][0], poly[i+1][1]]):
                colNum += 1
    return colNum % 2 == 1
    
while True:
    windowSurface.fill(BACKGROUNDCOLOR)
    keyListener()
    point = points[0]
    poly = []
    for i in points:
        poly.append(i)
    poly.remove(point)
    #if line2line([points[0][0],points[0][1],points[1][0],points[1][1]], [points[2][0],points[2][1],points[3][0],points[3][1]]):
    if pointToPoly(point, poly):
        clr = (255,0,0)
    else:
        clr = (0,0,0)
    '''pygame.draw.line(windowSurface, clr, points[0], points[1])
    pygame.draw.line(windowSurface, clr, points[2], points[3])'''
    pygame.draw.polygon(windowSurface, (0,0,0), poly)
    pygame.draw.ellipse(windowSurface, clr, (point[0]-6, point[1]-6, 12, 12))
    pygame.display.update()
    mainClock.tick()
