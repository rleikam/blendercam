from bpy.types import Operator
from bpy.props import IntProperty
from ...utils import positionObject
import bpy

class PositionOperationObject(Operator):

    bl_idname = "object.material_cam_position"
    bl_label = "Position object for CAM operation"
    bl_options = {'REGISTER', 'UNDO'}

    operationIndex: IntProperty()

    def execute(self, context):
        scene = context.scene
        operation = scene.cam_operations[self.operationIndex]
        if operation.object_name in bpy.data.objects:
            positionObject(operation)
        else:
            print('No object assigned')
        return {'FINISHED'}

    def draw(self, context):
        self.layout.prop_search(self, "operation", context.scene, "cam_operations")