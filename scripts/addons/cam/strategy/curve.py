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

def curve(operation):
    print('--- Operation: curve ---')
    pathSamples = []
    utils.getOperationSources(operation)
    if not operation.onlycurves:
        operation.info.warnings += 'at least one of assigned objects is not a curve\n'

    for ob in operation.objects:
        pathSamples.extend(curveToChunks(ob))  # make the chunks from curve here
    pathSamples = utils.sortChunks(pathSamples, operation)  # sort before sampling
    pathSamples = chunksRefine(pathSamples, operation)  # simplify

    # layers here
    if operation.use_layers:
        layers = getLayers(operation, operation.maxz, round(checkminz(operation), 6))
        # layers is a list of lists [[0.00,l1],[l1,l2],[l2,l3]] containg the start and end of each layer
        extendorder = []
        chunks = []
        for layer in layers:
            for ch in pathSamples:
                extendorder.append([ch.copy(), layer])  # include layer information to chunk list

        for chl in extendorder:  # Set offset Z for all chunks according to the layer information,
            chunk = chl[0]
            layer = chl[1]
            print('layer: ' + str(layer[1]))
            chunk.offsetZ(operation.maxz * 2 - operation.minz + layer[1])
            chunk.clampZ(operation.minz)  # safety to not cut lower than minz
            chunk.clampmaxZ(operation.free_movement_height)  # safety, not higher than free movement height

        for chl in extendorder:  # strip layer information from extendorder and transfer them to chunks
            chunks.append(chl[0])

        chunksToMesh(chunks, operation)  # finish by converting to mesh

    else:  # no layers, old curve
        for ch in pathSamples:
            ch.clampZ(operation.minz)  # safety to not cut lower than minz
            ch.clampmaxZ(operation.free_movement_height)  # safety, not higher than free movement height
        chunksToMesh(pathSamples, operation)
