from ...ops import fixUnits
from bpy.types import Operator
import bpy

class CamOperationCopy(Operator):
    """Copy CAM operation"""
    bl_idname = "scene.cam_operation_copy"
    bl_label = "Copy active CAM operation"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        # main(context)
        scene = bpy.context.scene

        fixUnits()

        scene = bpy.context.scene
        if len(scene.cam_operations) == 0: return {'CANCELLED'}
        copyop = scene.cam_operations[scene.cam_active_operation]
        scene.cam_operations.add()
        scene.cam_active_operation += 1
        l = len(scene.cam_operations) - 1
        scene.cam_operations.move(l, scene.cam_active_operation)
        o = scene.cam_operations[scene.cam_active_operation]

        for k in copyop.keys():
            o[k] = copyop[k]
        o.computing = False

        # ###get digits in the end

        isdigit = True
        numdigits = 0
        num = 0
        if o.name[-1].isdigit():
            numdigits = 1
            while isdigit:
                numdigits += 1
                isdigit = o.name[-numdigits].isdigit()
            numdigits -= 1
            o.name = o.name[:-numdigits] + str(int(o.name[-numdigits:]) + 1).zfill(numdigits)
            o.filename = o.name
        else:
            o.name = o.name + '_copy'
            o.filename = o.filename + '_copy'

        return {'FINISHED'}