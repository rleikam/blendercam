import bpy
from bpy.types import Panel
from ..operation import AddIntarsionOperations

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

        operationObjectColumn = layout.column(align=True)
        operationObjectColumn.label(text="Operation object")
        operationObjectColumn.prop_search(intarsionProperties, "operationObjectName", bpy.data, "objects", text="")
        operationObjectColumn.prop(intarsionProperties, "pocketDepth")

        carvingCutterColumn = layout.column(align=True)
        carvingCutterColumn.label(text="Carving cutter")
        carvingCutterColumn.prop(intarsionProperties, "carvingCutterType")

        match intarsionProperties.carvingCutterType:
            case ToolType.CONE.value:
                carvingCutterColumn.prop(intarsionProperties, "carvingCutterDiameter")
                carvingCutterColumn.prop(intarsionProperties, "angle")
            case ToolType.BALLCONE.value:
                carvingCutterColumn.prop(intarsionProperties, "carvingCutterDiameter")
                carvingCutterColumn.prop(intarsionProperties, "ballRadius")
                carvingCutterColumn.prop(intarsionProperties, "angle")
            case ToolType.BALLNOSE.value:
                carvingCutterColumn.prop(intarsionProperties, "ballRadius")

        clearingCutterColumn = layout.column(align=True)
        clearingCutterColumn.label(text="Clearing")
        clearingCutterColumn.prop(intarsionProperties, "clearingCutterDiameter")
        clearingCutterColumn.prop(intarsionProperties, "clearingCutterDistanceBetweenToolPaths")

        cutoutCutterColumn = layout.column(align=True)
        cutoutCutterColumn.label(text="Inlay Cutout")
        cutoutCutterColumn.prop(intarsionProperties, "clearingCutterDiameter")
        cutoutCutterColumn.prop(intarsionProperties, "inlayCutoutOffset")
        cutoutCutterColumn.prop(intarsionProperties, "inlayMaterialDepth")

        finishCutterColumn = layout.column(align=True)
        finishCutterColumn.label(text="Finish")
        finishCutterColumn.prop(intarsionProperties, "finishCutterDiameter")
        finishCutterColumn.prop(intarsionProperties, "finishCutterDistanceBetweenToolPaths")

        layout.operator(AddIntarsionOperations.bl_idname)