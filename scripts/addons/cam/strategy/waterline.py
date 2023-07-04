import bpy
import time
import mathutils
import math
from math import *
from mathutils import *
from bpy.props import *

from cam.strategy import *

import numpy

import cam.strategy as test
from cam import chunk
from cam.chunk import *

from cam import collision
from cam.collision import *

from cam import simple
from cam.simple import *

from cam import bridges
from cam.bridges import *

from cam import utils
from cam import strategy

from cam import pattern
from cam.pattern import *

from cam import polygon_utils_cam
from cam.polygon_utils_cam import *

from cam import image_utils
from cam.image_utils import *
from cam.opencamlib.opencamlib import *
from cam.nc import iso

def waterline(operation):
    topdown = True
    tw = time.time()
    chunks = []
    progress('retrieving object slices')
    prepareArea(operation)
    layerstep = 1000000000
    if operation.use_layers:
        layerstep = math.floor(operation.stepdown / operation.slice_detail)
        if layerstep == 0:
            layerstep = 1

    # for projection of filled areas
    layerstart = operation.max.z  #
    layerend = operation.min.z  #
    layers = [[layerstart, layerend]]
    #######################
    nslices = ceil(abs(operation.minz / operation.slice_detail))
    lastslice = spolygon.Polygon()  # polyversion
    layerstepinc = 0

    slicesfilled = 0
    utils.getAmbient(operation)

    for h in range(0, nslices):
        layerstepinc += 1
        slicechunks = []
        z = operation.minz + h * operation.slice_detail
        if h == 0:
            z += 0.0000001
            # if people do mill flat areas, this helps to reach those...
            # otherwise first layer would actually be one slicelevel above min z.

        islice = operation.offset_image > z
        slicepolys = imageToShapely(operation, islice, with_border=True)

        poly = spolygon.Polygon()  # polygversion
        lastchunks = []

        for p in slicepolys.geoms:
            poly = poly.union(p)  # polygversion TODO: why is this added?
            nchunks = shapelyToChunks(p, z)
            nchunks = limitChunks(nchunks, operation, force=True)
            lastchunks.extend(nchunks)
            slicechunks.extend(nchunks)
        if len(slicepolys.geoms) > 0:
            slicesfilled += 1

        #
        if operation.waterline_fill:
            layerstart = min(operation.maxz, z + operation.slice_detail)  #
            layerend = max(operation.min.z, z - operation.slice_detail)  #
            layers = [[layerstart, layerend]]
            #####################################
            # fill top slice for normal and first for inverse, fill between polys
            if not lastslice.is_empty or (operation.inverse and not poly.is_empty and slicesfilled == 1):
                restpoly = None
                if not lastslice.is_empty:  # between polys
                    if operation.inverse:
                        restpoly = poly.difference(lastslice)
                    else:
                        restpoly = lastslice.difference(poly)
                # print('filling between')
                if (not operation.inverse and poly.is_empty and slicesfilled > 0) or (
                        operation.inverse and not poly.is_empty and slicesfilled == 1):  # first slice fill
                    restpoly = lastslice

                restpoly = restpoly.buffer(-operation.dist_between_paths, resolution=operation.optimisation.circle_detail)

                fillz = z
                i = 0
                while not restpoly.is_empty:
                    nchunks = shapelyToChunks(restpoly, fillz)
                    # project paths TODO: path projection during waterline is not working
                    if operation.waterline_project:
                        nchunks = chunksRefine(nchunks, operation)
                        nchunks = utils.sampleChunks(operation, nchunks, layers)

                    nchunks = limitChunks(nchunks, operation, force=True)
                    #########################
                    slicechunks.extend(nchunks)
                    parentChildDist(lastchunks, nchunks, operation)
                    lastchunks = nchunks
                    # slicechunks.extend(polyToChunks(restpoly,z))
                    restpoly = restpoly.buffer(-operation.dist_between_paths, resolution=operation.optimisation.circle_detail)

                    i += 1
            # print(i)
            i = 0
            #  fill layers and last slice, last slice with inverse is not working yet
            #  - inverse millings end now always on 0 so filling ambient does have no sense.
            if (slicesfilled > 0 and layerstepinc == layerstep) or (
                    not operation.inverse and not poly.is_empty and slicesfilled == 1) or (
                    operation.inverse and poly.is_empty and slicesfilled > 0):
                fillz = z
                layerstepinc = 0

                bound_rectangle = operation.ambient
                restpoly = bound_rectangle.difference(poly)
                if operation.inverse and poly.is_empty and slicesfilled > 0:
                    restpoly = bound_rectangle.difference(lastslice)

                restpoly = restpoly.buffer(-operation.dist_between_paths, resolution=operation.optimisation.circle_detail)

                i = 0
                while not restpoly.is_empty:  # 'GeometryCollection':#len(restpoly.boundary.coords)>0:
                    # print(i)
                    nchunks = shapelyToChunks(restpoly, fillz)
                    #########################
                    nchunks = limitChunks(nchunks, operation, force=True)
                    slicechunks.extend(nchunks)
                    parentChildDist(lastchunks, nchunks, operation)
                    lastchunks = nchunks
                    restpoly = restpoly.buffer(-operation.dist_between_paths, resolution=operation.optimisation.circle_detail)
                    i += 1

            percent = int(h / nslices * 100)
            progress('waterline layers ', percent)
            lastslice = poly

        if (operation.movement_type == 'CONVENTIONAL' and operation.spindle_rotation_direction == 'CCW') or (
                operation.movement_type == 'CLIMB' and operation.spindle_rotation_direction == 'CW'):
            for chunk in slicechunks:
                chunk.points.reverse()
        slicechunks = utils.sortChunks(slicechunks, operation)
        if topdown:
            slicechunks.reverse()
        # project chunks in between

        chunks.extend(slicechunks)
    if topdown:
        chunks.reverse()

    print(time.time() - tw)
    strategy.chunksToMesh(chunks, operation)