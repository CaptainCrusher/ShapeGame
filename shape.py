import pygame, collisions, math, sys
from pygame.locals import *

friction = 1
airResistance = 0.02
gravity = 0.2
stiffness = 0.1
radius = 60
numberOfPoints = 4
torque = 0.01
bounciness = 1.2
permeability = 1.2





WINDOWWIDTH = 1200
WINDOWHEIGHT = 800
TEXTCOLOR = (0, 0, 0)
BACKGROUNDCOLOR = (200, 200, 200)
MOUSEUP = 6
MOUSEDOWN = 5
mousePressed = False
mouseX = 0
mouseY = 0
FPS = 60
pygame.init()
mainClock = pygame.time.Clock()
windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
pygame.display.set_caption('Physics Game')

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

def pointLineDist(point, line):
    a = math.dist(point, (line[0], line[1]))
    b = math.dist(point, (line[2], line[3]))
    c = math.dist((line[0],line[1]),(line[2],line[3]))
    if a**2 > b**2+c**2:
        return b
    elif b**2 > a**2+c**2:
        return a
    else:
        return math.sqrt(a**2-((c**2+a**2-b**2)/(c*2))**2)

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
            elif event[i].type == MOUSEUP:
                mousePressed = False
            elif event[i].type == MOUSEMOTION:
                mouseX = event[i].pos[0]
                mouseY = event[i].pos[1]
            elif event[i].type == QUIT:
                pygame.quit()
                sys.exit()

class Point:

    def __init__(this, x, y, tpe):
        this.x = x
        this.y = y
        this.mass = 1
        this.type = tpe
        this.v = [0, 0]
        this.force = [0, 0]
        this.friction = [0, 0]
        this.connections = []
        this.px = x
        this.py = y

    def update(this, friction):
        this.v[0] += this.force[0]/this.mass
        this.v[1] += this.force[1]/this.mass
        this.v[0] /= 1+airResistance+abs(this.friction[0]*friction)
        this.v[1] /= 1+airResistance+abs(this.friction[1]*friction)
        this.vMag = math.dist((0,0), this.v)
        this.force = [0, 0]
        this.friction = [0, 0]
        this.px = this.x
        this.py = this.y
        this.x += this.v[0]
        this.y += this.v[1]

class Shape:

    def __init__(this, points):
        this.points = points
        this.lengths = []
        for i in range(len(points)):
            for j in range(len(points)):
                if i == j:
                    continue
                else:
                    this.points[i].connections.append([j, math.dist((points[i].x,points[i].y),(points[j].x,points[j].y))])
        x = 0
        y = 0
        for i in this.points:
            x += i.x
            y += i.y
        x /= len(this.points)
        y /= len(this.points)
        this.center = [x, y]

    def gravity(this, gravity):
        for i in range(len(this.points)):
            this.points[i].force[1] += this.points[i].mass*gravity

    def update(this, friction):
        this.turn(keys, torque)
        this.holdTogether(stiffness)
        for i in range(len(this.points)):
            this.points[i].update(friction)
        this.updateCenter()

    def turn(this, keys, mag):
        if keys[K_LEFT]:
            m = -mag
        elif keys[K_RIGHT]:
            m = mag
        else:
            m = 0
        for i in range(len(this.points)):
            this.points[i].force[0] += m*(this.center[1]-this.points[i].y)
            this.points[i].force[1] -= m*(this.center[0]-this.points[i].x)

    def holdTogether(this, mag):
        for i in range(len(this.points)):
            thisPoint = this.points[i]
            for j in range(len(thisPoint.connections)):
                otherPoint = this.points[this.points[i].connections[j][0]]
                target = thisPoint.connections[j][1]
                distance = math.dist((otherPoint.x, otherPoint.y), (thisPoint.x, thisPoint.y))-target
                this.points[i].force[0] -= (thisPoint.x-otherPoint.x)*distance*mag/target
                this.points[i].force[1] -= (thisPoint.y-otherPoint.y)*distance*mag/target
                
    
    def updateCenter(this):
        x = 0
        y = 0
        for i in this.points:
            x += i.x
            y += i.y
        x /= len(this.points)
        y /= len(this.points)
        this.center = [x, y]

    def collide(this, blocks, mag, position):
        for i in range(len(this.points)):
            point = this.points[i]
            for block in blocks:
                if point.x > block.minX and point.x < block.maxX and point.y > block.minY and point.y < block.maxY:
                    if collisions.pointToPoly((point.x, point.y), block.points):
                        best = 10000000
                        index = 0
                        for j in range(len(block.points)):
                            if j == len(block.points)-1:
                                line = [block.points[j][0], block.points[j][1], block.points[0][0], block.points[0][1]]
                            else:
                                line = [block.points[j][0], block.points[j][1], block.points[j+1][0], block.points[j+1][1]]
                            distance = pointLineDist((point.x,point.y), line)
                            if distance < best:
                                col = False
                                for connection in point.connections:
                                    con = this.points[connection[0]]
                                    if collisions.line2line(line, (con.px,con.py,point.px,point.py)) or collisions.line2line(line, (con.x,con.y,point.x,point.y)):
                                        col = True
                                        break
                                if col:
                                    best = distance
                                    index = j
                        if index == len(block.points)-1:
                            line = [block.points[index][0], block.points[index][1], block.points[0][0], block.points[0][1]]
                        else:
                            line = [block.points[index][0], block.points[index][1], block.points[index+1][0], block.points[index+1][1]]
                        momentumAngle = math.atan2(point.v[1]+point.force[1], point.v[0]+point.force[0])
                        slopeAngle = math.atan2(line[3]-line[1], line[2]-line[0])
                        while momentumAngle-slopeAngle > math.pi:
                            momentumAngle -= 2*math.pi
                        while momentumAngle-slopeAngle < -math.pi:
                            momentumAngle += 2*math.pi
                        magnitude = math.sin(momentumAngle-slopeAngle)*math.dist((0,0),(point.v[0]+point.force[0], point.v[1]+point.force[1]))
                        this.points[i].force[0] += magnitude*mag*(line[3]-line[1])/math.dist((line[0],line[1]),(line[2],line[3]))
                        this.points[i].force[1] -= magnitude*mag*(line[2]-line[0])/math.dist((line[0],line[1]),(line[2],line[3]))
                        this.points[i].x += best*position*(line[3]-line[1])/math.dist((line[0],line[1]),(line[2],line[3]))
                        this.points[i].y -= best*position*(line[2]-line[0])/math.dist((line[0],line[1]),(line[2],line[3]))
                        this.points[i].friction[0] = magnitude*(line[2]-line[0])/math.dist((line[0],line[1]),(line[2],line[3]))
                        this.points[i].friction[1] = magnitude*(line[3]-line[1])/math.dist((line[0],line[1]),(line[2],line[3]))
                        #this.points[i].force[0] -= best*friction*(line[2]-line[0])/math.dist((line[0],line[1]),(line[2],line[3]))
                        #this.points[i].force[1] -= best*friction*(line[3]-line[1])/math.dist((line[0],line[1]),(line[2],line[3]))

    def collideEnd(this, end):
        for point in this.points:
            for connect in point.connections:
                point2 = this.points[connect[0]]
                line1 = [point.x, point.y, point2.x, point2.y]
                for i in range(4):
                    if i == 0:
                        line2 = [end[0], end[1], end[0]+20, end[1]]
                    elif i == 1:
                        line2 = [end[0]+20, end[1]+20, end[0]+20, end[1]]
                    elif i == 2:
                        line2 = [end[0]+20, end[1]+20, end[0], end[1]+20]
                    else:
                        line2 = [end[0], end[1], end[0]+20, end[1]]
                if collisions.line2line(line1, line2):
                    keys[ENTER] = True
                    return 1
        return 0

    def draw(this, surface):
        for i in range(len(this.points)):
            for j in range(len(this.points)):
                if i == j:
                    continue
                pygame.draw.line(surface, (0,0,0), (this.points[i].x-this.center[0]+WINDOWWIDTH/2, this.points[i].y-this.center[1]+WINDOWHEIGHT/2), (this.points[j].x-this.center[0]+WINDOWWIDTH/2, this.points[j].y-this.center[1]+WINDOWHEIGHT/2))
                pygame.draw.ellipse(surface, (0,0,0), (this.points[i].x-this.center[0]+WINDOWWIDTH/2-this.points[i].mass*10/2, this.points[i].y-this.center[1]+WINDOWHEIGHT/2-this.points[i].mass*10/2, this.points[i].mass*10, this.points[i].mass*10))


def setPlayer(lvl):
    global shapes
    playerPoints = []
    for p in shapes[lvl]:
        playerPoints.append(Point(p[0],p[1],p[2]))
    return Shape(playerPoints)


def roundTo(num, nearest):
    return round(num/nearest)*nearest

class Block:

    def __init__(this, points):
        this.points = points
        this.minX = 10000000
        this.minY = 10000000
        this.maxX = -1000000
        this.maxY = -1000000
        for point in points:
            if point[0] < this.minX:
                this.minX = point[0]
            if point[0] > this.maxX:
                this.maxX = point[0]
            if point[1] < this.minY:
                this.minY = point[1]
            if point[1] > this.maxY:
                this.maxY = point[1]

    def edit(this, mouseX, mouseY, mousePressed):
        for i in range(len(this.points)):
            if mousePressed and math.dist((mouseX+cam[0], mouseY+cam[1]), (this.points[i][0], this.points[i][1])) < 20:
                this.points[i][0] = roundTo(mouseX+cam[0], 10)
                this.points[i][1] = roundTo(mouseY+cam[1], 10)
                return True
        return False
        

blocks = [
[
Block([[0, 200], [150, 280], [630, 230], [650, 350], [50, 500]]),
Block([[150, 100], [250, 100], [250, 120], [150, 120]]),
Block([[30, -30], [250, -30], [250, -10], [0, -10], [0, -300], [30, -300]]),
Block([[300, -30], [770, -30], [770, -300], [800, -300], [800, -10], [650, -10], [650, 190], [600, 190], [600, -10], [300, -10]]),
Block([[650, -100], [650, -300], [680, -300], [680, -100]]),
Block([[770, 400], [1000, 180], [1070, 170], [830, 400]]),
Block([[670, 200], [850, 130], [850, 150], [730, 200]]),
],
[
Block([[-170, 270], [200, 100], [200, 130], [-160, 290]]),
Block([[20, 170], [-20, 180], [-110, -90], [130, -190], [140, -170], [-80, -70], [-30, 50]]),
Block([[-20, 100], [-20, 140], [-120, 140], [-120, 100]]),
Block([[-80, -20], [-60, 10], [-130, 20], [-130, -10]]),
Block([[-210, 220], [-140, 280], [-160, 290], [-210, 250]]),
],
]

shapes = [
[
    [950, 170, "normal"],
    [1010, 230, "normal"],
    [950, 290, "normal"],
    [890, 230, "normal"],
],
[
    [0, -60, "normal"],
    [60, 0, "normal"],
    [0, 60, "normal"],
    [-60, 0, "normal"],
],
]

ends = [
    [750, -100],
    [1000, 1000],
]

lvl = 1

player = setPlayer(lvl)

while True:
    if keys[K_p]:
        keys[K_p] = False
        print("[")
        for i in range(len(blocks[lvl])):
            print("Block("+str(blocks[lvl][i].points)+"),")
        print("],")
    if keys[ENTER]:
        player = setPlayer(lvl)
    if keys[ENTER]:
        if keys[K_UP]:
            cam[1] -= 5
        elif keys[K_DOWN]:
            cam[1] += 5
        if keys[K_LEFT]:
            cam[0] -= 5
        elif keys[K_RIGHT]:
            cam[0] += 5
    else:
        cam = [player.center[0]-WINDOWWIDTH/2, player.center[1]-WINDOWHEIGHT/2]
    if keys[SPACE]:
        keys[SPACE] = False
        blocks[lvl].append(Block([]))
    elif keys[K_a]:
        keys[K_a] = False
        blocks[lvl][len(blocks[lvl])-1].points.append(mouseX, mouseY)
    windowSurface.fill(BACKGROUNDCOLOR)
    keyListener()
    edited = False
    for i in range(len(blocks[lvl])):
        if blocks[lvl][i].edit(mouseX, mouseY, mousePressed):
            keys[ENTER] = True
            edited = True
    if mousePressed and not edited:
        blocks[lvl][len(blocks[lvl])-1].points.append([roundTo(mouseX+cam[0], 10), roundTo(mouseY+cam[1], 10)])
        keys[ENTER] = True
        mousePressed = False
    camBlocks = []
    for block in blocks[lvl]:
        camBlocks.append([])
        for point in block.points:
            camBlocks[len(camBlocks)-1].append([point[0]-cam[0], point[1]-cam[1]])
    for block in camBlocks:
        if len(block) > 2:
            pygame.draw.polygon(windowSurface, (100,100,100), block)
        elif len(block) > 1:
            pygame.draw.line(windowSurface, (100,100,100), block[0], block[1])
        elif len(block) > 0:
            pygame.draw.ellipse(windowSurface, (100,100,100), (block[0][0]-1,block[0][0]-1,2,2))
    pygame.draw.rect(windowSurface, (0, 255, 255), (ends[lvl][0]-cam[0], ends[lvl][1]-cam[1], 20, 20))
    player.gravity(gravity)
    player.collide(blocks[lvl], bounciness, permeability)
    player.update(friction)
    player.draw(windowSurface)
    lvl += player.collideEnd(ends[lvl])
    pygame.display.update()
    mainClock.tick(FPS)
