from bpy.props import *
import math
from math import *
from bpy_extras import object_utils
from cam.chunk import *
from cam.collision import *
from cam import simple
from cam.simple import *
from cam.pattern import *
from cam import utils
from cam.utils import *
from cam import polygon_utils_cam
from cam.polygon_utils_cam import *
from cam.image_utils import *

from cam.strategy.utility import *

from ..blender.property.OperationProperties import *

from shapely import geometry as sgeometry
from shapely import affinity

def pocket(operation: OperationProperties):
    printProgressionTitle("OPERATION: POCKET")

    simple.remove_multiple("3D_poc")
    
    maxDepth = checkminz(operation)
    cutterAngle = math.radians(operation.cutter_tip_angle / 2)
    cutterOffset = operation.cutter_diameter / 2

    match operation.cutter_type:
        case "VCARVE":
            cutterOffset = -maxDepth * math.tan(cutterAngle)
        case "CYLCONE":
            cutterOffset = -maxDepth * math.tan(cutterAngle) + operation.cylcone_diameter / 2
        case "BALLCONE":
            cutterOffset = -maxDepth * math.tan(cutterAngle) + operation.ball_radius

    if cutterOffset > operation.cutter_diameter / 2:
        cutterOffset = operation.cutter_diameter / 2
    
    outlineOffset = 0 if operation.ignoreRadiusCompensation else cutterOffset

    polygon = utils.getObjectOutline(outlineOffset, operation, False)
    approxn = (min(operation.max.x - operation.min.x, operation.max.y - operation.min.y) / operation.dist_between_paths) / 2
    print(f"Approximative: {approxn}")

    i = 0
    chunks = []
    chunksFromCurve = []
    lastchunks = []

    while not polygon.is_empty:
        if operation.pocketToCurve:
            polygon_utils_cam.shapelyToCurve('3dpocket', polygon, 0.0)  # make a curve starting with _3dpocket

        nchunks = shapelyToChunks(polygon, operation.min.z)
        newOutline = polygon.buffer(-operation.dist_between_paths, operation.optimisation.circle_detail)
        if newOutline.is_empty:

            pt = polygon.buffer(-cutterOffset, operation.optimisation.circle_detail)     # test if the last curve will leave material
            if not pt.is_empty:
                newOutline = pt

        nchunks = limitChunks(nchunks, operation)
        chunksFromCurve.extend(nchunks)
        parentChildDist(lastchunks, nchunks, operation)
        lastchunks = nchunks

        percent = int(i / approxn * 100)
        progress('outlining polygons ', percent)
        polygon = newOutline

        i += 1

    # if (o.poc)#TODO inside outside!
    if (operation.movement_type == 'CLIMB' and operation.spindle_rotation_direction == 'CW') or (
            operation.movement_type == 'CONVENTIONAL' and operation.spindle_rotation_direction == 'CCW'):
        for ch in chunksFromCurve:
            ch.points.reverse()

    chunksFromCurve = utils.sortChunks(chunksFromCurve, operation)

    chunks = []
    layers = getLayers(operation, operation.maxz, checkminz(operation))

    for l in layers:
        lchunks = setChunksZ(chunksFromCurve, l[1])
        if operation.ramp:
            for ch in lchunks:
                ch.zstart = l[0]
                ch.zend = l[1]

        # helix_enter first try here TODO: check if helix radius is not out of operation area.
        if operation.helix_enter:
            helix_radius = cutterOffset * operation.helix_diameter * 0.01  # 90 percent of cutter radius
            helix_circumference = helix_radius * pi * 2

            revheight = helix_circumference * tan(operation.ramp_in_angle)
            for chi, ch in enumerate(lchunks):
                if not chunksFromCurve[chi].children:
                    polygon = ch.points[0]  # TODO:intercept closest next point when it should stay low
                    # first thing to do is to check if helix enter can really enter.
                    checkc = Circle(helix_radius + cutterOffset, operation.optimisation.circle_detail)
                    checkc = affinity.translate(checkc, polygon[0], polygon[1])
                    covers = False
                    for poly in operation.silhouete:
                        if poly.contains(checkc):
                            covers = True
                            break

                    if covers:
                        revolutions = (l[0] - polygon[2]) / revheight
                        # print(revolutions)
                        h = Helix(helix_radius, operation.optimisation.circle_detail, l[0], polygon, revolutions)
                        # invert helix if not the typical direction
                        if (operation.movement_type == 'CONVENTIONAL' and operation.spindle_rotation_direction == 'CW') or (
                                operation.movement_type == 'CLIMB' and operation.spindle_rotation_direction == 'CCW'):
                            nhelix = []
                            for v in h:
                                nhelix.append((2 * polygon[0] - v[0], v[1], v[2]))
                            h = nhelix
                        ch.points = h + ch.points
                    else:
                        operation.info.warnings += 'Helix entry did not fit! \n '
                        ch.closed = True
                        ch.rampZigZag(l[0], l[1], operation)
        # Arc retract here first try:
        if operation.retract_tangential:  # TODO: check for entry and exit point before actual computing... will be much better.
            # TODO: fix this for CW and CCW!
            for chi, ch in enumerate(lchunks):
                # print(chunksFromCurve[chi])
                # print(chunksFromCurve[chi].parents)
                if chunksFromCurve[chi].parents == [] or len(chunksFromCurve[chi].parents) == 1:

                    revolutions = 0.25
                    v1 = Vector(ch.points[-1])
                    i = -2
                    v2 = Vector(ch.points[i])
                    v = v1 - v2
                    while v.length == 0:
                        i = i - 1
                        v2 = Vector(ch.points[i])
                        v = v1 - v2

                    v.normalize()
                    rotangle = Vector((v.x, v.y)).angle_signed(Vector((1, 0)))
                    e = Euler((0, 0, pi / 2.0))  # TODO:#CW CLIMB!
                    v.rotate(e)
                    polygon = v1 + v * operation.retract_radius
                    center = polygon
                    polygon = (polygon.x, polygon.y, polygon.z)

                    # progress(str((v1,v,p)))
                    h = Helix(operation.retract_radius, operation.optimisation.circle_detail, polygon[2] + operation.retract_height, polygon, revolutions)

                    e = Euler((0, 0, rotangle + pi))  # angle to rotate whole retract move
                    rothelix = []
                    c = []  # polygon for outlining and checking collisions.
                    for polygon in h:  # rotate helix to go from tangent of vector
                        v1 = Vector(polygon)

                        v = v1 - center
                        v.x = -v.x  # flip it here first...
                        v.rotate(e)
                        polygon = center + v
                        rothelix.append(polygon)
                        c.append((polygon[0], polygon[1]))

                    c = sgeometry.Polygon(c)
                    # print('çoutline')
                    # print(c)
                    coutline = c.buffer(cutterOffset, operation.optimisation.circle_detail)
                    # print(h)
                    # print('çoutline')
                    # print(coutline)
                    # polyToMesh(coutline,0)
                    rothelix.reverse()

                    covers = False
                    for poly in operation.silhouete:
                        if poly.contains(coutline):
                            covers = True
                            break

                    if covers:
                        ch.points.extend(rothelix)

        chunks.extend(lchunks)

    if operation.ramp:
        for ch in chunks:
            ch.rampZigZag(ch.zstart, ch.points[0][2], operation)

    if operation.first_down:
        chunks = utils.sortChunks(chunks, operation)

    if operation.pocketToCurve:  # make curve instead of a path
        simple.join_multiple("3dpocket")

    else:
        chunksToMesh(chunks, operation)  # make normal pocket path
