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

from concurrent.futures import ThreadPoolExecutor

from shapely.geometry import polygon as spolygon
from shapely import geometry as sgeometry
from shapely import affinity

SHAPELY = True

# add pocket op for medial axis and profile cut inside to clean unremoved material
def Add_Pocket(sourceName, sourceType, depth, cutterDiameter):
    bpy.ops.object.select_all(action='DESELECT')
    scene = bpy.context.scene
    mpocket_exists = False

    #Delete old medial pockets
    for sourceObject in scene.objects:
        if sourceObject.name.startswith("medial_poc"):
            sourceObject.select_set(True)
            bpy.ops.object.delete()

    # Verify if medial pockets exist
    for op in scene.cam_operations:
        if op.name == "MedialPocket":
            mpocket_exists = True

    pocketObjectName = f"{sourceName}_MedialPocket"
    sourceObject = None
    if sourceType == "OBJECT":
        sourceObject = bpy.data.objects[sourceName]
        sourceObject.select_set(True)
        utils.silhoueteOffset(sourceObject, -cutterDiameter/2, 1, 0.3)
        bpy.context.active_object.name = pocketObjectName
    else:
        collection = utils.createCollectionIfNotExists(pocketObjectName)

        sourceObject = bpy.data.collections[sourceName]

        medialPockets = []
        for object in sourceObject.objects:
            bpy.ops.object.select_all(action='DESELECT')
            object.select_set(True)
            utils.silhoueteOffset(object, -cutterDiameter/2, 1, 0.3)
            bpy.context.active_object.name = f"{object.name}_MedialPocket"
            medialPockets.append(bpy.context.active_object)
        
        utils.reassignObjectsToCollection(medialPockets, collection)

    if not mpocket_exists:     # create a pocket operation if it does not exist already
        scene.cam_operations.add()
        operation = scene.cam_operations[-1]
        operation.geometry_source = sourceType
        if sourceType == "OBJECT":
            operation.object_name= pocketObjectName
        else:
            operation.collection_name = pocketObjectName
        scene.cam_active_operation = len(scene.cam_operations) - 1
        operation.name = pocketObjectName
        operation.filename = operation.name
        operation.strategy = 'POCKET'
        operation.use_layers = False
        operation.material.estimate_from_model = False
        operation.material.size[2] = -depth
        operation.minz_from_ob = False
        operation.minz_from_material = True


def getLayers(operation, startdepth, enddepth):
    """returns a list of layers bounded by startdepth and enddepth
       uses operation.stepdown to determine number of layers.
    """
    print("Set layers...")
    if operation.use_layers:
        layerCount = math.ceil((startdepth - enddepth) / operation.stepdown)
        print(F"Generate layers from {startdepth} to {enddepth} - Layercount: {layerCount}")

        layers = []
        layerstart = operation.maxz
        for x in range(0, layerCount):
            layerend = round(max(startdepth - ((x + 1) * operation.stepdown), enddepth), 6)
            if int(layerstart * 10 ** 8) != int(layerend * 10 ** 8):
                # it was possible that with precise same end of operation,
                # last layer was done 2x on exactly same level...
                layers.append([layerstart, layerend])
            layerstart = layerend
    else:
        layers = [[round(startdepth, 6), round(enddepth, 6)]]

    return layers

def chunksToMesh(chunks : camPathChunk, operation):
    """convert sampled chunks to path, optimization of paths"""
    expiredTime = time.time()
    scene = bpy.context.scene
    camMachine = scene.cam_machine
    vertices = []

    free_movement_height = operation.free_movement_height

    if operation.machine_axes == '3':
        if camMachine.use_position_definitions:
            position = camMachine.starting_position
            origin = (position.x, position.y, position.z)
        else:
            origin = (0, 0, free_movement_height)

        vertices = [origin]
    
    if operation.machine_axes != '3':
        verts_rotations = []
    
    if (operation.machine_axes == '5' and operation.strategy5axis == 'INDEXED') or (
            operation.machine_axes == '4' and operation.strategy4axis == 'INDEXED'):
        extendChunks5axis(chunks, operation)

    if operation.array:
        nchunks = []
        for x in range(0, operation.array_x_count):
            for y in range(0, operation.array_y_count):
                print(x, y)
                for chunk in chunks:
                    chunk = chunk.copy()
                    chunk.shift(x * operation.array_x_distance, y * operation.array_y_distance, 0)
                    nchunks.append(chunk)
        chunks = nchunks

    progress('building paths from chunks')
    e = 0.0001
    lifted = True

    for chunkIndex in range(0, len(chunks)):

        chunk = chunks[chunkIndex]
        if len(chunk.points) > 0:  # TODO: there is a case where parallel+layers+zigzag ramps send empty chunks here...
            if operation.optimisation.optimize:
                chunk = optimizeChunk(chunk, operation)

            # lift and drop

            if lifted:  # did the cutter lift before? if yes, put a new position above of the first point of next chunk.
                if operation.machine_axes == '3' or (operation.machine_axes == '5' and operation.strategy5axis == 'INDEXED') or (
                        operation.machine_axes == '4' and operation.strategy4axis == 'INDEXED'):
                    v = (chunk.points[0][0], chunk.points[0][1], free_movement_height)
                else:  # otherwise, continue with the next chunk without lifting/dropping
                    v = chunk.startpoints[0]  # startpoints=retract points
                    verts_rotations.append(chunk.rotations[0])
                vertices.append(v)

            # add whole chunk
            vertices.extend(chunk.points)

            # add rotations for n-axis
            if operation.machine_axes != '3':
                verts_rotations.extend(chunk.rotations)

            lift = True
            # check if lifting should happen
            if chunkIndex < len(chunks) - 1 and len(chunks[chunkIndex + 1].points) > 0:
                # TODO: remake this for n axis, and this check should be somewhere else...
                last = Vector(chunk.points[-1])
                first = Vector(chunks[chunkIndex + 1].points[0])
                vect = first - last
                if (operation.machine_axes == '3' and (operation.strategy == 'PARALLEL' or operation.strategy == 'CROSS')
                    and vect.z == 0 and vect.length < operation.dist_between_paths * 2.5) \
                        or (operation.machine_axes == '4' and vect.length < operation.dist_between_paths * 2.5):
                    # case of neighbouring paths
                    lift = False
                if abs(vect.x) < e and abs(vect.y) < e:  # case of stepdown by cutting.
                    lift = False

            if lift:
                if operation.machine_axes == '3' or (operation.machine_axes == '5' and operation.strategy5axis == 'INDEXED') or (
                        operation.machine_axes == '4' and operation.strategy4axis == 'INDEXED'):
                    v = (chunk.points[-1][0], chunk.points[-1][1], free_movement_height)
                else:
                    v = chunk.startpoints[-1]
                    verts_rotations.append(chunk.rotations[-1])
                vertices.append(v)
            lifted = lift

    if operation.optimisation.use_exact and not operation.optimisation.use_opencamlib:
        cleanupBulletCollision(operation)
    print(time.time() - expiredTime)
    expiredTime = time.time()

    # actual blender object generation starts here:
    edges = [(index, index+1) for index in range(0, len(vertices) - 1)]

    objectName = getCAMPathObjectNameConventionFrom(operation.name)

    mesh = bpy.data.meshes.new(objectName)
    mesh.name = objectName
    mesh.from_pydata(vertices, edges, [])

    if objectName in scene.objects:
        scene.objects[objectName].data = mesh
        object = scene.objects[objectName]
    else:
        object = object_utils.object_data_add(bpy.context, mesh, operator=None)

        collection = getCAMPathCollection()
        reassignObjectsToCollection([object], collection)

    if operation.machine_axes != '3':
        # store rotations into shape keys, only way to store large arrays with correct floating point precision
        # - object/mesh attributes can only store array up to 32000 intems.

        object.shape_key_add()
        object.shape_key_add()
        shapeKey = mesh.shape_keys.key_blocks[1]
        shapeKey.name = 'rotations'
        print(len(shapeKey.data))
        print(len(verts_rotations))

        for i, co in enumerate(verts_rotations):  # TODO: optimize this. this is just rewritten too many times...
            shapeKey.data[i].co = co

    print(time.time() - expiredTime)

    object.location = (0, 0, 0)
    operation.path_object_name = objectName

    # parent the path object to source object if object mode
    if (operation.geometry_source == 'OBJECT') and operation.parent_path_to_object:
        activate(operation.objects[0])
        object.select_set(state=True, view_layer=None)
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
    else:
        object.select_set(state=True, view_layer=None)


def checkminz(operation):
    if operation.minz_from_material:
        return operation.min.z
    else:
        return operation.minz

def printProgressionTitle(title):
    titleDashes = 3
    titleEmptySpacing = 1
    titleLength = len(title)
    amountDashLines = titleDashes*2 + titleEmptySpacing*2 + titleLength

    dashLines = "-" * amountDashLines
    titleDashes = "-" * titleDashes
    titleSpacing = " " * titleEmptySpacing
    title = titleDashes + titleSpacing + title + titleSpacing + titleDashes

    print(dashLines)
    print(title)
    print(dashLines)

class ToolType(Enum):
    VCARVE = "VCARVE",
    BALLNOSE = "BALLNOSE",
    BALLCONE = "BALLCONE"

class Tool:
    def __init__(self):
        pass

    def calculateMillDepthFor(self, diameter: float) -> float:
        """Calculates the mill depth for the given diameter based on the tip of the mill"""
        pass

    def calculateMillDiameterFor(self, depth: float) -> float:
        """Calculates the mill diameter for the given depth based on the tip of the mill"""
        pass
    
    def getMaximumToolLength(self) -> float:
        """Get the maximum tool depth"""
        pass

class ToolManager:
    """
    Helper class for generating the calculation objects based on supported mill types
    """
    @staticmethod
    def constructToolFromOperation(operation) -> Tool:
        """Constructs a matching mill from the given operation"""

        match(operation.cutter_type):
            case ToolType.VCARVE.name:
                return VCarveMill(operation.cutter_tip_angle, operation.cutter_diameter)
            case ToolType.BALLNOSE.name:
                return BallnoseMill(operation.cutter_diameter)
            case ToolType.BALLCONE.name:
                return BallconeMill(operation.cutter_tip_angle, operation.ball_radius*2, operation.cutter_diameter)
                

    @staticmethod
    def isToolSupported(toolTypeName : str) -> str:
        """Checks if the given tool type is supported"""
        return toolTypeName in [enum.name for enum in ToolType]
    
    @staticmethod
    def getSupportedTools() -> Iterator[str]:
        """Gets the list of supported tools"""
        return [enum.name for enum in ToolType]

class VCarveMill(Tool):
    def __init__(self, angle, diameter):
        self._slope = math.tan(radians(angle / 2))
        self._maximumToolDepth = (diameter/2)/self._slope

    def calculateMillDepthFor(self, diameter: float) -> float:
        return (diameter/2)/self._slope
    
    def calculateMillDiameterFor(self, depth: float) -> float:
        return (depth*self._slope)*2

    def getMaximumToolLength(self) -> float:
        return self._maximumToolDepth
    
class BallconeMill(Tool):
    def __init__(self, angle : float, ballDiameter : float, diameter : float):

        self._slope = math.tan(radians(angle / 2))

        self._ballRadius = ballDiameter/2

        self._depthBallTangentToBallCenter = self._ballRadius * sin(radians(angle/2))
        self._radiusBallTangent = self._ballRadius * cos(radians(angle/2))
        self._depthConeTipToBallTangent = self._radiusBallTangent/self._slope
        self._depthConeTipToBallCenter = self._depthConeTipToBallTangent + self._depthBallTangentToBallCenter
        self._depthConeTipToBallTip = self._depthConeTipToBallCenter - self._ballRadius
        self._depthBallTipToBallTangent = self._depthConeTipToBallCenter - self._depthConeTipToBallTip - self._depthBallTangentToBallCenter

        self._maximumToolDepth = (diameter/2)/self._slope - self._depthConeTipToBallTip

    def calculateMillDepthFor(self, diameter: float) -> float:
        calculatedDepth = 0.0
        millRadius = diameter/2
        if millRadius < self._radiusBallTangent:
            calculatedRadians = acos(millRadius/self._ballRadius)
            calculatedDepth = self._ballRadius - self._ballRadius*sin(calculatedRadians)
        else:
            calculatedDepth = (millRadius/self._slope) - self._depthConeTipToBallTip
        
        return calculatedDepth
    
    def calculateMillDiameterFor(self, depth: float) -> float:
        if depth < self._depthBallTipToBallTangent:
            depthInverse = self._ballRadius - depth
            calculatedRadians = asin(depthInverse/self._ballRadius)
            calculatedDepth = 2*self._ballRadius*cos(calculatedRadians)
        else:
            calculatedDepth = 2*((depth+self._depthConeTipToBallTip)*self._slope)

        return calculatedDepth

    def getMaximumToolLength(self) -> float:
        return self._maximumToolDepth

class BallnoseMill(Tool):
    def __init(self, diameter):
        self.maximumToolDepth = diameter/2

    def calculateMillDepthFor(self, diameter: float) -> float:
        pass
    
    def calculateMillDiameterFor(self, depth: float) -> float:
        pass

    def getMaximumToolLength(self) -> float:
        pass
