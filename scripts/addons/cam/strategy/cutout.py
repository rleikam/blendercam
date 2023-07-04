import bpy
from bpy.props import *
import time
import math
from math import *
from bpy_extras import object_utils
from cam.chunk import *
from cam.collision import *
from cam import simple
from cam.simple import *
from cam.pattern import *
from cam import utils, bridges, ops
from cam.utils import *
from cam import polygon_utils_cam
from cam.polygon_utils_cam import *
from cam.image_utils import *
from enum import Enum
from typing import Iterator

from cam.strategy.utility import *

from concurrent.futures import ThreadPoolExecutor

from shapely.geometry import polygon as spolygon
from shapely import geometry as sgeometry
from shapely import affinity

SHAPELY = True

def cutout(operation):
    max_depth = checkminz(operation)
    cutter_angle = math.radians(operation.cutter_tip_angle / 2)
    c_offset = operation.cutter_diameter / 2  # cutter ofset
    print("cuttertype:", operation.cutter_type, "max_depth:", max_depth)
    if operation.cutter_type == 'VCARVE':
        c_offset = -max_depth * math.tan(cutter_angle)
    elif operation.cutter_type == 'CYLCONE':
        c_offset = -max_depth * math.tan(cutter_angle) + operation.cylcone_diameter / 2
    elif operation.cutter_type == 'BALLCONE':
        c_offset = -max_depth * math.tan(cutter_angle) + operation.ball_radius
    elif operation.cutter_type == 'BALLNOSE':
        r = operation.cutter_diameter / 2
        print("cutter radius:", r)
        if -max_depth < r:
            c_offset = math.sqrt(r ** 2 - (r + max_depth) ** 2)
            print("offset:", c_offset)
    if c_offset > operation.cutter_diameter / 2:
        c_offset = operation.cutter_diameter / 2
    if operation.straight:
        join = 2
    else:
        join = 1
    print('operation: cutout')
    offset = True
    if operation.cut_type == 'ONLINE' and operation.onlycurves:  # is separate to allow open curves :)
        print('separate')
        chunksFromCurve = []
        for ob in operation.objects:
            chunksFromCurve.extend(curveToChunks(ob, operation.use_modifiers))
        for ch in chunksFromCurve:
            # print(ch.points)

            if len(ch.points) > 2:
                ch.poly = chunkToShapely(ch)

    # p.addContour(ch.poly)
    else:
        chunksFromCurve = []
        if operation.cut_type == 'ONLINE':
            p = utils.getObjectOutline(0, operation, True)

        else:
            offset = True
            if operation.cut_type == 'INSIDE':
                offset = False

            p = utils.getObjectOutline(c_offset, operation, offset)
            if operation.outlines_count > 1:
                for i in range(1, operation.outlines_count):
                    chunksFromCurve.extend(shapelyToChunks(p, -1))
                    p = p.buffer(distance=operation.dist_between_paths * offset, resolution=operation.optimisation.circle_detail, join_style=join,
                                 mitre_limit=2)

        chunksFromCurve.extend(shapelyToChunks(p, -1))
        if operation.outlines_count > 1 and operation.movement_insideout == 'OUTSIDEIN':
            chunksFromCurve.reverse()

    # parentChildPoly(chunksFromCurve,chunksFromCurve,o)
    chunksFromCurve = limitChunks(chunksFromCurve, operation)
    if not operation.dont_merge:
        parentChildPoly(chunksFromCurve, chunksFromCurve, operation)
    if operation.outlines_count == 1:
        chunksFromCurve = utils.sortChunks(chunksFromCurve, operation)

    if (operation.movement_type == 'CLIMB' and operation.spindle_rotation_direction == 'CCW') or (
            operation.movement_type == 'CONVENTIONAL' and operation.spindle_rotation_direction == 'CW'):
        for ch in chunksFromCurve:
            ch.points.reverse()

    if operation.cut_type == 'INSIDE':  # there would bee too many conditions above,
        # so for now it gets reversed once again when inside cutting.
        for ch in chunksFromCurve:
            ch.points.reverse()

    layers = getLayers(operation, operation.maxz, checkminz(operation))
    extendorder = []

    if operation.first_down:  # each shape gets either cut all the way to bottom,
        # or every shape gets cut 1 layer, then all again. has to create copies,
        # because same chunks are worked with on more layers usually
        for chunk in chunksFromCurve:
            dir_switch = False  # needed to avoid unnecessary lifting of cutter with open chunks
            # and movement set to "MEANDER"
            for layer in layers:
                chunk_copy = chunk.copy()
                if dir_switch:
                    chunk_copy.points.reverse()
                extendorder.append([chunk_copy, layer])
                if (not chunk.closed) and operation.movement_type == "MEANDER":
                    dir_switch = not dir_switch
    else:
        for layer in layers:
            for chunk in chunksFromCurve:
                extendorder.append([chunk.copy(), layer])

    for chl in extendorder:  # Set Z for all chunks
        chunk = chl[0]
        layer = chl[1]
        print(layer[1])
        chunk.setZ(layer[1])

    chunks = []

    if operation.use_bridges:  # add bridges to chunks
        print('using bridges')
        simple.remove_multiple(operation.name+'_cut_bridges')
        print("old briddge cut removed")

        bridgeheight = min(operation.max.z, operation.min.z + abs(operation.bridges_height))

        for chl in extendorder:
            chunk = chl[0]
            layer = chl[1]
            if layer[1] < bridgeheight:
                bridges.useBridges(chunk, operation)

    if operation.profile_start > 0:
        print("cutout change profile start")
        for chl in extendorder:
            chunk = chl[0]
            if chunk.closed:
                chunk.changePathStart(operation)

    # Lead in
    if operation.lead_in > 0.0 or operation.lead_out > 0:
        print("cutout leadin")
        for chl in extendorder:
            chunk = chl[0]
            if chunk.closed:
                chunk.breakPathForLeadinLeadout(operation)
                chunk.leadContour(operation)

    if operation.ramp:  # add ramps or simply add chunks
        for chl in extendorder:
            chunk = chl[0]
            layer = chl[1]
            if chunk.closed:
                chunk.rampContour(layer[0], layer[1], operation)
                chunks.append(chunk)
            else:
                chunk.rampZigZag(layer[0], layer[1], operation)
                chunks.append(chunk)
    else:
        for chl in extendorder:
            chunks.append(chl[0])

    chunksToMesh(chunks, operation)
