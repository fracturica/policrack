

def lineCircleIntersection(point1, point2, r):
    def sgn(a):
        if a == 0:
            return 1
        else:
            return abs(a)/float(a)
    x1, y1, z1 = point1
    x2, y2, z2 = point2
    dx = x2 - x1
    dy = y2 - y1
    dr = (dx**2 + dy**2)**0.5
    D = x1*y2 - x2*y1
    x_1 = (D*dy + sgn(dy)*dx*(r**2*dr**2 - D**2)**0.5) / float(dr**2)
    x_2 = (D*dy - sgn(dy)*dx*(r**2*dr**2 - D**2)**0.5) / float(dr**2)
    y_1 = (-D*dx + abs(dy)*(r**2*dr**2 - D**2)**0.5) / float(dr**2)
    y_2 = (-D*dx - abs(dy)*(r**2*dr**2 - D**2)**0.5) / float(dr**2)
    return x_1, x_2, y_1, y_2


def transformPointToCircle(point, a, b):
    ratio = float(b)/a
    x = point[0] * ratio
    return x, point[1], point[2]


def transformPointToEllipse(point, a, b):
    ratio = float(a)/b
    x = point[0] * ratio
    return x, point[1], point[2]


def findIntersectionPointCircleRadialLine(point, r, refPoint, proximity):
    x1, x2, y1, y2 = lineCircleIntersection((0, 0, 0), point, r)
    x0, y0, z0 = refPoint
    if proximity == 'samequadrant':
        if x0 == 0:
            x = 0
        elif x1/x0 > 0:
            x = x1
        else:
            x = x2
        if y0 == 0:
            y = 0
        elif y1/y0 > 0:
            y = y1
        else:
            y = y2
    elif proximity == 'mindistance':
        dist1 = calcDistance2d(refPoint, (x1, y1, z0))
        dist2 = calcDistance2d(refPoint, (x2, y2, z0))
        if dist1 <= dist2:
            x, y = x1, y1
        else:
            x, y = x2, y2
    return x, y, z0


def findEllipseNormal(point, a, b):
    x0, y0, z0 = point
    coeff = float(a**2 * y0)/float(b**2 * x0)
    term = -coeff*x0 + y0
    return coeff, term


def calcDistance2d(point1, point2):
    x1, y1, z1 = point1
    x2, y2, z2 = point2
    d = ((x1 - x2)**2 + (y1 - y2)**2)**0.5
    return d


def findProjectionOfPointOnLine(point, line):
    x0, y0, z0 = point
    coeff1, term1 = line
    if abs(coeff1) > 10e-4:
        coeff2 = -1./coeff1
        term2 = y0 - coeff2*x0
        x = (term2 - term1) / (coeff1 - coeff2)
        y = coeff1*x + term1
    else:
        x = x0
        if abs(term1) > 10e-4:
            y = term1
        else:
            y = 0
    return x, y, z0


def findOffsetPoints(points, offset, a, b):
    offset_points = []
    for p in points:
        offset_points.append(findOffsetForPoint(p, offset, a, b))
    return offset_points


def findOffsetForPoint(point, offset, a, b):
    if abs(point[0]) < 10e-4:
        p = [
                0,
                point[1] + abs(point[1])/point[1] * offset,
                point[2]
                ]
    elif abs(point[1]) < 10e-4:
        p = [
                point[0] + abs(point[0]) / point[0] * offset,
                point[1],
                point[2]]
    else:
        point_circ = transformPointToCircle(point, a, b)
        point_circ_int = findIntersectionPointCircleRadialLine(
            point_circ, b, point_circ, 'samequadrant')
        point_ellipse = transformPointToEllipse(point_circ_int, a, b)

        line = findEllipseNormal(point_ellipse, a, b)
        point_proj = findProjectionOfPointOnLine(point, line)

        refPoint = [point_proj[i]-point_ellipse[i] for i in range(3)]
        p = findIntersectionPointCircleRadialLine(
            refPoint, offset, point_ellipse, 'samequadrant')
        p = [p[i]+point_ellipse[i] for i in range(3)]
    return p
