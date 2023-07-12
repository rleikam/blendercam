from ...utils import getBoundsWorldspace, addMachineAreaObject, getCAMMachineObjectName
from cam.ops import fixUnits
from bpy.types import Operator
import bpy

class AddOperation(Operator):
    """Add new CAM operation"""
    bl_idname = "scene.cam_operation_add"
    bl_label = "Add new CAM operation"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene is not None or bpy.context.active_object is None

    def execute(self, context):
        scene = context.scene
        fixUnits()

        object = bpy.context.active_object

        minx, miny, minz, maxx, maxy, maxz = getBoundsWorldspace([object])
        operation = scene.cam_operations.add()
        operation.object_name = object.name
        operation.minz = minz

        scene.cam_active_operation = len(scene.cam_operations) - 1

        operation.name = f"CAMOperation_{object.name}"
        operation.filename = operation.name

        newOperationExpansion = scene.cam_operation_expansions.add()
        newOperationExpansion.operationName = operation.name

        machineName = getCAMMachineObjectName()        
        if scene.objects.get(machineName) is None:
            addMachineAreaObject()

        return {'FINISHED'}