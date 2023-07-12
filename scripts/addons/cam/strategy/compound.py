import bpy
from math import *
from mathutils import *
from bpy.props import *

from cam.strategy import *

from cam.chunk import *
from cam.collision import *
from cam.simple import *
from cam.bridges import *
from cam.pattern import *
from cam.polygon_utils_cam import *
from cam.image_utils import *
from cam.opencamlib.opencamlib import *

from .utility import getLayers, chunksToMesh, sortChunks, getOperationSilhouete, connectChunksLow, getAmbient, chunksCoherency, sampleChunks, printProgressionTitle
from ..blender.property.OperationProperties import OperationProperties

def carving(operation: OperationProperties):
    printProgressionTitle("CARVE")

    object = bpy.data.objects[operation.curve_object]
    pathSamples = curveToChunks(object)
    pathSamples = sortChunks(pathSamples, operation)
    pathSamples = chunksRefine(pathSamples, operation)

    chunks = []
    layers = getLayers(operation, operation.maxz, operation.min.z)

    print("SAMPLE", operation.name)
    chunks = sampleChunks(operation, pathSamples, layers)
    print("SAMPLE OK")

    if operation.ramp:
        for chunk in chunks:
            chunk.rampZigZag(chunk.zstart, chunk.points[0][2], operation)

    for chunk in chunks:
        for index in range(0, len(chunk.points)):
            chunk.points[index] = (chunk.points[index][0], chunk.points[index][1], chunk.points[index][2] - operation.carve_depth)

    if operation.use_bridges:
        print(chunks)
        for bridgeChunk in chunks:
            useBridges(bridgeChunk, operation)

    chunksToMesh(chunks, operation)

def parallel(operation: OperationProperties):
    printProgressionTitle("PARALLEL")

    printProgressionTitle("CREATE PARALLEL PATTERN")
    pathSamples = getPathPatternParallel(operation, operation.parallel_angle)
    layers = getLayers(operation, operation.maxz, operation.min.z)

    printProgressionTitle("SAMPLING CHUNKS")
    chunks = sampleChunks(operation, pathSamples, layers)

    printProgressionTitle("SORTING CHUNKS")
    chunks = sortChunks(chunks, operation)

    printProgressionTitle("SET RAMP")
    if operation.ramp:
        for chunk in chunks:
            chunk.rampZigZag(chunk.zstart, chunk.points[0][2], operation)

    printProgressionTitle("SET BRIDGES")
    if operation.use_bridges:
        print(chunks)
        for bridgeChunk in chunks:
            useBridges(bridgeChunk, operation)

    printProgressionTitle("CONVERT CHUNKS TO MESH")
    chunksToMesh(chunks, operation)

def outlinefill(operation: OperationProperties):
    printProgressionTitle("OUTLINE")

    getOperationSilhouete(operation)
    pathSamples = getPathPattern(operation)
    pathSamples = sortChunks(pathSamples, operation)

    chunks = []
    layers = getLayers(operation, operation.maxz, operation.min.z)

    print("SAMPLE", operation.name)
    chunks.extend(sampleChunks(operation, pathSamples, layers))
    print("SAMPLE OK")

    print('sorting')
    chunks = sortChunks(chunks, operation)
    chunks = connectChunksLow(chunks, operation)

    if operation.ramp:
        for chunk in chunks:
            chunk.rampZigZag(chunk.zstart, chunk.points[0][2], operation)

    if operation.use_bridges:
        print(chunks)
        for bridgeChunk in chunks:
            useBridges(bridgeChunk, operation)

    chunksToMesh(chunks, operation)

def pencil(operation: OperationProperties):
    printProgressionTitle("PENCIL")

    prepareArea(operation)
    getAmbient(operation)
    pathSamples = getOffsetImageCavities(operation, operation.offset_image)
    pathSamples = limitChunks(pathSamples, operation)
    pathSamples = sortChunks(pathSamples, operation)

    layers = getLayers(operation, operation.maxz, operation.min.z)

    print("SAMPLE", operation.name)
    chunks = sampleChunks(operation, pathSamples, layers)

    print("SAMPLE OK")

    chunks = chunksCoherency(chunks)
    print('coherency check')

    print('sorting')
    chunks = sortChunks(chunks, operation)

    if operation.ramp:
        for chunk in chunks:
            chunk.rampZigZag(chunk.zstart, chunk.points[0][2], operation)

    if operation.use_bridges:
        print(chunks)
        for bridgeChunk in chunks:
            useBridges(bridgeChunk, operation)

    chunksToMesh(chunks, operation)

def block(operation):
    printProgressionTitle("BLOCK")

    printProgressionTitle("GET PATH PATTERN")
    pathSamples = getPathPattern(operation)

    printProgressionTitle("CONNECT CHUNKS LOW")
    pathSamples = connectChunksLow(pathSamples, operation)

    layers = getLayers(operation, operation.maxz, operation.min.z)

    printProgressionTitle("SAMPLE CHUNKS")
    chunks = sampleChunks(operation, pathSamples, layers)

    printProgressionTitle("SET RAMP")
    if operation.ramp:
        for chunk in chunks:
            chunk.rampZigZag(chunk.zstart, chunk.points[0][2], operation)

    printProgressionTitle("SET BRIDGES")
    if operation.use_bridges:
        print(chunks)
        for bridgeChunk in chunks:
            useBridges(bridgeChunk, operation)

    printProgressionTitle("CONVERT CHUNKS TO MESH")
    chunksToMesh(chunks, operation)

def spiral(operation: OperationProperties):
    pathSamples = getPathPattern(operation)
    pathSamples = connectChunksLow(pathSamples, operation)

    layers = getLayers(operation, operation.maxz, operation.min.z)

    print("SAMPLE", operation.name)
    chunks = sampleChunks(operation, pathSamples, layers)
    print("SAMPLE OK")

    if operation.ramp:
        for chunk in chunks:
            chunk.rampZigZag(chunk.zstart, chunk.points[0][2], operation)

    if operation.use_bridges:
        print(chunks)
        for bridgeChunk in chunks:
            useBridges(bridgeChunk, operation)

    chunksToMesh(chunks, operation)

def cross(operation: OperationProperties):
    pathSamples = getPathPattern(operation)

    layers = getLayers(operation, operation.maxz, operation.min.z)

    print("SAMPLE", operation.name)
    chunks = sampleChunks(operation, pathSamples, layers)
    print("SAMPLE OK")

    print('sorting')
    chunks = sortChunks(chunks, operation)

    if operation.ramp:
        for chunk in chunks:
            chunk.rampZigZag(chunk.zstart, chunk.points[0][2], operation)

    if operation.use_bridges:
        print(chunks)
        for bridgeChunk in chunks:
            useBridges(bridgeChunk, operation)

    chunksToMesh(chunks, operation)

def circles(operation: OperationProperties):
    pathSamples = getPathPattern(operation)
    pathSamples = connectChunksLow(pathSamples, operation)

    layers = getLayers(operation, operation.maxz, operation.min.z)

    print("SAMPLE", operation.name)
    chunks = sampleChunks(operation, pathSamples, layers)
    print("SAMPLE OK")

    if operation.ramp:
        for chunk in chunks:
            chunk.rampZigZag(chunk.zstart, chunk.points[0][2], operation)

    if operation.use_bridges:
        print(chunks)
        for bridgeChunk in chunks:
            useBridges(bridgeChunk, operation)

    chunksToMesh(chunks, operation)

def crazy(operation: OperationProperties):
    prepareArea(operation)

    millarea = operation.zbuffer_image < operation.minz + 0.000001
    avoidarea = operation.offset_image > operation.minz + 0.000001

    pathSamples = crazyStrokeImageBinary(operation, millarea, avoidarea)
    pathSamples = sortChunks(pathSamples, operation)
    pathSamples = chunksRefine(pathSamples, operation)

    layers = getLayers(operation, operation.maxz, operation.min.z)

    print("SAMPLE", operation.name)
    chunks = sampleChunks(operation, pathSamples, layers)
    print("SAMPLE OK")

    if operation.ramp:
        for chunk in chunks:
            chunk.rampZigZag(chunk.zstart, chunk.points[0][2], operation)

    if operation.use_bridges:
        print(chunks)
        for bridgeChunk in chunks:
            useBridges(bridgeChunk, operation)

    chunksToMesh(chunks, operation)