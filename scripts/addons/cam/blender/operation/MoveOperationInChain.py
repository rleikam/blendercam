from bpy.types import Operator
from bpy.props import IntProperty, EnumProperty

class MoveOperationInChain(Operator):
    """Add operation to chain"""
    bl_idname = "scene.cam_chain_operation_up"
    bl_label = "Add operation to chain"
    bl_options = {'REGISTER', 'UNDO'}

    direction: EnumProperty(name='direction',
                            items=(('UP', 'Up', ''), ('DOWN', 'Down', '')),
                            description='direction', default='DOWN')

    chainIndex: IntProperty(name="ChainIndex")

    operationIndex: IntProperty(name="OperationIndex")

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        chains = context.scene.cam_chains[self.chainIndex]

        if self.direction == 'UP':
            if self.operationIndex > 0:
                chains.operations.move(self.operationIndex, self.operationIndex - 1)
        else:
            if self.operationIndex < len(chains.operations) - 1:
                chains.operations.move(self.operationIndex, self.operationIndex + 1)

        return {'FINISHED'}