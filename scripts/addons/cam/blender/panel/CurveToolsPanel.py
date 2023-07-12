from ...curvecamtools import *

from bpy.types import Panel

class CurveToolsPanel(Panel):
    bl_space_type = 'VIEW_3D'
    bl_idname = "CAM_PT_curve_tools"
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_label = "Curve CAM Tools"

    def draw(self, context):
        layout = self.layout
        layout.operator(CamCurveBoolean.bl_idname)
        layout.operator(CamCurveConvexHull.bl_idname)
        layout.operator(CamCurveIntarsion.bl_idname)
        layout.operator(CurveToolPathSilhouette.bl_idname)
        layout.operator(CamCurveOvercuts.bl_idname)
        layout.operator(CamCurveOvercutsB.bl_idname)
        layout.operator(CamObjectSilhouete.bl_idname)
        layout.operator(CamOffsetSilhouete.bl_idname)
        layout.operator(CamCurveRemoveDoubles.bl_idname)
        layout.operator(CamMeshGetPockets.bl_idname)