from cam.strategy.utility import *
from cam.chunk import *
from cam import utils
from cam.pattern import *
from cam.polygon_utils_cam import *
from cam.opencamlib.opencamlib import *

def waterlineOCL(operation):
    utils.getAmbient(operation)
    chunks = []
    oclGetWaterline(operation, chunks)
    chunks = limitChunks(chunks, operation)
    if (operation.movement_type == 'CLIMB' and operation.spindle_rotation_direction == 'CW') or (
            operation.movement_type == 'CONVENTIONAL' and operation.spindle_rotation_direction == 'CCW'):
        for ch in chunks:
            ch.points.reverse()
    chunksToMesh(chunks, operation)