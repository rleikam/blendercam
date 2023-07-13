import bpy
from bpy.types import Panel

from .ButtonsPanel import ButtonsPanel
from ..property.IntarsionProperties import IntarsionProperties
from ...tool.ToolType import ToolType

class IntarsionPanel(ButtonsPanel, Panel):
    bl_label = "Intarsion generator"
    bl_idname = "CAM_PT_intarsion"

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    def draw(self, context):

        intarsionProperties: IntarsionProperties = context.scene.intarsion

        layout = self.layout

        operationObjectBox = layout.box()
        operationObjectBox.label(text="Operation object")
        operationObjectBox.prop_search(intarsionProperties, "operationObjectName", bpy.data, "objects", text="")

        carvingCutterBox = layout.box()
        carvingCutterBox.label(text="Carving cutter")
        carvingCutterBox.prop(intarsionProperties, "carvingCutterType")

        match intarsionProperties.carvingCutterType:
            case ToolType.CONE.name:
                carvingCutterBox.prop(intarsionProperties, "carvingCutterDiameter")
                carvingCutterBox.prop(intarsionProperties, "angle")
            case ToolType.BALLCONE.name:
                carvingCutterBox.prop(intarsionProperties, "carvingCutterDiameter")
                carvingCutterBox.prop(intarsionProperties, "ballRadius")
                carvingCutterBox.prop(intarsionProperties, "angle")
            case ToolType.BALLNOSE.name:
                carvingCutterBox.prop(intarsionProperties, "ballRadius")

        clearingCutterBox = layout.box()
        clearingCutterBox.label(text="Clearing cutter")
        clearingCutterBox.prop(intarsionProperties, "clearingCutterDiameter")
        clearingCutterBox.prop(intarsionProperties, "clearingCutterDistanceBetweenToolPaths")

        cutoutCutterBox = layout.box()
        cutoutCutterBox.label(text="Cutout cutter")
        cutoutCutterBox.prop(intarsionProperties, "clearingCutterDiameter")

        finishCutterBox = layout.box()
        finishCutterBox.label(text="Finish cutter")
        finishCutterBox.prop(intarsionProperties, "finishCutterDiameter")
        finishCutterBox.prop(intarsionProperties, "finishCutterDistanceBetweenToolPaths")

        operationDataBox = layout.box()
        operationDataBox.label(text="Operation data")
        operationDataBox.prop(intarsionProperties, "pocketDepth")
        operationDataBox.prop(intarsionProperties, "inlayCutoutOffset")
