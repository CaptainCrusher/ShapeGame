
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
            if line2line([point[0], point[1], point[0]+100000, point[1]], [poly[i][0], poly[i][1], poly[0][0], poly[0][1]]):
                colNum += 1
        else:
            if line2line([point[0], point[1], point[0]+100000, point[1]], [poly[i][0], poly[i][1], poly[i+1][0], poly[i+1][1]]):
                colNum += 1
    return colNum % 2 == 1
    

