from cam import utils
from ...exception import CamException
from cam.ops import fixUnits
from bpy.types import Operator
import bpy

class CamOperationAdd(Operator):
    """Add new CAM operation"""
    bl_idname = "scene.cam_operation_add"
    bl_label = "Add new CAM operation"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        scene = context.scene
        fixUnits()

        object = bpy.context.active_object
        if object is None: raise CamException("No object selected")

        minx, miny, minz, maxx, maxy, maxz = utils.getBoundsWorldspace([object])
        scene.cam_operations.add()
        operation = scene.cam_operations[-1]
        operation.object_name = object.name
        operation.minz = minz

        scene.cam_active_operation = len(scene.cam_operations) - 1

        operation.name = f"Op_{object.name}_{scene.cam_active_operation + 1}"
        operation.filename = operation.name

        newOperationExpansion = scene.cam_operation_expansions.add()
        newOperationExpansion.operationName = operation.name

        if scene.objects.get('CAM_machine') is None:
            utils.addMachineAreaObject()

        return {'FINISHED'}