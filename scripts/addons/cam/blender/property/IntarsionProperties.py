from bpy.types import PropertyGroup
from bpy.props import FloatProperty, EnumProperty

from ...constants import *
from ...utils import *
from ...tool.ToolType import ToolType

class IntarsionProperties(PropertyGroup):

    # Cutter data
    carvingCutterType: EnumProperty(
        name = "Carving cutter type",
        description = "The cutter that is used for carving along the pocket and the inlay contours." \
            "Also used for clearing the corners of the inlay and the pocket",
        items = [
            (ToolType.CONE, ToolType.CONE.value, "Simple cone type (V-CARVE) cutter"),
            (ToolType.BALLCONE, ToolType.BALLCONE.value, "Cone type cutter with a ball end"),
            (ToolType.BALLNOSE, ToolType.BALLNOSE.value, "Ball end mill"),
        ]
    )

    carvingCutterDiameter: FloatProperty(
        name = "Carving cutter Diameter",
        description = "Diameter of the carving cutter",
        min = 0.000001,
        max = 10,
        default = 0.003175
    )

    ballRadius: FloatProperty(
        name = "Ball radius",
        description = "Radius of the ball cutter",
        min = 0.000001,
        max = 10,
        default = 0.00025
    )

    angle: FloatProperty(
        name = "Angle",
        description = "Angle of the carving cutter",
        subtype = "ANGLE",
        min=0.0,
        max=180.0,
        default=10.0
    )

    clearingCutterDiameter: FloatProperty(
        name = "Clearing cutter diameter",
        description = "The diameter of the cutter for clearing the pockets and the inlays",
        min = 0.000001,
        max = 10,
        default = 0.003175
    )

    clearingCutterDistanceBetweenToolPaths: FloatProperty(
        name = "Clearing cutter distance between toolpaths",
        description = "The distance between toolpaths for the clearing cutter",
        min = 0.000001,
        max = 10,
        default = 0.003175
    )

    cutoutCutterDiameter: FloatProperty(
        name = "Cutout cutter diameter",
        description = "The diameter of the cutter for cutting out the inlays along the silhouette of the inlay.",
        min = 0.000001,
        max = 10,
        default = 0.003175
    )

    finishCutterDiameter: FloatProperty(
        name = "Finish cutter diameter",
        description = "The diameter of the cutter for finishing and removing the excess base material of the inlay, that is sticking out of the base plate",
        min = 0.000001,
        max = 10,
        default = 0.006
    )

    finishCutterDistanceBetweenToolPaths: FloatProperty(
        name = "Finish cutter distance between toolpaths",
        description = "The distance between toolpaths for the finish cutter",
        min = 0.000001,
        max = 10,
        default = 0.003175
    )

    # Cutting data
    pocketDepth: FloatProperty(
        name = "Inlay Depth",
        description = "The maximum inlay and pocket depth for the intarsion",
        min = 0.000001,
        max = 10,
        default = 0.005
    )

    inlayCutoutOffset: FloatProperty(
        name = "Inlay silhouette offset",
        description = "The silhouette offset of the inlay for cutting it out with the cutout cutter",
        min = 0.000001,
        max = 10,
        default = 0.005
    )