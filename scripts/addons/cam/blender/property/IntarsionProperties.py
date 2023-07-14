from bpy.types import PropertyGroup
from bpy.props import FloatProperty, EnumProperty, StringProperty

from ...constants import *
from ...utils import *
from ...tool.ToolType import ToolType
from math import radians

class IntarsionProperties(PropertyGroup):
    # Object data
    operationObjectName: StringProperty(
        name = "Operation object",
        description = "The object, the intarsion operation should be based from"
    )

    # Cutter data
    carvingCutterType: EnumProperty(
        name = "Carving cutter type",
        description = "The cutter that is used for carving along the pocket and the inlay contours. " \
            "Also used for clearing the corners of the inlay and the pocket",
        items = [
            (ToolType.CONE.value, ToolType.CONE.value, "Simple cone type (V-CARVE) cutter"),
            (ToolType.BALLCONE.value, ToolType.BALLCONE.value, "Cone type cutter with a ball end"),
            (ToolType.BALLNOSE.value, ToolType.BALLNOSE.value, "Ball end mill"),
        ]
    )

    carvingCutterDiameter: FloatProperty(
        name = "Carving cutter diameter",
        description = "Diameter of the carving cutter",
        min = 0.000001,
        max = 10,
        default = 0.003175,
        unit="LENGTH",
        precision=6
    )

    carvingCutterDistanceBetweenToolpaths: FloatProperty(
        name = "Distance between toolpaths",
        description = "Distance between toolpaths for corner clearing operations",
        min = 0.000001,
        max = 10,
        default = 0.00025,
        unit="LENGTH",
        precision=6
    )

    ballRadius: FloatProperty(
        name = "Ball radius",
        description = "Radius of the ball cutter",
        min = 0.000001,
        max = 10,
        default = 0.00025,
        unit="LENGTH",
        precision=6
    )

    angle: FloatProperty(
        name = "Angle",
        description = "Angle of the carving cutter",
        subtype = "ANGLE",
        min = 0.0,
        max = radians(180),
        default = radians(10.0),
        precision=6
    )

    clearingCutterDiameter: FloatProperty(
        name = "Clearing cutter diameter",
        description = "The diameter of the cutter for clearing the pockets and the inlays",
        min = 0.000001,
        max = 10,
        default = 0.003175,
        unit="LENGTH",
        precision=6
    )

    clearingCutterDistanceBetweenToolPaths: FloatProperty(
        name = "Clearing cutter distance between toolpaths",
        description = "The distance between toolpaths for the clearing cutter",
        min = 0.000001,
        max = 10,
        default = 0.003175,
        unit="LENGTH",
        precision=6
    )

    cutoutCutterDiameter: FloatProperty(
        name = "Cutout cutter diameter",
        description = "The diameter of the cutter for cutting out the inlays along the silhouette of the inlay.",
        min = 0.000001,
        max = 10,
        default = 0.003175,
        unit="LENGTH",
        precision=6
    )

    finishCutterDiameter: FloatProperty(
        name = "Finish cutter diameter",
        description = "The diameter of the cutter for finishing and removing the excess base material of the inlay, that is sticking out of the base plate",
        min = 0.000001,
        max = 10,
        default = 0.006,
        unit="LENGTH",
        precision=6
    )

    finishCutterDistanceBetweenToolPaths: FloatProperty(
        name = "Finish cutter distance between toolpaths",
        description = "The distance between toolpaths for the finish cutter",
        min = 0.000001,
        max = 10,
        default = 0.003175,
        unit="LENGTH",
        precision=6
    )

    # Cutting data
    pocketDepth: FloatProperty(
        name = "Inlay Depth",
        description = "The maximum inlay and pocket depth for the intarsion",
        min = 0.000001,
        max = 10,
        default = 0.005,
        unit="LENGTH",
        precision=6
    )

    inlayMaterialDepth: FloatProperty(
        name = "Inlay material depth",
        description = "The material depth for the inlay. Used for the cutout depth of the inlay.",
        min = 0.000001,
        max = 10,
        default = 0.01,
        unit="LENGTH",
        precision=6
    )

    inlayCutoutOffset: FloatProperty(
        name = "Inlay silhouette offset",
        description = "The silhouette offset of the inlay for cutting it out with the cutout cutter",
        min = 0.000001,
        max = 10,
        default = 0.005,
        unit="LENGTH",
        precision=6
    )