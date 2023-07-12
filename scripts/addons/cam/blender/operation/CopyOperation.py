from ...ops import fixUnits
from bpy.types import Operator
from bpy.props import IntProperty

class CopyOperation(Operator):
    """Copy CAM operation"""
    bl_idname = "scene.cam_operation_copy"
    bl_label = "Copy active CAM operation"
    bl_options = {'REGISTER', 'UNDO'}

    operationIndex: IntProperty()

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        scene = context.scene
        fixUnits()

        if len(scene.cam_operations) == 0: return {'CANCELLED'}
        operation = scene.cam_operations[self.operationIndex]

        copiedOperation = scene.cam_operations.add()
        for key in operation.keys():
            copiedOperation[key] = operation[key]
        copiedOperation.computing = False

        # Set the unique name of the new copied operation
        isdigit = True
        numdigits = 0

        if copiedOperation.name[-1].isdigit():
            numdigits = 1
            while isdigit:
                numdigits += 1
                isdigit = copiedOperation.name[-numdigits].isdigit()
            numdigits -= 1
            copiedOperation.name = copiedOperation.name[:-numdigits] + str(int(copiedOperation.name[-numdigits:]) + 1).zfill(numdigits)
            copiedOperation.filename = copiedOperation.name
        else:
            copiedOperation.name = copiedOperation.name + '_copy'
            copiedOperation.filename = copiedOperation.filename + '_copy'

        """
        Append the new operation after the operation, where it was copied from
        The move should be set afterwards, because there is an issue with the
        relocation of data in memory, when new objects are added to collection properties
        """
        scene.cam_active_operation = self.operationIndex + 1
        operationCount = len(scene.cam_operations) - 1
        scene.cam_operations.move(operationCount, self.operationIndex + 1)

        return {'FINISHED'}