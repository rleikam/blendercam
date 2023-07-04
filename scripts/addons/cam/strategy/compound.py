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

def compound(operation):
    if operation.strategy == 'CARVE':
        pathSamples = []
        object = bpy.data.objects[operation.curve_object]
        pathSamples.extend(curveToChunks(object))
        pathSamples = utils.sortChunks(pathSamples, operation)  # sort before sampling
        pathSamples = chunksRefine(pathSamples, operation)
    elif operation.strategy == 'PENCIL':
        prepareArea(operation)
        utils.getAmbient(operation)
        pathSamples = getOffsetImageCavities(operation, operation.offset_image)
        pathSamples = limitChunks(pathSamples, operation)
        pathSamples = utils.sortChunks(pathSamples, operation)  # sort before sampling
    elif operation.strategy == 'CRAZY':
        prepareArea(operation)
        # pathSamples = crazyStrokeImage(o)
        # this kind of worked and should work:
        millarea = operation.zbuffer_image < operation.minz + 0.000001
        avoidarea = operation.offset_image > operation.minz + 0.000001

        pathSamples = crazyStrokeImageBinary(operation, millarea, avoidarea)
        #####
        pathSamples = utils.sortChunks(pathSamples, operation)
        pathSamples = chunksRefine(pathSamples, operation)

    else:
        print("PARALLEL")
        if operation.strategy == 'OUTLINEFILL':
            utils.getOperationSilhouete(operation)

        pathSamples = getPathPattern(operation)

        if operation.strategy == 'OUTLINEFILL':
            pathSamples = utils.sortChunks(pathSamples, operation)
            # have to be sorted once before, because of the parenting inside of samplechunks

        if operation.strategy in ['BLOCK', 'SPIRAL', 'CIRCLES']:
            pathSamples = utils.connectChunksLow(pathSamples, operation)

    # print (minz)

    chunks = []
    layers = strategy.getLayers(operation, operation.maxz, operation.min.z)

    print("SAMPLE", operation.name)
    chunks.extend(utils.sampleChunks(operation, pathSamples, layers))
    print("SAMPLE OK")
    if operation.strategy == 'PENCIL':  # and bpy.app.debug_value==-3:
        chunks = chunksCoherency(chunks)
        print('coherency check')

    if operation.strategy in ['PARALLEL', 'CROSS', 'PENCIL', 'OUTLINEFILL']:  # and not o.parallel_step_back:
        print('sorting')
        chunks = utils.sortChunks(chunks, operation)
        if operation.strategy == 'OUTLINEFILL':
            chunks = utils.connectChunksLow(chunks, operation)
    if operation.ramp:
        for ch in chunks:
            ch.rampZigZag(ch.zstart, ch.points[0][2], operation)
    # print(chunks)
    if operation.strategy == 'CARVE':
        for ch in chunks:
            for vi in range(0, len(ch.points)):
                ch.points[vi] = (ch.points[vi][0], ch.points[vi][1], ch.points[vi][2] - operation.carve_depth)
    if operation.use_bridges:
        print(chunks)
        for bridge_chunk in chunks:
            useBridges(bridge_chunk, operation)

    strategy.chunksToMesh(chunks, operation)