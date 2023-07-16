from ...curvecamtools import *

from bpy.types import Panel

class CurveToolsPanel(Panel):
    bl_space_type = 'VIEW_3D'
    bl_idname = "CAM_PT_curve_tools"
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_label = "Curve CAM Tools"

    def draw(self, context):
        column = self.layout.column(align=True)
        column.operator(CamCurveBoolean.bl_idname)
        column.operator(CamCurveConvexHull.bl_idname)
        column.operator(CamCurveIntarsion.bl_idname)
        column.operator(CurveToolPathSilhouette.bl_idname)
        column.operator(CamCurveOvercuts.bl_idname)
        column.operator(CamCurveOvercutsB.bl_idname)
        column.operator(CamObjectSilhouete.bl_idname)
        column.operator(CamOffsetSilhouete.bl_idname)
        column.operator(CamCurveRemoveDoubles.bl_idname)
        column.operator(CamMeshGetPockets.bl_idname)
        column.operator(CamMapObjectToTarget.bl_idname)