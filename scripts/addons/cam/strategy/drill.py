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

def drill(operation):
    printProgressionTitle("OPERATION: DRILL")

    chunks = []
    for ob in operation.objects:
        activate(ob)

        bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked": False, "mode": 'TRANSLATION'},
                                      TRANSFORM_OT_translate={"value": (0, 0, 0),
                                                              "constraint_axis": (False, False, False),
                                                              "orient_type": 'GLOBAL', "mirror": False,
                                                              "use_proportional_edit": False,
                                                              "proportional_edit_falloff": 'SMOOTH',
                                                              "proportional_size": 1, "snap": False,
                                                              "snap_target": 'CLOSEST', "snap_point": (0, 0, 0),
                                                              "snap_align": False, "snap_normal": (0, 0, 0),
                                                              "texture_space": False, "release_confirm": False})
        # bpy.ops.collection.objects_remove_all()
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        ob = bpy.context.active_object
        if ob.type == 'CURVE':
            ob.data.dimensions = '3D'
        try:
            bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        except:
            pass
        l = ob.location

        if ob.type == 'CURVE':

            for c in ob.data.splines:
                maxx, minx, maxy, miny, maxz, minz = -10000, 10000, -10000, 10000, -10000, 10000
                for p in c.points:
                    if operation.drill_type == 'ALL_POINTS':
                        chunks.append(camPathChunk([(p.co.x + l.x, p.co.y + l.y, p.co.z + l.z)]))
                    minx = min(p.co.x, minx)
                    maxx = max(p.co.x, maxx)
                    miny = min(p.co.y, miny)
                    maxy = max(p.co.y, maxy)
                    minz = min(p.co.z, minz)
                    maxz = max(p.co.z, maxz)
                for p in c.bezier_points:
                    if operation.drill_type == 'ALL_POINTS':
                        chunks.append(camPathChunk([(p.co.x + l.x, p.co.y + l.y, p.co.z + l.z)]))
                    minx = min(p.co.x, minx)
                    maxx = max(p.co.x, maxx)
                    miny = min(p.co.y, miny)
                    maxy = max(p.co.y, maxy)
                    minz = min(p.co.z, minz)
                    maxz = max(p.co.z, maxz)
                cx = (maxx + minx) / 2
                cy = (maxy + miny) / 2
                cz = (maxz + minz) / 2

                center = (cx, cy)
                aspect = (maxx - minx) / (maxy - miny)
                if (1.3 > aspect > 0.7 and operation.drill_type == 'MIDDLE_SYMETRIC') or operation.drill_type == 'MIDDLE_ALL':
                    chunks.append(camPathChunk([(center[0] + l.x, center[1] + l.y, cz + l.z)]))

        elif ob.type == 'MESH':
            for v in ob.data.vertices:
                chunks.append(camPathChunk([(v.co.x + l.x, v.co.y + l.y, v.co.z + l.z)]))
        delob(ob)  # delete temporary object with applied transforms

    layers = getLayers(operation, operation.maxz, checkminz(operation))

    chunklayers = []
    for layer in layers:
        for chunk in chunks:
            # If using object for minz then use z from points in object
            if operation.minz_from_ob:
                z = chunk.points[0][2]
            else:  # using operation minz
                z = operation.minz
            # only add a chunk layer if the chunk z point is in or lower than the layer
            if z <= layer[0]:
                if z <= layer[1]:
                    z = layer[1]
                # perform peck drill
                newchunk = chunk.copy()
                newchunk.setZ(z)
                chunklayers.append(newchunk)
                # retract tool to maxz (operation depth start in ui)
                newchunk = chunk.copy()
                newchunk.setZ(operation.maxz)
                chunklayers.append(newchunk)

    chunklayers = utils.sortChunks(chunklayers, operation)
    chunksToMesh(chunklayers, operation)
