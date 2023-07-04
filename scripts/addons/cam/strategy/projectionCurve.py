import bpy
from bpy.props import *
from math import *
from bpy_extras import object_utils
from cam.chunk import *
from cam.collision import *
from cam.simple import *
from cam.pattern import *
from cam import utils
from cam.utils import *
from cam.polygon_utils_cam import *
from cam.image_utils import *

from cam.strategy.utility import *
def projectCurve(scene, operation):
    print('operation: projected curve')
    object = bpy.data.objects[operation.curve_object]

    pathSamples = []
    pathSamples.extend(curveToChunks(object))

    targetCurve = scene.objects[operation.curve_object1]

    if targetCurve.type != 'CURVE':
        operation.info.warnings += 'Projection target and source have to be curve objects!\n '
        return

    extend_up = 0.1
    extend_down = 0.04
    tsamples = curveToChunks(targetCurve)
    for chunkIndex, chunk in enumerate(pathSamples):
        chunkPoint = tsamples[chunkIndex].points
        chunk.depth = 0
        for i, scene in enumerate(chunk.points):
            # move the points a bit
            endPoint = Vector(chunkPoint[i])
            startPoint = Vector(chunk.points[i])
            # extend startpoint
            vector = startPoint - endPoint
            vector.normalize()
            vector *= extend_up
            startPoint += vector
            chunk.startpoints.append(startPoint)

            # extend endpoint
            vece = startPoint - endPoint
            vece.normalize()
            vece *= extend_down
            endPoint -= vece
            chunk.endpoints.append(endPoint)

            chunk.rotations.append((0, 0, 0))

            vec = startPoint - endPoint
            chunk.depth = min(chunk.depth, -vec.length)
            chunk.points[i] = startPoint.copy()

    layers = getLayers(operation, 0, chunk.depth)

    chunks = []
    chunks.extend(utils.sampleChunksNAxis(operation, pathSamples, layers))
    chunksToMesh(chunks, operation)
